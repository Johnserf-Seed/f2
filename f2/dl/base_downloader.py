# path: f2/dl/base_downloader.py

import sys
import httpx
import asyncio
import aiofiles
import traceback

from pathlib import Path
from rich.progress import TaskID
from typing import Union, Optional, Any, List, Set

from f2.log.logger import logger, trace_logger
from f2.i18n.translator import _
from f2.cli.cli_console import RichConsoleManager
from f2.crawlers.base_crawler import BaseCrawler
from f2.utils._signal import SignalManager
from f2.utils.utils import ensure_path
from f2.utils._dl import (
    get_content_length,
    trim_filename,
    get_chunk_size,
    get_segments_from_m3u8,
)
from f2.exceptions.api_exceptions import APIRetryExhaustedError

# 最大片段缓存数量，超过这个数量就会进行清理
# (Maximum segment cache count, clear when it exceeds this count)
MAX_SEGMENT_COUNT = 1000


class BaseDownloader(BaseCrawler):
    """
    基础下载器 (Base Downloader)

    该类继承自 BaseCrawler 类，提供了一个基础下载器，负责处理文件的下载任务，支持下载单个文件、静态文件以及流式视频下载。

    它支持断点续传、进度跟踪和错误处理，适用于多种文件下载场景。

    类属性:
    - headers (dict): 自定义 HTTP 请求头，包括 Cookie 信息。
    - progress (RichConsoleManager.progress): 下载进度管理器，用于显示下载进度。
    - download_tasks (list): 存储所有下载任务的列表。

    类方法:
    - _ensure_path: 确保目标路径存在，如果不存在则创建。
    - _download_chunks: 处理文件的分块下载，支持边下载边更新进度。
    - download_file: 下载文件，如果文件已经部分下载，则支持断点续传。
    - save_file: 保存静态文件到指定路径。
    - download_m3u8_stream: 下载 m3u8 流视频，支持多个片段的下载与合并。
    - initiate_download: 初始化文件下载任务，根据文件是否存在跳过或开始下载。
    - initiate_static_download: 初始化静态文件下载任务。
    - initiate_m3u8_download: 初始化 m3u8 流视频下载任务。
    - execute_tasks: 执行所有下载任务。
    - close: 关闭下载器，释放资源。
    - __aenter__: 异步上下文管理器的进入方法，初始化下载器。
    - __aexit__: 异步上下文管理器的退出方法，关闭下载器。

    异常处理:
    - 该类在下载过程中会处理多种异常，包括文件下载错误、网络超时、文件覆盖等问题，保证下载任务的稳定性。

    使用示例:
    ```python
        # 创建 BaseDownloader 实例并使用异步方式开始文件下载任务
        async with BaseDownloader(headers={'Cookie': 'value'}, proxies={'all': 'proxy_url'}) as downloader:
            await downloader.initiate_download(
                file_type='视频',
                file_url='https://example.com/file.mp4',
                base_path='/path/to/save',
                file_name='file',
                file_suffix='.mp4'
            )
            await downloader.execute_tasks()
    ```
    """

    def __init__(self, kwargs: dict = ...):
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        self.headers = kwargs.get("headers", {}) | {"Cookie": kwargs["cookie"]}
        super().__init__(kwargs, proxies=proxies, crawler_headers=self.headers)

        self.progress = RichConsoleManager().progress
        self.download_tasks = []

    @staticmethod
    def _ensure_path(path: Union[str, Path]) -> Path:
        return ensure_path(path)

    async def _download_chunks(
        self,
        request: httpx.Request,
        file: Any,
        content_length: int,
        task_id: TaskID,
    ) -> None:
        """
        为给定的任务ID下载块 (Download chunks for a given task ID)

        Args:
            request (httpx.Request): HTTP请求对象 (HTTP request object)
            file: 文件对象 (File object)
            content_length (int): 内容长度 (Content length)
            task_id (TaskID): 任务ID (Task ID)
        """

        try:
            response = await self.aclient.send(request, stream=True)
            async for chunk in response.aiter_bytes(get_chunk_size(content_length)):
                if SignalManager.is_shutdown_signaled():
                    break
                await file.write(chunk)
                await self.progress.update(
                    task_id, advance=len(chunk), total=int(content_length)
                )
        except httpx.TimeoutException as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("文件区块超时：{0}").format(e))
        except httpx.NetworkError as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("文件区块网络错误：{0}").format(e))
        except httpx.HTTPStatusError as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("文件区块HTTP错误：{0}").format(e))
        except httpx.ProxyError as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("文件区块代理错误：{0}").format(e))
        except httpx.UnsupportedProtocol as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("文件区块协议错误：{0}").format(e))
        except httpx.StreamError as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("文件区块流错误：{0}").format(e))
        except httpx.RemoteProtocolError as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("文件区块不符合HTTP协议：{0}").format(e))
        except Exception as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("文件区块下载失败：{0} Exception：{1}").format(request, e))

    async def download_file(
        self,
        task_id: TaskID,
        urls: Union[str, List[str]],
        full_path: Union[str, Path],
    ) -> None:
        """
        下载文件 (Download file)

        Args:
            task_id (TaskID): 任务ID (Task ID)
            urls (Union[str, List[str]]): 文件URL (File URL)
            full_path (Union[str, Path]): 保存路径 (Save path)

        Note:
            url仅代表一个文件的链接，当url为列表时，表示该文件的多个链接
            (url represents only a link to a file, when url is a list,
                it represents multiple links to the file)
        """
        async with self.semaphore:
            # 如果urls是单个链接，则转换为列表以便统一处理
            if isinstance(urls, str):
                urls = [urls]

            # 确保目标路径存在 (Ensure target path exists)
            full_path = self._ensure_path(full_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = full_path.with_suffix(".tmp")

            # 遍历所有链接 (Iterate over all links)
            for link in urls:
                try:
                    # 获取文件内容大小 (Get the size of the file content)
                    content_length = await get_content_length(
                        link, self.headers, self.proxies
                    )
                    logger.debug(
                        _("{0} 在服务器上的总内容长度为：{1} 字节").format(
                            link, content_length
                        )
                    )

                    # 如果文件内容大小为0, 则尝试下一个链接 (If the file content size is 0, try the next link)
                    if content_length == 0:
                        logger.warning(
                            _("链接 {0} 响应大小为 0 字节，尝试下一个链接").format(link)
                        )
                        continue

                    start_byte = 0 if not tmp_path.exists() else tmp_path.stat().st_size
                    logger.debug(
                        _("找到了未下载完的文件 {0}, 大小为 {1} 字节").format(
                            tmp_path, start_byte
                        )
                    )

                    if start_byte == content_length:
                        tmp_path.rename(full_path)
                        logger.info(_("文件已完整下载，无需重复下载"))
                        return

                    # 构建range请求头 (Build range request header)
                    range_headers = (
                        {"Range": f"bytes={start_byte}-"} if start_byte else {}
                    )
                    range_headers.update(self.headers)

                    range_request = self.aclient.build_request(
                        "GET", link, headers=range_headers
                    )

                    retry_attempts = 3  # 最大重试次数
                    for attempt in range(retry_attempts):
                        try:
                            async with aiofiles.open(
                                tmp_path, "ab" if start_byte else "wb"
                            ) as file:
                                await self._download_chunks(
                                    range_request, file, content_length, task_id
                                )
                            break  # 成功下载，跳出重试循环

                        except httpx.RemoteProtocolError as e:
                            logger.warning(
                                _("协议错误，重试 {0}/{1}：{2}").format(
                                    attempt + 1, retry_attempts, e
                                )
                            )
                            if attempt == retry_attempts - 1:
                                # 重试次数用尽，抛出异常 (Retry attempts exhausted, raise exception)
                                raise APIRetryExhaustedError(_("重试次数已用尽"))

                    # 检查文件大小是否匹配 (Check if the file size matches)
                    actual_size = tmp_path.stat().st_size
                    if actual_size != content_length:
                        logger.warning(
                            _("文件大小不匹配 - 预期: {0} 字节, 实际: {1} 字节").format(
                                content_length, actual_size
                            )
                        )
                        await self.progress.update(
                            task_id,
                            description=_("[yellow][  警告  ]：[/yellow]"),
                            filename=trim_filename(full_path.name, 45),
                            state="warning",
                        )
                        continue  # 保留.tmp后缀，尝试下一个链接

                    # 尝试重命名文件
                    try:
                        tmp_path.rename(full_path)
                    except (FileExistsError, PermissionError) as e:
                        logger.error(_("文件重命名失败：{0}").format(e))
                        tmp_path.replace(full_path)
                    except Exception as e:
                        trace_logger.error(traceback.format_exc())
                        logger.error(_("意外错误：{0}").format(e))
                        tmp_path.unlink(missing_ok=True)
                        await self.progress.update(
                            task_id,
                            description=_("[red][  失败  ]：[/red]"),
                            filename=trim_filename(full_path.name, 45),
                            state="error",
                        )
                        continue

                    logger.info(
                        _("[green][  完成  ]：{0}[/green]").format(Path(full_path).name)
                    )
                    await self.progress.update(
                        task_id,
                        description=_("[green][  完成  ]：[/green]"),
                        filename=trim_filename(full_path.name, 45),
                        state="completed",
                        visible=False,
                    )
                    break  # 下载成功，跳出链接循环

                except Exception as e:
                    logger.error(_("下载失败：{0}").format(e))
                    continue

            else:
                # 如果遍历完所有链接仍然无法成功下载，则记录警告
                logger.warning(_("所有链接都无法下载"))
                logger.error(
                    _("[red][  丢失  ]：[/red]无法下载文件，路径：{0}").format(
                        Path(full_path).name
                    )
                )
                await self.progress.update(
                    task_id,
                    description=_("[red][  丢失  ]：[/red]"),
                    filename=trim_filename(full_path.name, 45),
                    state="error",
                    visible=False,
                )

    async def save_file(
        self,
        task_id: TaskID,
        content: Any,
        full_path: Union[str, Path],
    ):
        """
        保存文件 (Save file)

        Args:
            task_id (TaskID): 任务ID (Task ID)
            content (Any): 文件内容 (File content)
            full_path (Union[str, Path]): 保存路径 (Save path)
        """
        # 确保目标路径存在 (Ensure target path exists)
        full_path = self._ensure_path(full_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 确定打开文件的模式 (Determine the mode in which the file is opened)
        mode = "wb" if isinstance(content, bytes) else "w"

        # 准备 aiofiles.open 的参数 (Prepare parameters for aiofiles.open)
        open_params = {"file": full_path, "mode": mode}
        if mode == "w":  # 文本模式时添加 encoding 参数
            open_params["encoding"] = "utf-8"

        # 更新进度条 (Update progress bar)
        await self.progress.update(
            task_id, advance=1024, total=int(sys.getsizeof(content))
        )
        # 创建异步文件对象并写入内容 (Create an async file object and write content)
        async with aiofiles.open(**open_params) as f:
            await f.write(content)

        logger.info(_("[green][  完成  ]：{0}[/green]").format(Path(full_path).name))
        await self.progress.update(
            task_id,
            description=_("[green][  完成  ]：[/green]"),
            filename=trim_filename(full_path.name, 45),
            state="completed",
            visible=False,
        )
        logger.debug(_("文件已保存到：{0}").format(full_path))

    async def download_m3u8_stream(
        self,
        task_id: TaskID,
        url: str,
        full_path: Union[str, Path],
    ) -> None:
        """
        下载m3u8流视频 (Download m3u8 stream video)

        Args:
            task_id (TaskID): 任务ID (Task ID)
            url (str): m3u8文件的URL (m3u8 file URL)
            full_path (Union[str, Path]): 保存路径 (Save path)

        Note:
            由于直播流的特殊性，可能会出现直播结束、账号在别处进入直播间等情况，导致直播流无法下载。

            直播流的大小不确定，因此无法准确计算下载进度，只能根据下载的块大小来更新进度条。

            可能会出现 httpx.RemoteProtocolError 错误，这是由于服务器返回的块大小未严格遵守 HTTP 规范。
            非代码问题，而是服务器问题，跳过该片段处理。
            Issues: https://github.com/encode/httpx/issues/1927
        """
        async with self.semaphore:
            full_path = self._ensure_path(full_path)
            # 设置默认下载总量 (Set default total download)
            total_downloaded = 10240000
            # 默认块大小 (Default chunk size)
            default_chunks = 409600
            # 记录已经下载的片段序号
            # (Record the segment number that has been downloaded)
            downloaded_segments: Set = set()

            while not SignalManager.is_shutdown_signaled():
                try:
                    segments = await get_segments_from_m3u8(url)

                    if not segments:
                        logger.debug(_("m3u8片段为空，直播流已结束"))
                        logger.info(
                            _("[green][  完成  ]：{0}[/green]").format(
                                Path(full_path).name
                            )
                        )
                        await self.progress.update(
                            task_id,
                            description=_("[green][  完成  ]：[/green]"),
                            filename=trim_filename(full_path.name, 45),
                            state="completed",
                            visible=False,
                        )
                        return

                    # 确保目标路径存在 (Ensure target path exists)
                    full_path.parent.mkdir(parents=True, exist_ok=True)

                    async with aiofiles.open(full_path, "ab") as file:
                        for segment in segments:
                            if SignalManager.is_shutdown_signaled():
                                break

                            # 检查是否已经下载过该片段 (Check if the segment has been downloaded)
                            if segment.absolute_uri not in downloaded_segments:
                                ts_url = segment.absolute_uri
                                ts_content_length = await get_content_length(
                                    ts_url,
                                    self.headers,
                                    self.proxies,
                                )
                                if ts_content_length == 0:
                                    ts_content_length = default_chunks
                                    logger.debug(
                                        _(
                                            "无法读取该TS文件字节长度，将使用默认400kb块大小处理数据"
                                        )
                                    )

                                try:
                                    ts_request = self.aclient.build_request(
                                        "GET", ts_url, headers=self.headers
                                    )
                                    ts_response = await self.aclient.send(
                                        ts_request, stream=True
                                    )

                                    async for chunk in ts_response.aiter_bytes(
                                        get_chunk_size(ts_content_length)
                                    ):
                                        if SignalManager.is_shutdown_signaled():
                                            break

                                        # 直播流分块下载，每次下载后更新进度条
                                        # (Live stream block download, update progress bar after each download)
                                        await file.write(chunk)
                                        total_downloaded += len(chunk)
                                        await self.progress.update(
                                            task_id,
                                            advance=len(chunk),
                                            total=total_downloaded,
                                        )

                                    # 记录已经下载的片段序号
                                    # (Record the segment number that has been downloaded)
                                    downloaded_segments.add(segment.absolute_uri)

                                except httpx.ReadTimeout:
                                    logger.warning(_("下载超时：跳过该 TS 文件片段"))
                                    continue

                                except httpx.RemoteProtocolError as e:
                                    logger.error(
                                        _(
                                            "服务器返回的块大小未严格遵守 HTTP 规范，跳过该片段。错误信息：{0}"
                                        ).format(e)
                                    )
                                    continue

                                finally:
                                    await ts_response.aclose()
                            else:
                                logger.debug(
                                    _("跳过已下载的片段，URL：{0}").format(
                                        segment.absolute_uri
                                    )
                                )

                            # 每下载一定数量的片段后，清理一次集合
                            # (After downloading a certain number of segments, clean up the collection)
                            if len(downloaded_segments) > MAX_SEGMENT_COUNT:
                                downloaded_segments = set()

                    # 等待片段时长，避免过快下载
                    # (Wait for the segment duration to avoid downloading too fast)
                    await asyncio.sleep(segment.duration)

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        logger.debug(_("m3u8文件或ts文件未找到，当前直播已结束"))
                    elif e.response.status_code == 504:
                        logger.warning(_("[red]网关超时，无法下载直播流[/red]"))
                    else:
                        logger.debug(_("HTTP错误：{0}").format(e))
                        logger.error(_("[red]m3u8文件下载失败，但文件已保存[/red]"))

                    logger.info(
                        _("[green][  完成  ]：{0}[/green]").format(Path(full_path).name)
                    )
                    await self.progress.update(
                        task_id,
                        description=_("[red][  完成  ]：[/red]"),
                        filename=trim_filename(full_path.name, 45),
                        state="completed",
                        visible=False,
                    )
                    logger.debug(_("直播流文件已保存到：{0}").format(full_path))
                    return

                except Exception as e:
                    trace_logger.error(traceback.format_exc())
                    logger.error(_("m3u8文件解析失败：{0}").format(e))
                    await self.progress.update(
                        task_id,
                        description=_("[red][  失败  ]：[/red]"),
                        filename=trim_filename(full_path.name, 45),
                        state="completed",
                    )
                    return

    async def initiate_download(
        self,
        file_type: str,
        file_url: Union[str, List[str]],
        base_path: Union[str, Path],
        file_name: str,
        file_suffix: Optional[str],
    ) -> None:
        """
        初始化下载任务。如果文件已经存在，则跳过下载。否则，创建一个新的异步下载任务。
        (Initiate a download task. If file already exists,
        skip the download. Otherwise, create a new async download task)

        Args:
            file_type (str): 文件类型描述 (File type description)
            file_url (Union[str, List[str]]): 文件URL (File URL)
            file_name (str): 文件名称 (File name)
            base_path (Union[str, Path]): 基础路径 (Base path)
            file_suffix (Optional[str]): 文件后缀 (File suffix)

        Note:
            file_url仅代表一个文件的链接，当file_url为列表时，表示该文件的多个链接
            (file_url represents only a link to a file, when file_url is a list,
                it represents multiple links to the file)
        """

        # 文件路径
        file_path = f"{file_name}{file_suffix}"
        # 文件全路径
        full_path = self._ensure_path(base_path) / file_path

        if full_path.exists():
            logger.info(_("[cyan][  跳过  ]: {0}[/cyan]").format(Path(full_path).name))
            task_id = await self.progress.add_task(
                description=_("[cyan][  跳过  ]:[/cyan]"),
                filename=trim_filename(file_path, 45),
                start=True,
                total=1,
                completed=1,
            )
            await self.progress.update(task_id, state="completed", visible=False)
        else:
            task_id = await self.progress.add_task(
                description=_("[  {0}  ]:").format(file_type),
                filename=trim_filename(file_path, 45),
                start=True,
            )
            await self.progress.update(task_id, state="starting")
            download_task = asyncio.create_task(
                self.download_file(task_id, file_url, full_path)
            )
            self.download_tasks.append(download_task)

    async def initiate_static_download(
        self,
        file_type: str,
        content: Any,
        base_path: Union[str, Path],
        file_name: str,
        file_suffix: Optional[str],
    ) -> None:
        """
        初始化静态下载任务。如果文件已经存在，则跳过下载。否则，创建一个新的异步下载任务。
        (Initiate a download task. If file already exists, skip the download.
        Otherwise, create a new async download task)

        Args:
            file_type (str): 文件类型描述 (File type description)
            file_url (str): 文件URL (File URL)
            file_name (str): 文件名称 (File name)
            base_path (Union[str, Path]): 基础路径 (Base path)
            file_suffix (Optional[str]): 文件后缀 (File suffix)
        """

        # 文件路径
        file_path = f"{file_name}{file_suffix}"
        # 文件全路径
        full_path = self._ensure_path(base_path) / file_path

        if full_path.exists():
            logger.info(_("[cyan][  跳过  ]: {0}[/cyan]").format(Path(full_path).name))
            task_id = await self.progress.add_task(
                description=_("[cyan][  跳过  ]:[/cyan]"),
                filename=trim_filename(file_path, 45),
                start=True,
                total=1,
                completed=1,
            )
            await self.progress.update(task_id, state="completed", visible=False)
        else:
            task_id = await self.progress.add_task(
                description=_("[  {0}  ]:").format(file_type),
                filename=trim_filename(file_path, 45),
                start=True,
            )
            await self.progress.update(task_id, state="starting")
            download_task = asyncio.create_task(
                self.save_file(task_id, content, full_path)
            )
            self.download_tasks.append(download_task)

    async def initiate_m3u8_download(
        self,
        file_type: str,
        m3u8_url: str,
        base_path: Union[str, Path],
        file_name: str,
        file_suffix: Optional[str],
    ) -> None:
        """
        初始化m3u8流视频下载任务。如果文件已经存在，则跳过下载。否则，创建一个新的异步下载任务。
        (Initiate a m3u8 stream video download task. If file already exists,
        skip the download. Otherwise, create a new async download task)

        Args:
            file_type (str): 文件类型描述 (File type description)
            m3u8_url (str): m3u8文件的URL (m3u8 file URL)
            file_name (str): 文件名称 (File name)
            base_path (Union[str, Path]): 基础路径 (Base path)
            file_suffix (Optional[str]): 文件后缀 (File suffix)
        """
        # 文件路径
        file_path = f"{file_name}{file_suffix}"
        # 文件全路径
        full_path = self._ensure_path(base_path) / file_path

        if full_path.exists():
            logger.info(_("[cyan][  跳过  ]: {0}[/cyan]").format(Path(full_path).name))
            task_id = await self.progress.add_task(
                description=_("[cyan][  跳过  ]:[/cyan]"),
                filename=trim_filename(file_path, 45),
                start=True,
                total=1,
                completed=1,
            )
            await self.progress.update(task_id, state="completed", visible=False)
        else:
            task_id = await self.progress.add_task(
                description=_("[  {0}  ]:").format(file_type),
                filename=trim_filename(file_path, 45),
                start=True,
            )
            await self.progress.update(task_id, state="starting")
            download_task = asyncio.create_task(
                self.download_m3u8_stream(task_id, m3u8_url, full_path)
            )
            self.download_tasks.append(download_task)

    async def execute_tasks(self):
        """执行所有下载任务 (Execute all download tasks)"""
        logger.debug(
            _("开始执行下载任务，本次共有 {0} 个任务").format(len(self.download_tasks))
        )
        await asyncio.gather(*self.download_tasks)
        self.download_tasks.clear()

    async def close(self) -> None:
        """关闭下载器 (Close the downloader)"""
        if self.client:
            self.client.close()
        if self.aclient:
            await self.aclient.aclose()

    async def __aenter__(self) -> "BaseDownloader":
        """进入上下文管理器 (Enter the context manager)"""
        self.progress.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文管理器 (Exit the context manager)"""
        self.progress.__exit__(exc_type, exc_val, exc_tb)
        await self.close()

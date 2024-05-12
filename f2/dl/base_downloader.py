# path: f2/dl/base_downloader.py

import sys
import httpx
import asyncio
import aiofiles
import traceback
from pathlib import Path
from rich.progress import TaskID
from typing import Union, Optional, Any, List

from f2.log.logger import logger
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

# 最大片段缓存数量，超过这个数量就会进行清理
# (Maximum segment cache count, clear when it exceeds this count)
MAX_SEGMENT_COUNT = 1000


class BaseDownloader(BaseCrawler):
    """基础下载器 (Base Downloader Class)"""

    def __init__(self, kwargs: dict = ...):
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        self.headers = kwargs.get("headers") | {"Cookie": kwargs["cookie"]}
        super().__init__(proxies=proxies, crawler_headers=self.headers)

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
        except httpx.ReadTimeout as e:
            logger.warning(_("文件区块下载超时：{0}").format(e))
        except Exception as e:
            logger.error(_("文件区块下载失败：{0}").format(e))

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

            # 遍历所有链接 (Iterate over all links)
            for link in urls:
                # 获取文件内容大小 (Get the size of the file content)
                content_length = await get_content_length(
                    link, self.headers, self.proxies
                )

                logger.debug(
                    _("{0} 在服务器上的总内容长度为：{1} 字节").format(
                        link, content_length
                    )
                )

                # 如果文件内容大小为0, 则尝试下一个链接 (If file content size is 0, try the next link)
                if content_length == 0:
                    logger.warning(
                        _("链接 {0} 内容长度为0，尝试下一个链接是否可用").format(link)
                    )
                    continue

                # 确保目标路径存在 (Ensure target path exists)
                full_path.parent.mkdir(parents=True, exist_ok=True)
                # 寻找未下载完的临时文件 (Find unfinished temporary files)
                tmp_path = full_path.with_suffix(".tmp")
                # 获取临时文件的大小 (Get the size of the temporary file)
                start_byte = 0 if not tmp_path.exists() else tmp_path.stat().st_size

                logger.debug(
                    _("找到了未下载完的文件 {0}, 大小为 {1} 字节").format(
                        tmp_path, start_byte
                    )
                )

                if start_byte in [0, content_length]:
                    if start_byte:
                        tmp_path.rename(full_path)
                        logger.debug(_("临时文件已完全下载"))
                        return

                # 构建range请求头 (Build range request header)
                range_headers = (
                    {"Range": "bytes={}-".format(start_byte)} if start_byte else {}
                )
                range_headers.update(self.headers)
                range_request = self.aclient.build_request(
                    "GET", link, headers=range_headers
                )
                async with aiofiles.open(
                    tmp_path, "ab" if start_byte else "wb"
                ) as file:
                    await self._download_chunks(
                        range_request, file, content_length, task_id
                    )

                # 下载完成后重命名文件 (Rename file after download is complete)
                try:
                    tmp_path.rename(full_path)
                except FileExistsError:
                    logger.warning(_("{0} 已存在，将覆盖").format(full_path))
                    tmp_path.replace(full_path)
                except PermissionError:
                    logger.error(
                        _(
                            "另一个程序正在使用此文件或受异步调度影响，该任务需要重新下载"
                        )
                    )
                    # 尝试删除临时文件 (Try to delete the temporary file)
                    try:
                        tmp_path.unlink()
                        tmp_path.rename(full_path)
                    except Exception as e:
                        logger.error(_("尝试删除临时文件失败：{0}").format(e))

                    await self.progress.update(
                        task_id,
                        description=_("[  失败  ]："),
                        filename=trim_filename(full_path.name, 45),
                        state="error",
                    )

                await self.progress.update(
                    task_id,
                    description=_("[  完成  ]:"),
                    filename=trim_filename(full_path.name, 45),
                    state="completed",
                )
                logger.debug(_("下载完成, 文件已保存为 {0}").format(full_path))

                # 如果下载成功，则跳出循环 (If download is successful, break the loop)
                break

            else:
                # 如果遍历完所有链接仍然无法成功下载，则记录警告
                logger.warning("所有链接都无法下载")
                await self.progress.update(
                    task_id,
                    description=_("[  丢失  ]："),
                    filename=trim_filename(full_path.name, 45),
                    state="error",
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
        await self.progress.update(
            task_id, advance=1024, total=int(sys.getsizeof(content))
        )
        # 创建异步文件对象 (Create an asynchronous file object)
        async with aiofiles.open(file=full_path, mode=mode, encoding="utf-8") as f:
            await f.write(content)

        await self.progress.update(
            task_id,
            description=_("[  完成  ]:"),
            filename=trim_filename(full_path.name, 45),
            state="completed",
        )
        logger.debug(_("下载完成, 文件已保存为 {0}").format(full_path))

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
        """
        async with self.semaphore:
            full_path = self._ensure_path(full_path)
            # 设置默认下载总量 (Set default total download)
            total_downloaded = 10240000
            # 默认块大小 (Default chunk size)
            default_chunks = 409600
            # 记录已经下载的片段序号
            # (Record the segment number that has been downloaded)
            downloaded_segments = set()

            while not SignalManager.is_shutdown_signaled():
                try:
                    segments = await get_segments_from_m3u8(url)

                    if not segments:
                        await self.progress.update(
                            task_id,
                            description=_("[  丢失  ]:"),
                            filename=trim_filename(full_path.name, 45),
                            state="completed",
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
                                    ts_url, self.headers, self.proxies
                                )
                                if ts_content_length == 0:
                                    ts_content_length = default_chunks
                                    logger.warning(
                                        _(
                                            "无法读取该TS文件字节长度，将使用默认400kb块大小处理数据"
                                        )
                                    )
                                ts_request = self.aclient.build_request(
                                    "GET", ts_url, headers=self.headers
                                )
                                ts_response = await self.aclient.send(
                                    ts_request, stream=True
                                )

                                try:
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

                                except httpx.ReadTimeout as e:
                                    logger.warning(_("TS文件下载超时: {0}").format(e))
                                except Exception as e:
                                    logger.error(_("TS文件下载失败: {0}").format(e))
                                    logger.error(traceback.format_exc())
                                finally:
                                    await ts_response.aclose()
                            else:
                                logger.debug(
                                    _("为你跳过已下载的片段，URI: {0}").format(
                                        segment.absolute_uri
                                    )
                                )

                            # 每下载一定数量的片段后，清理一次集合
                            # (After downloading a certain number of segments, clean up the collection)
                            if len(downloaded_segments) > MAX_SEGMENT_COUNT:
                                downloaded_segments = set()

                    # 等待一段时间后再次请求更新 (Request update again after waiting for a while)
                    await asyncio.sleep(segment.duration)

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        logger.warning(_("m3u8文件或ts文件未找到，可能直播结束"))
                        await self.progress.update(
                            task_id,
                            description=_("[  丢失  ]:"),
                            filename=trim_filename(full_path.name, 45),
                            state="completed",
                        )
                        return
                    else:
                        logger.error(_("HTTP错误: {0}").format(e))
                        await self.progress.update(
                            task_id,
                            description=_("[  失败  ]:"),
                            filename=trim_filename(full_path.name, 45),
                            state="completed",
                        )
                        return

                except Exception as e:
                    logger.error(_("m3u8文件解析失败: {0}").format(e))
                    logger.error(traceback.format_exc())
                    await self.progress.update(
                        task_id,
                        description=_("[  失败  ]:"),
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
            task_id = await self.progress.add_task(
                description=_("[  跳过  ]:"),
                filename=trim_filename(file_path, 45),
                start=True,
                total=1,
                completed=1,
            )
            await self.progress.update(task_id, state="completed")
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
            task_id = await self.progress.add_task(
                description=_("[  跳过  ]:"),
                filename=trim_filename(file_path, 45),
                start=True,
                total=1,
                completed=1,
            )
            await self.progress.update(task_id, state="completed")
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
            task_id = await self.progress.add_task(
                description=_("[  跳过  ]:"),
                filename=trim_filename(file_path, 45),
                start=True,
                total=1,
                completed=1,
            )
            await self.progress.update(task_id, state="completed")
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
        await self.aclient.aclose()

    async def __aenter__(self) -> "BaseDownloader":
        """进入上下文管理器 (Enter the context manager)"""
        self.progress.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文管理器 (Exit the context manager)"""
        self.progress.__exit__(exc_type, exc_val, exc_tb)
        await self.aclient.aclose()

# path: f2/dl/base_downloader.py

import asyncio
import hashlib
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles  # type: ignore
import httpx
from rich.progress import TaskID

from f2.cli.cli_console import RichConsoleManager
from f2.crawlers.base_crawler import BaseCrawler
from f2.dl.m3u8 import M3U8DownloadMixin
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.core.signal import SignalManager
from f2.utils.file.path import ensure_path
from f2.utils.http.utils import (
    get_chunk_size,
    get_content_length,
    trim_filename,
)


class BaseDownloader(M3U8DownloadMixin, BaseCrawler):
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

    def __init__(self, kwargs: Optional[dict] = None):
        kwargs = kwargs or {}
        proxies: Dict[str, Optional[str]] = kwargs.get(
            "proxies", {"http://": None, "https://": None}
        )
        self.headers = kwargs.get("headers", {}) | {"Cookie": kwargs.get("cookie", "")}
        super().__init__(kwargs, proxies=proxies, crawler_headers=self.headers)

        self.progress = RichConsoleManager().progress
        self.download_tasks: List[asyncio.Task] = []

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
            content_length: (int): 内容长度 (Content length)
            task_id (TaskID): 任务ID (Task ID)
        """

        try:
            response = await self.aclient.send(
                request, stream=True, follow_redirects=True
            )
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

    @staticmethod
    def _parse_content_range_start(response: httpx.Response) -> Optional[int]:
        """
        解析 Content-Range 头中的起始字节 (Parse the start byte of the Content-Range header)

        Args:
            response (httpx.Response): 响应对象，Content-Range 形如 "bytes 1000-9999/10000"

        Returns:
            Optional[int]: 起始字节，头缺失或无法解析时返回 None
        """
        match = re.match(r"bytes\s+(\d+)-", response.headers.get("Content-Range", ""))
        return int(match.group(1)) if match else None

    @staticmethod
    async def _rewind_file(file: Any, size: int) -> None:
        """
        把文件截断到 size 字节并把写入位置移到末尾 (Truncate the file to size bytes)

        用于丢弃本次调用中已写入但需要重新下载的数据。
        """
        await file.flush()
        await file.truncate(size)
        await file.seek(size)

    async def _download_chunks_optimized(
        self,
        request: httpx.Request,
        file: Any,
        content_length: int,
        task_id: TaskID,
        start_byte: int = 0,
    ) -> bool:
        """
        优化的分块下载方法，支持断点续传、重试与错误处理

        重试时从"已写入文件的位置"继续请求，不会重复写入已下载的字节；
        当服务器忽略 Range 返回 200 时，会丢弃文件中已有内容后从头写入。

        Args:
            request (httpx.Request): HTTP请求对象
            file: 文件对象
            content_length (int): 内容长度
            task_id (TaskID): 任务ID
            start_byte (int): 开始下载的字节位置（文件中已有的字节数），默认为0

        Returns:
            bool: 下载是否成功
        """
        retry_count = 0
        max_retries = 3

        # base：调用前文件中已有的字节数（续传起点）
        # written：本次调用已写入文件的字节数，跨重试保留，重试时从 base + written 继续
        base = start_byte
        written = 0

        while retry_count < max_retries:
            try:
                # 使用更优化的超时配置
                timeout = httpx.Timeout(connect=15.0, read=60.0, write=30.0, pool=30.0)

                # 每次（重）发请求都从文件当前末尾继续
                offset = base + written
                current_headers = {
                    k: v for k, v in request.headers.items() if k.lower() != "range"
                }
                if offset > 0:
                    current_headers["Range"] = f"bytes={offset}-"

                # 使用更简单的方式发送请求，让httpx处理重定向
                async with self.aclient.stream(
                    request.method,
                    str(request.url),
                    headers=current_headers,
                    timeout=timeout,
                    follow_redirects=True,  # 让httpx自动处理重定向
                ) as response:
                    status_code = response.status_code

                    if status_code == 200 and offset > 0:
                        # 服务器忽略了 Range 并返回整个文件：丢弃已有内容，从头写入
                        logger.warning(
                            _(
                                "服务器不支持断点续传，丢弃已下载的 {0} 字节后重新下载"
                            ).format(offset)
                        )
                        await self._rewind_file(file, 0)
                        base, written, offset = 0, 0, 0
                    elif status_code == 206:
                        range_start = self._parse_content_range_start(response)
                        if range_start is not None and range_start != offset:
                            logger.warning(
                                _(
                                    "服务器返回的续传起点 {0} 与请求的 {1} 不一致，重试 {2}/{3}"
                                ).format(
                                    range_start, offset, retry_count + 1, max_retries
                                )
                            )
                            retry_count += 1
                            await asyncio.sleep(2**retry_count)  # 指数退避
                            continue
                    elif status_code != 200:
                        logger.warning(
                            _("下载响应状态码异常: {0}，重试 {1}/{2}").format(
                                status_code, retry_count + 1, max_retries
                            )
                        )
                        retry_count += 1
                        await asyncio.sleep(2**retry_count)  # 指数退避
                        continue

                    # 使用缓冲区批量写入，提高异步性能
                    buffer = bytearray()
                    # 动态缓冲区大小：根据文件大小调整缓冲区
                    # 小文件(< 10MB): 256KB, 中文件(10MB-100MB): 1MB, 大文件(> 100MB): 4MB
                    if content_length < 10 * 1024 * 1024:  # < 10MB
                        buffer_size = 256 * 1024  # 256KB
                    elif content_length < 100 * 1024 * 1024:  # < 100MB
                        buffer_size = 1024 * 1024  # 1MB
                    else:  # >= 100MB
                        buffer_size = 4 * 1024 * 1024  # 4MB

                    chunk_size = get_chunk_size(content_length)
                    # 确保chunk_size不超过buffer_size的1/4，避免频繁刷新
                    chunk_size = min(chunk_size, buffer_size // 4)

                    # 调试信息：记录缓冲区配置
                    logger.debug(
                        _(
                            "文件大小: {0:.2f}MB, 缓冲区大小: {1}KB, 块大小: {2}KB"
                        ).format(
                            content_length / (1024 * 1024),
                            buffer_size // 1024,
                            chunk_size // 1024,
                        )
                    )

                    async for chunk in response.aiter_bytes(chunk_size):
                        if SignalManager.is_shutdown_signaled():
                            # 信号中断时，重置进度状态
                            await self.progress.update(
                                task_id,
                                description=_("[yellow][  中断  ]：[/yellow]"),
                                state="error",
                            )
                            return False

                        buffer.extend(chunk)

                        # 智能缓冲区写入策略
                        # 1. 当缓冲区满时写入
                        # 2. 定期写入避免内存占用过高
                        # 3. 批量更新进度条减少UI刷新频率
                        if len(buffer) >= buffer_size:
                            await file.write(buffer)
                            written += len(buffer)
                            # 对于大文件，减少flush频率以提高性能
                            if content_length > 50 * 1024 * 1024:  # > 50MB时减少flush
                                if written % (buffer_size * 4) == 0:  # 每16MB flush一次
                                    await file.flush()
                            else:
                                await file.flush()  # 小文件每次都flush确保数据安全

                            # 异步更新进度 - 使用 completed 而非 advance 来确保进度准确
                            await self.progress.update(
                                task_id,
                                completed=base + written,
                                total=content_length,
                            )
                            buffer.clear()

                    # 写入剩余缓冲区数据
                    if buffer:
                        await file.write(buffer)
                        written += len(buffer)
                        await file.flush()  # 最后确保所有数据都写入磁盘
                        await self.progress.update(
                            task_id,
                            completed=base + written,
                            total=content_length,
                        )

                    return True

            except (httpx.TimeoutException, httpx.PoolTimeout) as e:
                retry_count += 1
                wait_time = min(2**retry_count, 30)  # 最大等待30秒
                logger.warning(
                    _("下载超时，{0} 秒后从 {1} 字节继续重试 ({2}/{3}): {4}").format(
                        wait_time, base + written, retry_count, max_retries, str(e)
                    )
                )
                # 进度回退到已写入文件的位置
                await self.progress.update(
                    task_id,
                    completed=base + written,
                    total=content_length,
                )
                if retry_count < max_retries:
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    trace_logger.error(_("下载超时重试次数已达上限"))
                    await self.progress.update(
                        task_id, description=_("[red][  超时  ]：[/red]"), state="error"
                    )
                    return False

            except httpx.HTTPStatusError as e:
                # 对于HTTP错误，不重试，直接失败
                trace_logger.error(traceback.format_exc())
                await self.progress.update(
                    task_id, description=_("[red][  错误  ]：[/red]"), state="error"
                )
                return False

            except Exception as e:
                retry_count += 1
                logger.warning(
                    _("下载异常，从 {0} 字节继续重试 ({1}/{2}): {3}").format(
                        base + written, retry_count, max_retries, str(e)
                    )
                )
                # 进度回退到已写入文件的位置
                await self.progress.update(
                    task_id,
                    completed=base + written,
                    total=content_length,
                )
                if retry_count < max_retries:
                    await asyncio.sleep(2**retry_count)
                    continue
                else:
                    trace_logger.error(traceback.format_exc())
                    await self.progress.update(
                        task_id, description=_("[red][  失败  ]：[/red]"), state="error"
                    )
                    return False

        return False

    async def _validate_file_integrity(
        self, file_path: Path, expected_size: int, url: str
    ) -> bool:
        """
        验证文件完整性

        Args:
            file_path: 文件路径
            expected_size: 期望的文件大小
            url: 原始URL，用于获取ETag等信息

        Returns:
            bool: 文件是否完整
        """
        if not file_path.exists():
            return False

        actual_size = file_path.stat().st_size
        if actual_size != expected_size:
            logger.debug(
                _("文件大小不匹配 - 期望: {0}, 实际: {1}").format(
                    expected_size, actual_size
                )
            )
            return False

        # 添加ETag验证
        try:
            # 获取服务器的ETag用于验证
            response = await self.aclient.head(url, headers=self.headers)
            etag = response.headers.get("ETag")
            # 💩中💩 微博返回的ETag格式为 "1-b863f929ea62855a2eaa9fc4f8502be6"，需要处理
            if etag and '"1-' in etag:
                # 去除引号
                etag = etag.strip('"')
                # 去除前缀1-
                etag = etag.split("-")[1] if "-" in etag else etag
                # 添加引号
                etag = f'"{etag}"' if not etag.startswith('"') else etag

            if etag:
                # 计算本地文件的哈希值与ETag比较 ETag	"203394d4707fb4f999ce023359ec00ea"
                hash_md5 = hashlib.md5()
                async with aiofiles.open(file_path, "rb") as f:
                    while True:
                        chunk = await f.read(8192)
                        if not chunk:
                            break
                        hash_md5.update(chunk)
                local_etag = f'"{hash_md5.hexdigest()}"'
                # 比较ETag
                if local_etag != etag:
                    logger.debug(
                        _("文件ETag不匹配 - 期望: {0}, 实际: {1}").format(
                            etag, local_etag
                        )
                    )
                    return False
                logger.debug(
                    _("文件ETag匹配 - 期望: {0}, 实际: {1}").format(etag, local_etag)
                )
                return True
            else:
                logger.debug(_("未找到ETag头，无法进行ETag验证"))
        except Exception:
            # ETag验证失败不影响主流程
            logger.debug(_("获取ETag失败，可能是服务器不支持HEAD请求或ETag头缺失"))
            trace_logger.error(traceback.format_exc())
            return False

        return True

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
            urls = [urls] if isinstance(urls, str) else urls

            # 确保目标路径存在
            full_path = self._ensure_path(full_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = full_path.with_suffix(".tmp")

            # 遍历所有链接
            for link_index, link in enumerate(urls):
                try:
                    # 获取文件内容大小
                    content_length = await get_content_length(
                        link, self.headers, self.proxies, verify=self._verify
                    )

                    if content_length == 0:
                        logger.warning(
                            _("链接 {0} 响应大小为 0 字节，尝试下一个链接").format(link)
                        )
                        # 更新进度状态为错误
                        await self.progress.update(
                            task_id,
                            description=_("[yellow][  空文件  ]：[/yellow]"),
                        )
                        continue

                    # 检查现有文件
                    if full_path.exists():
                        if await self._validate_file_integrity(
                            full_path, content_length, link
                        ):
                            logger.info(
                                _("文件已存在且完整，跳过下载: {0}").format(
                                    full_path.name
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
                        else:
                            # 文件不完整，删除重新下载
                            full_path.unlink(missing_ok=True)

                    # 检查临时文件
                    start_byte = 0
                    if tmp_path.exists():
                        start_byte = tmp_path.stat().st_size
                        # 检查临时文件是否已经完整
                        if start_byte >= content_length:
                            if start_byte == content_length:
                                # 临时文件已完整，直接重命名
                                tmp_path.rename(full_path)
                                # 从临时文件恢复完整文件"))
                                logger.info(
                                    _(
                                        "[green][  恢复  ]：从临时文件恢复完整文件[/green]"
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
                            else:
                                # 临时文件异常，删除重新下载
                                tmp_path.unlink(missing_ok=True)
                                start_byte = 0

                    # 构建下载请求
                    range_headers = self.headers.copy()
                    if start_byte > 0:
                        range_headers["Range"] = f"bytes={start_byte}-"
                        logger.info(
                            _("继续下载，从 {0} 字节开始 (已下载 {1:.1f}%)").format(
                                start_byte, (start_byte / content_length) * 100
                            )
                        )
                        # 重要：设置进度条的初始进度状态，确保不会被后续的advance覆盖
                        await self.progress.update(
                            task_id,
                            completed=start_byte,
                            total=content_length,
                        )
                    else:
                        # 新下载，初始化进度条
                        await self.progress.update(
                            task_id,
                            completed=0,
                            total=content_length,
                        )

                    request = self.aclient.build_request(
                        "GET", link, headers=range_headers
                    )

                    # 执行下载
                    try:
                        async with aiofiles.open(
                            tmp_path, "ab" if start_byte else "wb"
                        ) as file:
                            success = await self._download_chunks_optimized(
                                request, file, content_length, task_id, start_byte
                            )

                        if not success:
                            logger.error(_("下载失败，尝试下一个链接"))
                            # 清理失败的临时文件
                            tmp_path.unlink(missing_ok=True)
                            # 重置进度条到开始状态
                            await self.progress.update(
                                task_id,
                                completed=0,
                                total=content_length,
                                description=_("[yellow][  重试  ]：[/yellow]"),
                            )
                            continue

                        # 验证下载完整性
                        if await self._validate_file_integrity(
                            tmp_path, content_length, link
                        ):
                            # 原子性重命名
                            try:
                                tmp_path.rename(full_path)
                            except (FileExistsError, PermissionError):
                                tmp_path.replace(full_path)

                            logger.info(
                                _("[green][  完成  ]：{0}[/green]").format(
                                    full_path.name
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
                        else:
                            logger.warning(_("文件完整性验证失败，尝试下一个链接"))
                            # 清理验证失败的文件
                            tmp_path.unlink(missing_ok=True)
                            # 重置进度条状态
                            await self.progress.update(
                                task_id,
                                completed=0,
                                total=content_length,
                                description=_("[yellow][  重试  ]：[/yellow]"),
                            )
                            continue

                    except Exception as e:
                        logger.error(_("下载过程异常: {0}").format(str(e)))
                        # 清理异常产生的临时文件
                        tmp_path.unlink(missing_ok=True)
                        # 重置进度条状态
                        await self.progress.update(
                            task_id,
                            completed=0,
                            total=content_length,
                            description=_("[red][  异常  ]：[/red]"),
                        )
                        continue

                except Exception as e:
                    logger.error(_("处理链接失败: {0} - {1}").format(link, str(e)))
                    # 重置进度条状态
                    await self.progress.update(
                        task_id,
                        completed=0,
                        description=_("[red][  错误  ]：[/red]"),
                    )
                    continue

            # 所有链接都失败
            logger.warning(_("所有链接都无法下载"))
            # 清理可能残留的临时文件
            tmp_path.unlink(missing_ok=True)
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
        open_params: Dict[str, Any] = {"file": full_path, "mode": mode}
        if mode == "w":  # 文本模式时添加 encoding 参数
            open_params["encoding"] = "utf-8"

        # 更新进度条 (Update progress bar)
        await self.progress.update(
            task_id, advance=1024, total=int(sys.getsizeof(content))
        )
        # 创建异步文件对象并写入内容 (Create an async file object and write content)
        async with aiofiles.open(**open_params) as f:  # type: ignore
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
        stream_status_callback: Any = None,
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
            stream_status_callback: 直播状态检查回调函数（可选）
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
                self.download_m3u8_stream(
                    task_id, m3u8_url, full_path, stream_status_callback
                )
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

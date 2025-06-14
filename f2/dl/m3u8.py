# path: f2/dl/m3u8.py

import asyncio
import traceback
from pathlib import Path
from typing import Any, Set, Union

import aiofiles  # type: ignore
import httpx
from rich.progress import TaskID

from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.core.signal import SignalManager
from f2.utils.http.utils import (
    get_chunk_size,
    get_content_length,
    get_segments_from_m3u8,
    trim_filename,
)

MAX_SEGMENT_COUNT = 1000


class M3U8DownloadMixin:
    """Mixin providing m3u8 stream download helpers."""

    semaphore: asyncio.Semaphore
    headers: dict
    proxies: dict
    aclient: httpx.AsyncClient
    progress: Any

    def _ensure_path(self, path: Union[str, Path]) -> Path: ...
    async def download_m3u8_stream(
        self,
        task_id: TaskID,
        url: str,
        full_path: Union[str, Path],
    ) -> None:
        """下载m3u8流视频"""
        async with self.semaphore:
            full_path = self._ensure_path(full_path)
            total_downloaded = 10240000
            default_chunks = 409600
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

                    full_path.parent.mkdir(parents=True, exist_ok=True)

                    async with aiofiles.open(full_path, "ab") as file:
                        for segment in segments:
                            if SignalManager.is_shutdown_signaled():
                                break

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

                                        await file.write(chunk)
                                        total_downloaded += len(chunk)
                                        await self.progress.update(
                                            task_id,
                                            advance=len(chunk),
                                            total=total_downloaded,
                                        )

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

                            if len(downloaded_segments) > MAX_SEGMENT_COUNT:
                                downloaded_segments = set()

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

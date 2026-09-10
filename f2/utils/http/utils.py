# path: f2/utils/http/utils.py

import asyncio
import traceback
from pathlib import Path
from typing import List, Optional, Union
from urllib.error import HTTPError

import httpx
import m3u8
from m3u8.model import Segment

from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.file.path import ensure_path


async def get_content_length(
    url: str,
    headers: Optional[dict] = None,
    proxies: Optional[dict] = None,
    max_retries: int = 3,
    verify: Union[bool, str] = True,
) -> int:
    """
    获取给定URL的Content-Length，使用HEAD请求重试，失败后退避到GET请求

    Args:
        url (str): 目标URL
        headers (Optional[dict], optional): 自定义请求头
        proxies (Optional[dict], optional): 代理配置
        max_retries (int, optional): 最大重试次数，默认为3
        verify (Union[bool, str], optional): TLS 证书校验，True / False / CA 证书路径，默认为 True

    Returns:
        int: 文件的Content-Length，单位为字节
    """

    if proxies is None:
        proxies = {"all://": None}

    proxy_url = (
        proxies.get("http://") or proxies.get("https://") or proxies.get("all://")
    )

    timeout_config = httpx.Timeout(
        connect=10.0,  # 连接超时
        read=30.0,  # 读取超时
        write=10.0,  # 写入超时
        pool=10.0,  # 连接池超时
    )

    # 优化请求头
    optimized_headers = {
        "Accept": "*/*",
        "Accept-Encoding": "identity;q=1, *;q=0",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
    }

    if headers:
        optimized_headers.update(headers)

    async with httpx.AsyncClient(
        timeout=timeout_config,
        transport=httpx.AsyncHTTPTransport(
            retries=2,
            proxy=proxy_url,
        ),
        verify=verify,
        follow_redirects=True,
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
    ) as aclient:

        # 策略1：HEAD请求重试
        for attempt in range(max_retries):
            try:
                response = await aclient.head(url)
                response.raise_for_status()

                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > 0:
                    logger.debug(
                        _("HEAD请求成功获取Content-Length: {0}").format(content_length)
                    )
                    return int(content_length)

                # HEAD请求成功但没有Content-Length，直接退避到GET请求
                logger.debug(_("HEAD请求成功但无Content-Length头，退避到GET请求"))
                break

            except (
                httpx.TimeoutException,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
            ):
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 递增等待时间
                    logger.warning(
                        _("HEAD请求超时，{0} 秒后重试 ({1}/{2})：{3}").format(
                            wait_time, attempt + 1, max_retries, url
                        )
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.warning(
                        _(
                            "HEAD请求超时（已达最大重试次数），退避到GET请求：{0}"
                        ).format(url)
                    )
                    break

            except httpx.HTTPStatusError as e:
                if e.response.status_code in (404, 405, 403):  # 常见的HEAD不支持状态码
                    logger.debug(
                        _("HEAD请求HTTP错误：{0}，状态码：{1}，退避到GET请求").format(
                            url, e.response.status_code
                        )
                    )
                    break
                elif attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(
                        _(
                            "HEAD请求HTTP错误：{0}，状态码：{1}，{2} 秒后重试 ({3}/{4})"
                        ).format(
                            url,
                            e.response.status_code,
                            wait_time,
                            attempt + 1,
                            max_retries,
                        )
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.warning(
                        _(
                            "HEAD请求HTTP错误（已达最大重试次数）：{0}，状态码：{1}，退避到GET请求"
                        ).format(url, e.response.status_code)
                    )
                    break

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(
                        _("HEAD请求发生错误，{0}秒后重试 ({1}/{2})：{3}").format(
                            wait_time, attempt + 1, max_retries, str(e)
                        )
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.warning(
                        _(
                            "HEAD请求发生错误（已达最大重试次数），退避到GET请求：{0}"
                        ).format(str(e))
                    )
                    break

        # 策略2：退避到GET Stream请求获取Content-Length
        logger.debug(_("尝试使用GET Stream请求获取Content-Length"))
        try:
            async with aclient.stream("GET", url) as response:
                response.raise_for_status()

                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > 0:
                    logger.debug(
                        _("GET请求成功获取Content-Length: {0}").format(content_length)
                    )
                    return int(content_length)
                else:
                    logger.debug(
                        _("策略2: 无法通过GET Stream获取Content-Length，退避到策略3")
                    )

                # 如果GET请求也没有Content-Length，说明可能是动态内容或chunked传输
                # 这种情况下返回0，让下载器使用流式下载
                logger.debug(
                    _("GET请求成功但无Content-Length头，将使用流式下载：{0}").format(
                        url
                    )
                )

        except Exception as e:
            logger.error(_("GET Stream请求也失败：{0}，错误：{1}").format(url, str(e)))
            trace_logger.error(traceback.format_exc())
            return 0

        # 策略3：退避到GET请求获取Content-Length
        logger.debug(_("尝试使用GET请求获取Content-Length"))
        try:
            response = await aclient.get(url)
            response.raise_for_status()

            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > 0:
                logger.debug(
                    _("GET请求成功获取Content-Length: {0}").format(content_length)
                )
                return int(content_length)

            # 如果GET请求也没有Content-Length，说明可能是动态内容或chunked传输
            # 这种情况下返回0，让下载器使用流式下载
            logger.debug(
                _("GET请求成功但无Content-Length头，将使用流式下载：{0}").format(url)
            )
            return 0

        except Exception as e:
            logger.error(_("GET请求也失败：{0}，错误：{1}").format(url, str(e)))
            trace_logger.error(traceback.format_exc())
            return 0


def trim_filename(filename: Union[str, Path], max_length: int = 50) -> str:
    """
    裁剪文件名以适应控制台显示 (Trim the filename to fit console display)

    Args:
        filename (str or Path): 完整的文件名 (Full filename)
        max_length (int): 显示的最大字符数 (Maximum number of characters to display)

    Returns:
        裁剪后的文件名 (trimmed filename)
    """

    filename = str(ensure_path(filename))

    prefix_suffix_len = max_length // 2 - 2

    # 如果文件名长度超过最大长度，则进行裁剪
    return (
        f"{filename[:prefix_suffix_len]}...{filename[-prefix_suffix_len:]}"
        if len(str(filename)) > max_length
        else filename
    )


def get_chunk_size(file_size: int) -> int:
    """
    根据文件大小确定合适的下载块大小 (Determine appropriate download chunk size based on file size)

    Args:
        file_size (int): 文件大小，单位为字节 (File size in bytes)

    Returns:
        int: 下载块的大小 (Size of the download chunk)
    """

    # 文件大小单位为字节 (File size is in bytes)
    if file_size < 10 * 1024:  # 小于10KB (Less than 10KB)
        return file_size  # 一次性下载整个文件 (Download the entire file at once)
    elif file_size < 1 * 1024 * 1024:  # 小于1MB (Less than 1MB)
        return file_size // 10
    elif file_size < 10 * 1024 * 1024:  # 小于10MB (Less than 10MB)
        return file_size // 20
    elif file_size < 100 * 1024 * 1024:  # 小于100MB (Less than 100MB)
        return file_size // 50
    else:  # 文件大小大于100MB (File size greater than 100MB)
        return 1 * 1024 * 1024  # 使用1MB的块大小 (Use a chunk size of 1MB)


async def get_segments_from_m3u8(
    url: str, visited_urls: Optional[set] = None, depth: int = 0, max_depth: int = 5
) -> Optional[List[Segment]]:
    """
    从给定的m3u8文件中获取segments，支持嵌套m3u8文件并防止无限递归

    Args:
        url (str): m3u8文件的URL
        visited_urls (Optional[set]): 已访问过的URL集合，用于防止循环引用
        depth (int): 当前递归深度
        max_depth (int): 最大递归深度，默认为5

    Returns:
        Optional[List[Segment]]: m3u8文件中的segments列表，如果加载失败则返回None
    """
    # 初始化已访问URL集合
    if visited_urls is None:
        visited_urls = set()

    # 检查递归深度
    if depth >= max_depth:
        logger.warning(
            _("m3u8文件嵌套深度超过最大限制 {0}，停止解析：{1}").format(max_depth, url)
        )
        return None

    # 检查是否已访问过此URL（防止循环引用）
    if url in visited_urls:
        logger.warning(_("检测到m3u8循环引用，跳过URL：{0}").format(url))
        return None

    visited_urls.add(url)

    # 应该先测试m3u8文件是否存在，以避免出现错误
    try:
        m3u8_obj = m3u8.load(url)
    except HTTPError as e:
        trace_logger.error(_("无法加载m3u8文件：{0}，错误详情：{1}").format(url, e))
        trace_logger.error(traceback.format_exc())
        return None
    except Exception as e:
        trace_logger.error(_("加载m3u8文件时发生错误：{0}").format(e))
        trace_logger.error(traceback.format_exc())
        return None

    # 如果没有segments说明m3u8可能存在嵌套, 需要尝试获取嵌套的m3u8文件
    segments = m3u8_obj.segments
    if not segments:
        logger.debug(
            _(
                "未找到m3u8文件的segments (深度: {0}/{1}), 尝试获取嵌套的m3u8文件"
            ).format(depth + 1, max_depth)
        )

        # 检查是否有嵌套的playlist
        if not m3u8_obj.playlists:
            logger.warning(
                _("m3u8文件中既无segments也无嵌套playlists，可能直播结束或格式不支持")
            )
            return None

        # 尝试获取嵌套的m3u8文件（通常选择第一个或质量最高的）
        try:
            # 优先选择质量最高的流
            best_playlist = max(
                m3u8_obj.playlists,
                key=lambda p: (
                    getattr(p.stream_info, "bandwidth", 0)  # 使用带宽作为质量指标
                    if hasattr(p, "stream_info") and p.stream_info
                    else 0
                ),
            )
            nested_m3u8_url = best_playlist.absolute_uri
            logger.debug(
                _("选择嵌套m3u8 URL: {0} (带宽: {1})").format(
                    nested_m3u8_url,
                    (
                        getattr(best_playlist.stream_info, "bandwidth", _("未知"))
                        if hasattr(best_playlist, "stream_info")
                        and best_playlist.stream_info
                        else _("未知")
                    ),
                )
            )
        except (IndexError, AttributeError) as e:
            logger.error(_("获取嵌套m3u8 URL失败：{0}").format(e))
            trace_logger.error(traceback.format_exc())
            return None

        # 递归获取嵌套的segments
        segments = await get_segments_from_m3u8(
            nested_m3u8_url, visited_urls, depth + 1, max_depth
        )

        # 再次检查segments是否存在
        if not segments:
            logger.warning(
                _("未找到嵌套m3u8文件的segments, 可能直播结束或该直播非m3u8格式")
            )

    return segments


async def get_segments_duration(url: str) -> Union[List[float], None]:
    """
    从给定的m3u8文件中获取segments的duration

    Args:
        url (str): m3u8文件的URL

    Returns:
        Union[List[float], None]: segments的duration列表，如果获取失败则返回None
    """
    segments = await get_segments_from_m3u8(url)
    if segments is None:
        return None
    return [segment.duration for segment in segments]

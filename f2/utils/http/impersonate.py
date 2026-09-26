# path: f2/utils/http/impersonate.py

import functools
from typing import Any, Dict, Optional, Tuple, Union

import httpx

from f2.i18n.translator import _
from f2.log.logger import logger

# 这些请求头由 curl 生成；Accept-Encoding 也交给 curl，响应才会按浏览器支持的编码自动解压
_CURL_MANAGED_HEADERS = frozenset(
    {"host", "accept-encoding", "connection", "content-length", "transfer-encoding"}
)
# curl 返回的是解压后的内容，这些响应头已与响应体不符
_DECODED_RESPONSE_HEADERS = frozenset(
    {"content-encoding", "content-length", "transfer-encoding"}
)
# CURLINFO_HTTP_VERSION 的取值
_HTTP_VERSIONS = {
    1: b"HTTP/1.0",
    2: b"HTTP/1.1",
    3: b"HTTP/2",
    4: b"HTTP/2",
    5: b"HTTP/2",
    30: b"HTTP/3",
    31: b"HTTP/3",
}


@functools.lru_cache(maxsize=None)
def _warn_missing_once() -> None:
    """未安装 curl_cffi 时只提示一次 (Warn only once when curl_cffi is missing)"""
    logger.warning(
        _(
            "未安装 curl_cffi，无法模拟浏览器的 TLS 指纹，TikTok 等网站的接口可能只返回空内容。"
            "请执行 pip install curl_cffi 后重试"
        )
    )


def _curl_timeout(
    timeout: Dict[str, Optional[float]],
) -> Union[None, float, Tuple[float, float]]:
    """把 httpx 的超时设置换成 curl_cffi 的 (连接超时, 读取超时)"""
    connect, read = timeout.get("connect"), timeout.get("read")
    if connect is not None and read is not None:
        return (connect, read)
    return connect if connect is not None else read


def _to_httpx_error(error: Exception, request: httpx.Request) -> Exception:
    """把 curl_cffi 的异常换成对应的 httpx 异常，爬虫原有的重试与报错逻辑无需改动"""
    try:
        from curl_cffi.requests import exceptions as curl_errors
    except ImportError:
        return error

    pairs = (
        (curl_errors.ConnectTimeout, httpx.ConnectTimeout),
        (curl_errors.Timeout, httpx.ReadTimeout),
        (curl_errors.ProxyError, httpx.ProxyError),
        (curl_errors.ConnectionError, httpx.ConnectError),
        (curl_errors.CurlError, httpx.TransportError),
    )
    for curl_error, httpx_error in pairs:
        if isinstance(error, curl_error):
            return httpx_error(str(error), request=request)
    return error


class ImpersonateTransport(httpx.AsyncBaseTransport):
    """
    用 curl_cffi 发送请求的 httpx 传输层，TLS 与 HTTP/2 指纹与 Chrome 一致
    (httpx transport that sends requests through curl_cffi with Chrome's fingerprints)

    2026-09-26 实测，www.tiktok.com 的接口会校验客户端指纹：httpx 发出的请求即使签名正确，
    也只会得到 200 空内容（响应头 tt_orcas_res: 1）；curl_cffi 模拟 Chrome 后同一请求正常返回，
    只模拟 TLS 而改用 HTTP/1.1 仍然不行。

    重定向、cookie 与重试仍由 httpx 客户端处理，这里只发送单个请求：URL 原样发送，
    签名覆盖的就是这串字节；curl 不保存响应中的 cookie，避免与请求头中的 cookie 重复发送。
    """

    def __init__(self, session: Any) -> None:
        self._session = session

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        headers = [
            (key, value)
            for key, value in request.headers.multi_items()
            if key.lower() not in _CURL_MANAGED_HEADERS
        ]
        content = await request.aread()

        try:
            response = await self._session.request(
                request.method,
                str(request.url),
                headers=headers,
                data=content or None,
                timeout=_curl_timeout(request.extensions.get("timeout", {})),
                allow_redirects=False,
                quote=False,
            )
        except Exception as error:
            mapped = _to_httpx_error(error, request)
            if mapped is error:
                raise
            raise mapped from error

        return httpx.Response(
            status_code=response.status_code,
            headers=[
                (key, value)
                for key, value in response.headers.multi_items()
                if key.lower() not in _DECODED_RESPONSE_HEADERS
            ],
            content=response.content,
            request=request,
            extensions={
                "http_version": _HTTP_VERSIONS.get(
                    int(response.http_version or 0), b"HTTP/1.1"
                )
            },
        )

    async def aclose(self) -> None:
        await self._session.close()


def create_impersonate_transport(
    *,
    proxy: Optional[str] = None,
    verify: Union[bool, str] = True,
    max_clients: int = 10,
    impersonate: str = "chrome",
) -> Optional[ImpersonateTransport]:
    """
    创建模拟浏览器指纹的传输层 (Create a transport that impersonates a browser)

    curl_cffi 是可选依赖，未安装时返回 None 并提示一次，调用方继续使用 httpx。

    Args:
        proxy (Optional[str]): 代理地址，支持 http、https、socks4、socks5
        verify (Union[bool, str]): 是否校验 TLS 证书，或 CA 证书文件路径
        max_clients (int): 最大并发连接数
        impersonate (str): 模拟的浏览器，默认为 curl_cffi 支持的最新版 Chrome

    Returns:
        Optional[ImpersonateTransport]: 传输层，未安装 curl_cffi 时为 None
    """
    try:
        from curl_cffi.requests import AsyncSession
    except ImportError:
        _warn_missing_once()
        return None

    session = AsyncSession(
        impersonate=impersonate,
        proxy=proxy,
        # 运行时也接受 CA 证书文件路径（设置为 CAINFO），curl_cffi 的类型标注只写了 bool
        verify=verify,  # type: ignore[arg-type]
        max_clients=max_clients,
        discard_cookies=True,
    )
    return ImpersonateTransport(session)

# path: f2/crawlers/websocket_crawler.py

import asyncio
import re
import time
import traceback
from typing import Optional
from urllib.parse import unquote, urlsplit

from websockets import __version__ as websockets_version
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import (
    ConnectionClosedError,
    ConnectionClosedOK,
    InvalidStatus,
)
from websockets.protocol import State

from f2.exceptions.api_exceptions import APIConnectionError
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.time.timestamp import timestamp_2_str

# websockets 17.2 起才解码代理地址中按 URL 编码的用户名与密码，之前的版本原样用于认证
_DECODES_PROXY_AUTH = tuple(
    int(part) for part in re.findall(r"\d+", websockets_version)[:2]
) >= (17, 2)


def _websockets_proxy(proxy: Optional[str]) -> Optional[str]:
    """
    交给 websockets 的代理地址 (Proxy URL for websockets)

    F2 的代理地址中用户名与密码按 URL 编码（见 proxy_url_from_config），websockets 17.2
    之前的版本不会解码，编码后的值会被当成密码发给代理，这里还原为原文。原文中有 /、?、#
    时这些版本无法解析代理地址，需要升级 websockets。
    """
    if not proxy or _DECODES_PROXY_AUTH:
        return proxy or None
    parts = urlsplit(proxy)
    if parts.username is None or parts.password is None:
        return proxy
    host = parts.netloc.rpartition("@")[2]
    auth = f"{unquote(parts.username)}:{unquote(parts.password)}"
    return f"{parts.scheme}://{auth}@{host}"


class WebSocketCrawler:
    """
    WebSocket 爬虫客户端 (WebSocket Crawler Client)

    该类提供了一个 WebSocket 客户端，可以通过 WebSocket 协议连接到服务器，接收和发送消息。它支持代理、超时控制、连接和消息的处理等功能。

    类属性:
    - websocket (websockets.asyncio.client.ClientConnection): WebSocket 客户端连接。
    - wss_headers (dict): 自定义 WebSocket 请求头信息。
    - proxy (str): 代理地址，未配置时使用环境变量与系统设置中的代理。
    - callbacks (dict): 存储 WebSocket 回调函数的字典。
    - timeout (int): WebSocket 接收消息的超时时间。

    类方法:
    - connect_websocket: 连接到指定的 WebSocket 服务器。
    - receive_messages: 接收 WebSocket 消息并进行处理。
    - close_websocket: 关闭 WebSocket 连接。
    - on_message: 处理接收到的消息。
    - on_error: 处理 WebSocket 错误消息。
    - on_close: 处理 WebSocket 关闭事件。
    - on_open: 处理 WebSocket 打开事件。
    - __aenter__: 异步上下文管理器的进入方法，连接 WebSocket。
    - __aexit__: 异步上下文管理器的退出方法，关闭 WebSocket 连接。

    异常处理:
    - 该类会根据 WebSocket 连接的错误、消息接收超时等情况抛出相应的异常，并通过日志记录错误信息。

    使用示例:
    ```python
        # 创建 WebSocketCrawler 实例并使用异步方式连接 WebSocket 服务器
        async with WebSocketCrawler(wss_headers={"Cookie": ""}, timeout=10) as crawler:
            await crawler.connect_websocket("wss://example.com/socket")
            await crawler.receive_messages()
    ```
    """

    # 服务器拒绝握手后再次连接前等待的秒数
    retry_delay: float = 2

    def __init__(
        self,
        wss_headers: dict,
        callbacks: Optional[dict] = None,
        timeout: int = 10,
        proxy: Optional[str] = None,
    ):
        """
        初始化 WebSocketCrawler 实例

        Args:
            wss_headers: WebSocket 连接头信息
            callbacks: WebSocket 回调函数
            timeout: WebSocket 超时时间
            proxy: 代理地址（http、https、socks4、socks5），为空时与其他请求一样
                使用环境变量与系统设置中的代理
        """
        self.websocket: Optional[ClientConnection] = None
        self.wss_headers = wss_headers
        self.proxy = _websockets_proxy(proxy)
        self.callbacks = callbacks or {}  # 存储回调函数
        self.timeout = timeout
        # 爬虫主动关闭连接的原因（如本地服务器没有客户端时为 "no_client"），receive_messages 以此作为返回值
        self.close_reason: Optional[str] = None

    async def connect_websocket(self, websocket_uri: str, attempts: int = 3):
        """
        连接 WebSocket

        websockets 15 起原生支持 HTTP 与 SOCKS 代理（SOCKS 由 python-socks 提供），
        不再需要 websockets_proxy；配置了代理时使用它，否则使用环境变量与系统设置中的代理。

        Args:
            websocket_uri: WebSocket URI (ws:// or wss://)
            attempts: 服务器拒绝握手（返回非 101 状态码）时最多尝试的次数

        Raises:
            APIConnectionError: 连接被拒绝，或多次握手都被服务器拒绝
        """
        for attempt in range(1, attempts + 1):
            try:
                self.websocket = await connect(
                    websocket_uri,
                    additional_headers=self.wss_headers,
                    proxy=self.proxy or True,
                    ping_interval=10,
                    ping_timeout=None,
                )
                logger.debug(
                    _(
                        "[ConnectWebsocket] [🌐 已连接 WebSocket] | [服务器：{0}]"
                    ).format(websocket_uri)
                )
                return
            except ConnectionRefusedError as exc:
                trace_logger.error(traceback.format_exc())
                raise APIConnectionError(
                    _(
                        "[ConnectWebSocket] [🚫 WebSocket 连接被拒绝] | [错误：{0}]"
                    ).format(exc)
                ) from exc
            except InvalidStatus as exc:
                trace_logger.error(traceback.format_exc())
                logger.error(
                    _("[ConnectWebSocket] [⚠️ 无效状态码] | [状态码：{0}]").format(exc)
                )
                # 此前一直递归重试，服务器持续拒绝时程序不会结束
                if attempt == attempts:
                    raise APIConnectionError(
                        _(
                            "[ConnectWebSocket] [🚫 WebSocket 连接被拒绝] | [错误：{0}]"
                        ).format(exc)
                    ) from exc
                await asyncio.sleep(self.retry_delay)

    async def receive_messages(self):
        """
        接收 WebSocket 消息并处理

        Returns:
            str: 结束原因。连接关闭为 "closed"，处理出错为 "error"；
                 爬虫通过 close_websocket(reason=...) 主动关闭时为该原因
        """

        logger.info(_("[ReceiveMessages] [📩 开始接收消息]"))
        logger.info(
            _("[ReceiveMessages] [⏱ 消息等待超时：{0} 秒]").format(self.timeout)
        )

        timeout_count = 0

        while True:
            try:
                if self.websocket is None:
                    logger.error(_("[ReceiveMessages] [❌ WebSocket未连接]"))
                    return "closed"

                message = await asyncio.wait_for(
                    self.websocket.recv(), timeout=self.timeout
                )
                # 为wss连接设置10秒超时机制
                timestamp = timestamp_2_str(time.time(), "%Y-%m-%d %H:%M:%S")
                logger.info(
                    _("[ReceiveMessages] | [⏳ 接收消息 {0}]").format(timestamp)
                )

                timeout_count = 0  # 重置超时计数
                await self.on_message(message)

            except asyncio.TimeoutError:
                timeout_count += 1
                logger.warning(
                    _("[ReceiveMessages] [⚠️ 超时] | [超时次数：{0} / 3]").format(
                        timeout_count
                    )
                )
                if timeout_count >= 3:
                    logger.warning(
                        _(
                            "[ReceiveMessages] [❌ 超时关闭连接] | "
                            "[超时次数：{0}] [连接状态：未连接]"
                        ).format(timeout_count)
                    )
                    return "closed"
                if self.websocket is None or self.websocket.state is State.CLOSED:
                    logger.warning(
                        _(
                            "[ReceiveMessages] [🔒 远程服务器关闭] | [WebSocket 连接结束]"
                        )
                    )
                    return "closed"
            except ConnectionClosedError as exc:
                if self.close_reason:
                    return self.close_reason
                trace_logger.error(traceback.format_exc())
                logger.warning(
                    _("[ReceiveMessages] [🔌 连接关闭] | [原因：{0}]").format(exc)
                )
                return "closed"

            except ConnectionClosedOK:
                # 爬虫主动关闭时连接同样正常结束，返回关闭原因，调用方才能与直播结束区分
                if self.close_reason:
                    logger.debug(
                        _("[ReceiveMessages] [✔️ 主动关闭] | [原因：{0}]").format(
                            self.close_reason
                        )
                    )
                    return self.close_reason
                logger.info(
                    _("[ReceiveMessages] [✔️ 正常关闭] | [WebSocket 连接正常关闭]")
                )
                return "closed"

            except Exception as exc:
                trace_logger.error(traceback.format_exc())
                logger.error(
                    _("[ReceiveMessages] [⚠️ 消息处理错误] | [错误：{0}]").format(exc)
                )
                return "error"

    async def close_websocket(self, reason: Optional[str] = None):
        """
        关闭 WebSocket 连接

        Args:
            reason: 主动关闭的原因，receive_messages 会以它作为返回值
        """
        if reason:
            self.close_reason = reason
        if self.websocket:
            await self.websocket.close()
            logger.debug(_("[CloseWebSocket] [🔒 WebSocket 已关闭]"))

    async def on_message(self, message):
        """
        处理 WebSocket 消息

        Args:
            message: WebSocket 消息
        """
        logger.debug(_("[OnMessage] [📩 收到消息] | [内容：{0}]").format(message))

    async def on_error(self, message):
        """
        处理 WebSocket 错误

        Args:
            message: WebSocket 错误
        """
        logger.error(_("[OnError] [⚠️ 错误] | [内容：{0}]").format(message))

    async def on_close(self, message):
        """
        处理 WebSocket 关闭

        Args:
            message: WebSocket 关闭消息
        """
        logger.info(_("[OnClose] [🔒 连接关闭] | [关闭原因：{0}]").format(message))

    async def on_open(self):
        """
        处理 WebSocket 打开
        """
        logger.info(_("[OnOpen] [🌐 连接已打开] | [WebSocket 连接成功]"))

    async def __aenter__(self):
        """
        进入异步上下文：连接WebSocket
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        退出异步上下文：关闭WebSocket连接
        """
        await self.close_websocket()

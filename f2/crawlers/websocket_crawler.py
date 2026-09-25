# path: f2/crawlers/websocket_crawler.py

import asyncio
import time
import traceback
from typing import Optional

import websockets
import websockets_proxy  # type: ignore[import-untyped]
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from f2.exceptions.api_exceptions import APIConnectionError
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.time.timestamp import timestamp_2_str


class WebSocketCrawler:
    """
    WebSocket 爬虫客户端 (WebSocket Crawler Client)

    该类提供了一个 WebSocket 客户端，可以通过 WebSocket 协议连接到服务器，接收和发送消息。它支持代理、超时控制、连接和消息的处理等功能。

    类属性:
    - websocket (websockets.WebSocketClientProtocol): WebSocket 客户端实例。
    - wss_headers (dict): 自定义 WebSocket 请求头信息。
    - proxy (websockets_proxy.Proxy): 代理设置，用于 WebSocket 连接。
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
        """
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.wss_headers = wss_headers
        self.proxy = websockets_proxy.Proxy.from_url(proxy) if proxy else None
        self.callbacks = callbacks or {}  # 存储回调函数
        self.timeout = timeout

    async def connect_websocket(
        self,
        websocket_uri: str,
    ):
        """
        连接 WebSocket

        Args:
            websocket_uri: WebSocket URI (ws:// or wss://)
        """
        try:
            # https://websockets.readthedocs.io/en/stable/reference/features.html#client websockets库暂不支持代理
            # https://github.com/racinette/websockets_proxy 使用websockets_proxy库进行代理
            if self.proxy:
                self.websocket = await websockets_proxy.proxy_connect(
                    websocket_uri,
                    extra_headers=self.wss_headers,
                    proxy=self.proxy,
                    ping_interval=10,
                    ping_timeout=None,
                )
            else:
                self.websocket = await websockets.connect(
                    websocket_uri, extra_headers=self.wss_headers
                )
            logger.debug(
                _("[ConnectWebsocket] [🌐 已连接 WebSocket] | [服务器：{0}]").format(
                    websocket_uri
                )
            )
        except ConnectionRefusedError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _("[ConnectWebSocket] [🚫 WebSocket 连接被拒绝] | [错误：{0}]").format(
                    exc
                )
            ) from exc

        except websockets.InvalidStatusCode as exc:
            trace_logger.error(traceback.format_exc())
            logger.error(
                _("[ConnectWebSocket] [⚠️ 无效状态码] | [状态码：{0}]").format(exc)
            )
            await asyncio.sleep(2)
            await self.connect_websocket(websocket_uri)

    async def receive_messages(self):
        """
        接收 WebSocket 消息并处理
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
                if self.websocket is None or self.websocket.closed:
                    logger.warning(
                        _(
                            "[ReceiveMessages] [🔒 远程服务器关闭] | [WebSocket 连接结束]"
                        )
                    )
                    return "closed"
            except ConnectionClosedError as exc:
                trace_logger.error(traceback.format_exc())
                logger.warning(
                    _("[ReceiveMessages] [🔌 连接关闭] | [原因：{0}]").format(exc)
                )
                return "closed"

            except ConnectionClosedOK:
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

    async def close_websocket(self):
        """
        关闭 WebSocket 连接
        """
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

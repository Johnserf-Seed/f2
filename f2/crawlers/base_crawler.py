# path: f2/crawlers/base_crawler.py

import time
import httpx
import json
import asyncio
import traceback
import websockets
import websockets_proxy

from httpx import Response
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.exceptions.conf_exceptions import InvalidEncodingError
from f2.exceptions.api_exceptions import (
    APIConnectionError,
    APIResponseError,
    APITimeoutError,
    APIUnavailableError,
    APIUnauthorizedError,
    APINotFoundError,
    APIRateLimitError,
    APIRetryExhaustedError,
)
from f2.utils.utils import timestamp_2_str


class BaseCrawler:
    """
    基础爬虫客户端 (Base Crawler Client)

    该类提供了一个通用的爬虫客户端，可以使用同步或异步方式发起 HTTP 请求。它支持 GET、POST 和 HEAD 请求，并具备代理支持、超时控制、重试机制、最大连接数等功能。

    类属性:
    - proxies (dict): 代理设置，用于支持 HTTP 和 HTTPS 请求的代理。
    - http_proxy (str): HTTP 代理地址。
    - https_proxy (str): HTTPS 代理地址。
    - crawler_headers (dict): 自定义请求头。
    - _max_tasks (int): 最大异步任务数。
    - semaphore (asyncio.Semaphore): 用于限制并发任务数的信号量。
    - _max_connections (int): 最大连接数。
    - limits (httpx.Limits): 用于限制最大连接数的配置。
    - _max_retries (int): 请求重试次数。
    - _timeout (int): 请求超时时间。
    - timeout (httpx.Timeout): 超时设置。
    - _aclient (httpx.AsyncClient): 异步 HTTP 客户端。
    - _client (httpx.Client): 同步 HTTP 客户端。

    类方法:
    - aclient (property): 获取异步客户端（如果未初始化则创建）。
    - client (property): 获取同步客户端（如果未初始化则创建）。
    - _create_mount: 根据是否异步模式创建 HTTP 传输配置。
    - _fetch_response: 获取接口的响应数据（原始响应）。
    - _fetch_get_json: 获取接口的响应并解析为 JSON 数据（GET 请求）。
    - _fetch_post_json: 获取接口的响应并解析为 JSON 数据（POST 请求）。
    - parse_json: 解析 JSON 响应对象。
    - get_fetch_data: 发送 GET 请求并获取响应数据。
    - post_fetch_data: 发送 POST 请求并获取响应数据。
    - head_fetch_data: 发送 HEAD 请求并获取响应数据。
    - handle_http_status_error: 处理 HTTP 状态码错误并抛出相应的自定义异常。
    - close: 关闭客户端，释放资源。
    - __aenter__: 异步上下文管理器的进入方法。
    - __aexit__: 异步上下文管理器的退出方法。

    异常处理:
    - 该类会根据不同的 HTTP 错误状态码或请求异常，抛出相应的自定义异常，如 APITimeoutError、APIConnectionError 等。

    使用示例:
    ```python
        # 创建 BaseCrawler 实例并使用异步方式获取数据
        async with BaseCrawler(proxies={'http://': 'http://proxy.com'}, crawler_headers={'User-Agent': 'MyCrawler'}) as crawler:
            response = await crawler._fetch_get_json("https://api.example.com/data")
            print(response)
    ```
    """

    def __init__(
        self,
        kwargs: dict = {},
        *,
        proxies: dict = {},
        crawler_headers: dict = {},
    ):
        # 设置代理 (Set proxy)
        self.proxies = proxies
        self.http_proxy = self.proxies.get("http://", None)
        self.https_proxy = self.proxies.get("https://", None)

        # 爬虫请求头 / Crawler request header
        self.crawler_headers = crawler_headers or {}

        # 异步的任务数 / Number of asynchronous tasks
        self._max_tasks = kwargs.get("max_tasks", 10)
        self.semaphore = asyncio.Semaphore(self._max_tasks)

        # 限制最大连接数 / Limit the maximum number of connections
        self._max_connections = kwargs.get("max_connections", 10)
        self.limits = httpx.Limits(max_connections=self._max_connections)

        # 业务逻辑重试次数 / Business logic retry count
        self._max_retries = kwargs.get("max_retries", 5)

        # 超时等待时间 / Timeout waiting time
        self._timeout = kwargs.get("timeout", 10)
        self.timeout = httpx.Timeout(self._timeout)

        # 异步客户端 / Asynchronous client
        self._aclient = None

        # 同步客户端 / Synchronous client
        self._client = None

    def _create_mount(self, async_mode=False) -> dict:
        """
        创建挂载配置，根据 async_mode 切换异步或同步的 HTTPTransport

        Args:
            async_mode: bool: 是否异步模式

        Returns:
            dict: 挂载配置
        """

        transport_class = (
            httpx.AsyncHTTPTransport if async_mode else httpx.HTTPTransport
        )
        if isinstance(self.proxies, dict) and self.http_proxy:
            return {
                "all://": transport_class(
                    verify=False,
                    limits=self.limits,
                    proxy=httpx.Proxy(url=self.http_proxy),
                    local_address="0.0.0.0",
                    retries=self._max_retries,
                ),
            }
        else:
            return {
                "all://": transport_class(
                    verify=False,
                    limits=self.limits,
                    retries=self._max_retries,
                ),
            }

    @property
    def aclient(self):
        if self._aclient is None:
            try:
                self._aclient = httpx.AsyncClient(
                    headers=self.crawler_headers,
                    mounts=self._create_mount(async_mode=True),
                    timeout=self.timeout,
                )
            except UnicodeEncodeError:
                raise InvalidEncodingError
        return self._aclient

    @property
    def client(self):
        if self._client is None:
            try:
                self._client = httpx.Client(
                    headers=self.crawler_headers,
                    mounts=self._create_mount(),
                    timeout=self.timeout,
                )
            except UnicodeEncodeError:
                raise InvalidEncodingError
        return self._client

    async def _fetch_response(self, endpoint: str) -> Response:
        """获取数据 (Get data)

        Args:
            endpoint (str): 接口地址 (Endpoint URL)

        Returns:
            Response: 原始响应对象 (Raw response object)
        """
        return await self.get_fetch_data(endpoint)

    async def _fetch_get_json(self, endpoint: str) -> dict:
        """获取 JSON 数据 (Get JSON data)

        Args:
            endpoint (str): 接口地址 (Endpoint URL)

        Returns:
            dict: 解析后的JSON数据 (Parsed JSON data)
        """
        response = await self.get_fetch_data(endpoint)
        return self.parse_json(response)

    async def _fetch_post_json(self, endpoint: str, params: dict = {}) -> dict:
        """获取 JSON 数据 (Post JSON data)

        Args:
            endpoint (str): 接口地址 (Endpoint URL)

        Returns:
            dict: 解析后的JSON数据 (Parsed JSON data)
        """
        response = await self.post_fetch_data(endpoint, params)
        return self.parse_json(response)

    def parse_json(self, response: Response) -> dict:
        """解析JSON响应对象 (Parse JSON response object)

        Args:
            response (Response): 原始响应对象 (Raw response object)

        Returns:
            dict: 解析后的JSON数据 (Parsed JSON data)
        """
        if (
            response is not None
            and isinstance(response, Response)
            and response.status_code == 200
        ):
            try:
                return response.json()
            except json.JSONDecodeError as e:
                logger.error(
                    _("解析 {0} 接口 JSON 失败：{1}").format(str(response.url), e)
                )
            except UnicodeDecodeError as e:
                logger.error(
                    _("接口 {0} JSON 解码错误：{1}").format(str(response.url), e)
                )
        else:
            if isinstance(response, Response):
                logger.error(
                    _("获取数据失败。状态码: {0}").format(response.status_code)
                )
            else:
                logger.error(_("无效的Json响应"))

        return {}

    async def get_fetch_data(self, url: str):
        """
        获取GET端点数据 (Get GET endpoint data)

        Args:
            url (str): 端点URL (Endpoint URL)

        Returns:
            response: 响应内容 (Response content)
        """
        for attempt in range(self._max_retries):
            try:
                response = await self.aclient.get(url, follow_redirects=True)
                if not response.text.strip() or not response.content:
                    error_message = _(
                        "第 {0} 次请求响应内容为空, 状态码: {1}, URL:{2}"
                    ).format(attempt + 1, response.status_code, str(response.url))

                    logger.warning(error_message)

                    if attempt == self._max_retries - 1:
                        raise APIRetryExhaustedError(
                            _(
                                "获取端点数据失败，重试次数达到上限。代理：{0}，异常类名：{1}"
                            ).format(
                                self.proxies,
                                self.__class__.__name__,
                            )
                        )

                    await asyncio.sleep(self._timeout)
                    continue

                logger.debug(_("响应状态码: {0}").format(response.status_code))
                response.raise_for_status()
                return response

            # 捕获所有与 httpx 请求相关的异常情况 (Captures all httpx request-related exceptions)
            except httpx.TimeoutException as exc:
                raise APITimeoutError(
                    _(
                        "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                    ).format(
                        _("请求端点超时"),
                        url,
                        self.proxies,
                        self.__class__.__name__,
                        exc,
                    )
                )

            except httpx.NetworkError as exc:
                raise APIConnectionError(
                    _(
                        "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                    ).format(
                        _("网络连接失败，请检查当前网络环境"),
                        url,
                        self.proxies,
                        self.__class__.__name__,
                        exc,
                    )
                )

            except httpx.ProtocolError as exc:
                raise APIUnauthorizedError(
                    _(
                        "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                    ).format(
                        _("请求协议错误"),
                        url,
                        self.proxies,
                        self.__class__.__name__,
                        exc,
                    )
                )

            except httpx.ProxyError as exc:
                raise APIConnectionError(
                    _(
                        "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                    ).format(
                        _("请求代理错误"),
                        url,
                        self.proxies,
                        self.__class__.__name__,
                        exc,
                    )
                )

            except httpx.HTTPStatusError as exc:
                self.handle_http_status_error(exc, url, attempt + 1)

            except httpx.RequestError as req_err:
                raise APIConnectionError(
                    _(
                        "连接端点失败，检查网络环境或代理：{0} 代理：{1} 类名：{2} 异常详细信息：{3}"
                    ).format(url, self.proxies, self.__class__.__name__, req_err)
                )

    async def post_fetch_data(self, url: str, params: dict = {}):
        """
        获取POST端点数据 (Get POST endpoint data)

        Args:
            url (str): 端点URL (Endpoint URL)
            params (dict): POST请求参数 (POST request parameters)

        Returns:
            response: 响应内容 (Response content)
        """
        for attempt in range(self._max_retries):
            try:
                response = await self.aclient.post(
                    url, json=dict(params), follow_redirects=True
                )
                if not response.text.strip() or not response.content:
                    error_message = _(
                        "第 {0} 次请求响应内容为空, 状态码: {1}, URL:{2}"
                    ).format(attempt + 1, response.status_code, str(response.url))

                    logger.warning(error_message)

                    if attempt == self._max_retries - 1:
                        raise APIRetryExhaustedError(
                            _("获取端点数据失败, 次数达到上限")
                        )

                    await asyncio.sleep(self._timeout)
                    continue

                logger.debug(_("响应状态码: {0}").format(response.status_code))
                response.raise_for_status()
                return response

            except httpx.RequestError as req_err:
                raise APIConnectionError(
                    _(
                        "连接端点失败，检查网络环境或代理：{0} 代理：{1} 类名：{2} 异常详细信息：{3}"
                    ).format(url, self.proxies, self.__class__.__name__, req_err)
                )

            except httpx.HTTPStatusError as http_error:
                self.handle_http_status_error(http_error, url, attempt + 1)

    async def head_fetch_data(self, url: str):
        """
        获取HEAD端点数据 (Get HEAD endpoint data)

        Args:
            url (str): 端点URL (Endpoint URL)

        Returns:
            response: 响应内容 (Response content)
        """
        try:
            response = await self.aclient.head(url)
            logger.debug(_("响应状态码: {0}").format(response.status_code))
            response.raise_for_status()
            return response

        except httpx.RequestError as req_err:
            raise APIConnectionError(
                _(
                    "连接端点失败，检查网络环境或代理：{0} 代理：{1} 类名：{2} 异常详细信息：{3}"
                ).format(url, self.proxies, self.__class__.__name__, req_err)
            )

        except httpx.HTTPStatusError as http_error:
            self.handle_http_status_error(http_error, url, 1)

    def handle_http_status_error(self, http_error, url: str, attempt):
        """
        处理HTTP状态错误 (Handle HTTP status error)

        Args:
            http_error: HTTP状态错误 (HTTP status error)
            url: 端点URL (Endpoint URL)
            attempt: 尝试次数 (Number of attempts)
        Raises:
            APIConnectionError: 连接端点失败 (Failed to connect to endpoint)
            APIResponseError: 响应错误 (Response error)
            APIUnavailableError: 服务不可用 (Service unavailable)
            APINotFoundError: 端点不存在 (Endpoint does not exist)
            APITimeoutError: 连接超时 (Connection timeout)
            APIUnauthorizedError: 未授权 (Unauthorized)
            APIRateLimitError: 请求频率过高 (Request frequency is too high)
            APIRetryExhaustedError: 重试次数达到上限 (The number of retries has reached the upper limit)
        """
        response = getattr(http_error, "response", None)
        status_code = getattr(response, "status_code", None)

        if response is None or status_code is None:
            logger.error(
                _("HTTP状态错误：{0}, URL：{1}, 尝试次数：{2}").format(
                    http_error, url, attempt
                )
            )
            raise APIResponseError(
                _("处理HTTP错误时遇到意外情况：{0}").format(http_error)
            )

        # 状态码与异常类的映射
        status_code_exception_map = {
            400: APIResponseError,
            404: APINotFoundError,
            503: APIUnavailableError,
            408: APITimeoutError,
            401: APIUnauthorizedError,
            429: APIRateLimitError,
            444: APIUnavailableError,
        }

        # 根据状态码抛出对应的异常
        if status_code in status_code_exception_map:
            exception_class = status_code_exception_map[status_code]
            raise exception_class(_("HTTP状态码错误：{0}").format(status_code))

        # 特殊处理状态码 302
        if status_code == 302:
            logger.info(
                _("HTTP状态码302：重定向，URL：{0}，尝试次数：{1}").format(url, attempt)
            )
            return

        # 未知状态码的处理
        logger.error(
            _("未知HTTP状态码：{0}, URL：{1}, 尝试次数：{2}").format(
                status_code, url, attempt
            )
        )
        raise APIResponseError(_("未知HTTP状态码错误：{0}").format(status_code))

    async def close(self):
        # 如果没有初始化客户端，则不关闭 (If the client is not initialized, do not close)
        if self._client:
            self.client.close()
        if self._aclient:
            await self.aclient.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


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
        callbacks: dict = None,
        timeout: int = 10,
        proxy: str = None,
    ):
        """
        初始化 WebSocketCrawler 实例

        Args:
            wss_headers: WebSocket 连接头信息
            callbacks: WebSocket 回调函数
            timeout: WebSocket 超时时间
        """
        self.websocket = None
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
            logger.error(
                _("[ConnectWebSocket] [🚫 WebSocket 连接被拒绝] | [错误：{0}]").format(
                    exc
                )
            )
            raise APIConnectionError(
                _("[ConnectWebSocket] [❌ WebSocket 连接失败] | [服务器：{0}]").format(
                    exc
                )
            )

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
                            "[超时次数：{0}] [连接状态：{1}]"
                        ).format(timeout_count, self.websocket.closed)
                    )
                    return "closed"
                if self.websocket.closed:
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

# path: f2/crawlers/base_crawler.py

import httpx
import json
import asyncio
import traceback
import websockets

from httpx import Response
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from f2.i18n.translator import _
from f2.log.logger import logger
from f2.exceptions.api_exceptions import (
    APIError,
    APIConnectionError,
    APIResponseError,
    APITimeoutError,
    APIUnavailableError,
    APIUnauthorizedError,
    APINotFoundError,
    APIRateLimitError,
    APIRetryExhaustedError,
)


class BaseCrawler:
    """
    基础爬虫客户端 (Base crawler client)
    """

    def __init__(
        self,
        proxies: dict = ...,
        max_retries: int = 5,
        max_connections: int = 10,
        timeout: int = 10,
        max_tasks: int = 10,
        crawler_headers: dict = {},
    ):
        # 设置代理 (Set proxy)
        self.proxies = proxies
        if isinstance(proxies, dict):
            # 底层连接重试次数 / Underlying connection retry count
            self.sync_transport = httpx.HTTPTransport(
                proxy=proxies.get("http://", None),
                retries=max_retries,
                local_address="0.0.0.0",
            )
            # 底层连接重试次数 / Underlying connection retry count
            self.async_transport = httpx.AsyncHTTPTransport(
                proxy=proxies.get("http://", None),
                retries=max_retries,
                local_address="0.0.0.0",
            )

        # 爬虫请求头 / Crawler request header
        self.crawler_headers = crawler_headers or {}

        # 异步的任务数 / Number of asynchronous tasks
        self._max_tasks = max_tasks
        self.semaphore = asyncio.Semaphore(max_tasks)

        # 限制最大连接数 / Limit the maximum number of connections
        self._max_connections = max_connections
        self.limits = httpx.Limits(max_connections=max_connections)

        # 业务逻辑重试次数 / Business logic retry count
        self._max_retries = max_retries

        # 超时等待时间 / Timeout waiting time
        self._timeout = timeout
        self.timeout = httpx.Timeout(timeout)

        # 异步客户端 / Asynchronous client
        self._aclient = None

        # 同步客户端 / Synchronous client
        self._client = None

    @property
    def aclient(self):
        if self._aclient is None:
            self._aclient = httpx.AsyncClient(
                headers=self.crawler_headers,
                verify=False,
                timeout=self.timeout,
                limits=self.limits,
            )
        return self._aclient

    @property
    def client(self):
        if self._client is None:
            self._client = httpx.Client(
                headers=self.crawler_headers,
                verify=False,
                timeout=self.timeout,
                limits=self.limits,
            )
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
                logger.error(_("解析 {0} 接口 JSON 失败：{1}").format(response.url, e))
            except UnicodeDecodeError as e:
                logger.error(_("解析 {0} 接口 JSON 失败：{1}").format(response.url, e))
        else:
            if isinstance(response, Response):
                logger.error(
                    _("获取数据失败。状态码: {0}").format(response.status_code)
                )
            else:
                logger.error(_("无效响应类型"))

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
                        "第 {0} 次响应内容为空, 状态码: {1}, URL:{2}"
                    ).format(attempt + 1, response.status_code, response.url)

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

            except APIError as e:
                logger.error(e)

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
                        "第 {0} 次响应内容为空, 状态码: {1}, URL:{2}"
                    ).format(attempt + 1, response.status_code, response.url)

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

            except APIError as e:
                logger.error(e)

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

        except APIError as e:
            logger.error(e)

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

        if status_code == 302:
            pass
        elif status_code == 404:
            raise APINotFoundError(_("HTTP状态码错误："), status_code)
        elif status_code == 503:
            raise APIUnavailableError(_("HTTP状态码错误："), status_code)
        elif status_code == 408:
            raise APITimeoutError(_("HTTP状态码错误："), status_code)
        elif status_code == 401:
            raise APIUnauthorizedError(_("HTTP状态码错误："), status_code)
        elif status_code == 429:
            raise APIRateLimitError(_("HTTP状态码错误："), status_code)
        else:
            logger.error(
                _("HTTP状态错误：{0}, URL：{1}, 尝试次数：{2}").format(
                    http_error, url, attempt
                )
            )
            raise APIResponseError(_("HTTP状态码错误："), status_code)

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
    WebSocket爬虫客户端 (WebSocket crawler client)
    """

    def __init__(self, wss_headers: dict, callbacks: dict = None, timeout: int = 10):
        """
        初始化 WebSocketCrawler 实例

        Args:
            wss_headers: WebSocket 连接头信息
            callbacks: WebSocket 回调函数
            timeout: WebSocket 超时时间
        """
        self.websocket = None
        self.wss_headers = wss_headers
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
            # https://websockets.readthedocs.io/en/stable/reference/features.html#client 暂不支持代理
            self.websocket = await websockets.connect(
                websocket_uri, extra_headers=self.wss_headers
            )
            logger.info(_("已连接 WebSocket"))
        except ConnectionRefusedError as exc:
            logger.error(traceback.format_exc())
            logger.error(_("WebSocket 连接被拒绝：{0}").format(exc))
            raise APIConnectionError(_("连接 WebSocket 失败：{0}").format(exc))

        except websockets.InvalidStatusCode as exc:
            logger.error(traceback.format_exc())
            logger.error(_("WebSocket 连接状态码无效：{0}").format(exc))
            await asyncio.sleep(2)
            await self.connect_websocket(websocket_uri)

    async def receive_messages(self):
        """
        接收 WebSocket 消息并处理
        """
        timeout_count = 0
        try:
            while True:
                try:
                    # 为wss连接设置10秒超时机制
                    logger.info(
                        _("等待接收消息，超时时间：{0} 秒").format(self.timeout)
                    )
                    message = await asyncio.wait_for(
                        self.websocket.recv(), timeout=self.timeout
                    )
                    timeout_count = 0  # 重置超时计数
                    await self.on_message(message)
                except asyncio.TimeoutError:
                    logger.warning(_("接收消息超时"))
                    timeout_count += 1
                    if timeout_count >= 3:
                        await self.on_close(_("即将关闭 WebSocket 连接"))
                        return "closed"
                    if self.websocket.closed:
                        await self.on_close(_("即将关闭 WebSocket 连接"))
                        return "closed"
                except ConnectionClosedError as exc:
                    logger.error(traceback.format_exc())
                    await self.on_close(_("WebSocket 连接被关闭：{0}").format(exc))
                    return "closed"
                except ConnectionClosedOK:
                    await self.on_close(_("WebSocket 连接正常关闭"))
                    return "closed"
                except Exception as exc:
                    logger.error(traceback.format_exc())
                    logger.error(_("处理消息时出错：{0}").format(exc))
                    await self.on_error(exc)
                    return "error"

        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(_("接收消息过程中出错：{0}").format(e))
            return "error"

    async def close_websocket(self):
        """
        关闭 WebSocket 连接
        """
        if self.websocket:
            await self.websocket.close()
            logger.info(_("已关闭 WebSocket 连接"))

    async def on_message(self, message):
        """
        处理 WebSocket 消息

        Args:
            message: WebSocket 消息
        """
        logger.debug(_("收到消息：{0}").format(message))

    async def on_error(self, message):
        """
        处理 WebSocket 错误

        Args:
            message: WebSocket 错误
        """
        logger.error(_("WebSocket 错误：{0}").format(message))

    async def on_close(self, message):
        """
        处理 WebSocket 关闭

        Args:
            message: WebSocket 关闭消息
        """
        logger.warning(message)

    async def on_open(self):
        """
        处理 WebSocket 打开
        """
        logger.info(_("WebSocket 连接已打开"))

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

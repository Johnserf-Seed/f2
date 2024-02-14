# path: f2/crawlers/base_crawler.py

import httpx
import json
import asyncio
from urllib.parse import quote, unquote
from httpx import Response


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
        proxies: dict = {},
        max_retries: int = 5,
        max_connections: int = 10,
        timeout: int = 10,
        max_tasks: int = 10,
        crawler_headers: dict = {},
    ):
        if isinstance(proxies, dict):
            self.proxies = proxies
            # [f"{k}://{v}" for k, v in proxies.items()]
        else:
            self.proxies = None

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
        # 底层连接重试次数 / Underlying connection retry count
        self.atransport = httpx.AsyncHTTPTransport(retries=max_retries)

        # 超时等待时间 / Timeout waiting time
        self._timeout = timeout
        self.timeout = httpx.Timeout(timeout)
        # 异步客户端 / Asynchronous client
        self.aclient = httpx.AsyncClient(
            headers=self.crawler_headers,
            proxies=self.proxies,
            timeout=self.timeout,
            limits=self.limits,
            transport=self.atransport,
        )

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
        # 检查响应是否成功 (Check if the response is successful)
        if (
            response is not None
            and isinstance(response, Response)
            and response.status_code == 200
        ):
            try:
                # 尝试解析 JSON 数据 (Try to parse JSON data)
                return response.json()
            except json.JSONDecodeError as e:
                # JSON 解析失败，处理异常 (JSON parsing failed, handling exceptions)
                logger.error(_("解析 {0} 接口 JSON 失败： {1}").format(response.url, e))
        else:
            # 处理响应为 None 或者状态码异常的情况
            if isinstance(response, Response):
                logger.error(
                    _("获取数据失败。状态码: {0}").format(response.status_code)
                )
            else:
                logger.error(_("无效响应类型。响应类型: {0}").format(type(response)))

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

                    print(error_message)
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

            except httpx.RequestError:
                logger.error(
                    _("连接端点失败，检查网络环境或代理: {0} 代理：{1}").format(
                        url, self.proxies
                    )
                )
                raise APIConnectionError(
                    _("连接端点失败，检查网络环境或代理: {0} 代理：{1}").format(
                        url, self.proxies
                    )
                )

            except httpx.HTTPStatusError as http_error:
                self.handle_http_status_error(http_error, url, attempt + 1)

            except APIError as e:
                e.display_error()

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

                    print(error_message)
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

            except httpx.RequestError:
                logger.error(
                    _("连接端点失败，检查网络环境或代理: {0} 代理：{1}").format(
                        url, self.proxies
                    )
                )
                raise APIConnectionError(
                    _("连接端点失败，检查网络环境或代理: {0} 代理：{1}").format(
                        url, self.proxies
                    )
                )

            except httpx.HTTPStatusError as http_error:
                self.handle_http_status_error(http_error, url, attempt + 1)

            except APIError as e:
                e.display_error()

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

        except httpx.RequestError:
            logger.error(
                _("连接端点失败，检查网络环境或代理: {0} 代理：{1}").format(
                    url, self.proxies
                )
            )
            raise APIConnectionError(
                _("连接端点失败，检查网络环境或代理: {0} 代理：{1}").format(
                    url, self.proxies
                )
            )

        except httpx.HTTPStatusError as http_error:
            self.handle_http_status_error(http_error, url, 1)

        except APIError as e:
            e.display_error()

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
                _("HTTP状态错误: {0}, URL: {1}, 尝试次数: {2}").format(
                    http_error, url, attempt
                )
            )
            raise APIResponseError(f"处理HTTP错误时遇到意外情况: {http_error}")

        if status_code == 302:
            pass
        elif status_code == 404:
            raise APINotFoundError(f"HTTP Status Code {status_code}")
        elif status_code == 503:
            raise APIUnavailableError(f"HTTP Status Code {status_code}")
        elif status_code == 408:
            raise APITimeoutError(f"HTTP Status Code {status_code}")
        elif status_code == 401:
            raise APIUnauthorizedError(f"HTTP Status Code {status_code}")
        elif status_code == 429:
            raise APIRateLimitError(f"HTTP Status Code {status_code}")
        else:
            logger.error(
                _("HTTP状态错误: {0}, URL: {1}, 尝试次数: {2}").format(
                    status_code, url, attempt
                )
            )
            raise APIResponseError(f"HTTP状态错误: {status_code}")

    async def close(self):
        await self.aclient.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclient.aclose()

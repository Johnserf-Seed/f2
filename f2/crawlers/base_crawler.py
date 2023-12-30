# path: f2/crawlers/base_crawler.py

import httpx
import json

# import random
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
            self.proxies = proxies or None

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

        # 代理 / Proxy
        # proxy = random.choice(self.proxies)
        # proxies={"http": proxy, "https": proxy}

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

    async def _fetch(self, endpoint: str) -> dict:
        """获取数据 (Get data)

        Args:
            endpoint (str): 接口地址 (Endpoint URL)

        Returns:
            dict: 解析后的JSON数据 (Parsed JSON data)
        """
        response = await self.get_fetch_data(endpoint)

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
                logger.error(_("获取数据失败。状态码: {0}").format(response.status_code))
            else:
                logger.error("Invalid response type.")

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
                response = await self.aclient.get(url)

                if not response.text.strip() or not response.content:
                    print(
                        _("第 {0} 次响应内容为空, 状态码: {1}").format(
                            attempt + 1, response.status_code
                        )
                    )
                    logger.warning(
                        _("第 {0} 次响应内容为空, 状态码: {1}").format(
                            attempt + 1, response.status_code
                        )
                    )

                    if attempt == self._max_retries - 1:
                        raise APIRetryExhaustedError(_("获取端点数据失败, 次数达到上限"))

                    await asyncio.sleep(self._timeout)
                    continue

                logger.debug(_("响应状态码: {0}").format(response.status_code))
                response.raise_for_status()
                return response

            except httpx.RequestError:
                logger.error(
                    _("连接端点失败: {0}").format(url)
                )  #  (Failed to connect to endpoint)
                raise APIConnectionError(_("连接端点失败: {0}").format(url))

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
                response = await self.aclient.post(url, content=dict(params))
                if not response.text.strip() or not response.content:
                    print(
                        _("第 {0} 次响应内容为空, 状态码: {1}").format(
                            attempt + 1, response.status_code
                        )
                    )

                    print(error_message)
                    logger.warning(error_message)

                    if attempt == self._max_retries - 1:
                        raise APIRetryExhaustedError(_("获取端点数据失败, 次数达到上限"))

                    await asyncio.sleep(self._timeout)
                    continue

                logger.debug(_("响应状态码: {0}").format(response.status_code))
                response.raise_for_status()
                return response

            except httpx.RequestError:
                logger.error(_("连接端点失败: {0}").format(url))
                raise APIConnectionError(_("连接端点失败: {0}").format(url))

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
            logger.error(_("连接端点失败: {0}").format(url))
            raise APIConnectionError(_("连接端点失败: {0}").format(url))

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
                _("HTTP状态错误: {0}, URL: {1}, 尝试次数: {2}").format(http_error, url, attempt)
            )
            raise APIResponseError(f"处理HTTP错误时遇到意外情况: {http_error}")

        if status_code == 404:
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

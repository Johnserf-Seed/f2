# path: f2/apps/tiktok/utils.py

import f2
import re
import json
import httpx
import asyncio
import traceback

from typing import Union
from pathlib import Path

from f2.i18n.translator import _
from f2.log.logger import logger
from f2.utils.xbogus import XBogus as XB
from f2.utils.conf_manager import ConfigManager
from f2.utils.utils import (
    gen_random_str,
    get_timestamp,
    extract_valid_urls,
    split_filename,
)
from f2.crawlers.base_crawler import BaseCrawler
from f2.exceptions.api_exceptions import (
    APIConnectionError,
    APIResponseError,
    APIUnauthorizedError,
    APINotFoundError,
    APITimeoutError,
)


class ClientConfManager:
    """
    用于管理客户端配置 (Used to manage client configuration)
    """

    client_conf = (
        ConfigManager(f2.F2_CONFIG_FILE_PATH).get_config("f2").get("tiktok", {})
    )

    @classmethod
    def client(cls) -> dict:
        return cls.client_conf

    @classmethod
    def proxies(cls) -> dict:
        return cls.client_conf.get("proxies", {})

    @classmethod
    def headers(cls) -> dict:
        return cls.client_conf.get("headers", {})

    @classmethod
    def user_agent(cls) -> str:
        return cls.headers().get("User-Agent", "")

    @classmethod
    def referer(cls) -> str:
        return cls.headers().get("Referer", "")

    @classmethod
    def msToken(cls) -> str:
        return cls.client_conf.get("msToken", {})

    @classmethod
    def ttwid(cls) -> str:
        return cls.client_conf.get("ttwid", {})

    @classmethod
    def odin_tt(cls) -> str:
        return cls.client_conf.get("odin_tt", {})


class TokenManager(BaseCrawler):

    token_conf = ClientConfManager.msToken()
    ttwid_conf = ClientConfManager.ttwid()
    odin_tt_conf = ClientConfManager.odin_tt()
    proxies = ClientConfManager.proxies()
    mstoken_headers = {
        "Content-Type": "application/json",
        "User-Agent": ClientConfManager.user_agent(),
    }
    ttwid_headers = {
        "Cookie": ttwid_conf.get("cookie"),
        "Content-Type": "text/plain",
        "User-Agent": ClientConfManager.user_agent(),
    }

    def __init__(self):
        super().__init__(proxies=self.proxies)

    def gen_real_msToken(self) -> str:
        """
        生成真实的msToken,当出现错误时返回虚假的值
        (Generate a real msToken and return a false value when an error occurs)
        """

        try:
            payload = json.dumps(
                {
                    "magic": self.token_conf["magic"],
                    "version": self.token_conf["version"],
                    "dataType": self.token_conf["dataType"],
                    "strData": self.token_conf["strData"],
                    "tspFromClient": get_timestamp(),
                }
            )
            response = self.client.post(
                self.token_conf["url"],
                content=payload,
                headers=self.mstoken_headers,
            )
            response.raise_for_status()

            msToken = str(httpx.Cookies(response.cookies).get("msToken"))

            if len(msToken) not in [148]:
                raise APIResponseError(_("{0} 内容不符合要求").format("msToken"))

            logger.debug(_("生成真实的msToken：{0}").format(msToken))
            return msToken

        # 捕获所有与 httpx 请求相关的异常情况 (Captures all httpx request-related exceptions)
        except httpx.TimeoutException as exc:
            logger.error(traceback.format_exc())
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求端点超时"),
                    self.token_conf["url"],
                    ClientConfManager.proxies(),
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
                    self.token_conf["url"],
                    ClientConfManager.proxies(),
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
                    self.token_conf["url"],
                    ClientConfManager.proxies(),
                    self.__name__,
                    exc,
                )
            )

        except httpx.ProxyError as exc:
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求代理错误"),
                    self.token_conf["url"],
                    ClientConfManager.proxies(),
                    self.__name__,
                    exc,
                )
            )

        except httpx.HTTPStatusError as exc:
            # 捕获 httpx 的状态代码错误 (captures specific status code errors from httpx)
            logger.error(_("msToken API错误：{0}").format(exc))
            if response.status_code == 401:
                raise APIUnauthorizedError(
                    _(
                        "参数验证失败，请更新 F2 配置文件中的 {0}，以匹配 {1} 新规则"
                    ).format("msToken", "tiktok")
                )

            elif response.status_code == 404:
                raise APINotFoundError(_("{0} 无法找到API端点").format("msToken"))
            else:
                raise APIResponseError(
                    _("链接：{0}，状态码 {1}：{2} ").format(
                        exc.response.url,
                        exc.response.status_code,
                        exc.response.text,
                    )
                )

    @classmethod
    def gen_false_msToken(cls) -> str:
        """生成随机msToken (Generate random msToken)"""
        false_msToken = gen_random_str(146) + "=="
        logger.debug(_("生成虚假的msToken：{0}").format(false_msToken))
        return false_msToken

    def gen_ttwid(self) -> str:
        """
        生成请求必带的ttwid (Generate the essential ttwid for requests)
        """

        try:
            response = self.client.post(
                self.ttwid_conf["url"],
                content=self.ttwid_conf["data"],
                headers=self.ttwid_headers,
            )
            response.raise_for_status()

            ttwid = httpx.Cookies(response.cookies).get("ttwid")

            if ttwid is None:
                raise APIResponseError(
                    _("ttwid: 检查没有通过, 请更新配置文件中的ttwid")
                )

            logger.debug(_("生成ttwid：{0}").format(str(ttwid)))
            return str(ttwid)

        # 捕获所有与 httpx 请求相关的异常情况 (Captures all httpx request-related exceptions)
        except httpx.TimeoutException as exc:
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求端点超时"),
                    self.ttwid_conf["url"],
                    ClientConfManager.proxies(),
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
                    self.ttwid_conf["url"],
                    ClientConfManager.proxies(),
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
                    self.ttwid_conf["url"],
                    ClientConfManager.proxies(),
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
                    self.ttwid_conf["url"],
                    ClientConfManager.proxies(),
                    self.__class__.__name__,
                    exc,
                )
            )

        except httpx.HTTPStatusError as exc:
            # 捕获 httpx 的状态代码错误 (captures specific status code errors from httpx)
            if response.status_code == 401:
                raise APIUnauthorizedError(
                    _(
                        "参数验证失败，请更新 F2 配置文件中的 {0}，以匹配 {1} 新规则"
                    ).format("ttwid", "tiktok")
                )

            elif response.status_code == 404:
                raise APINotFoundError(_("{0} 无法找到API端点").format("ttwid"))
            else:
                raise APIResponseError(
                    _("链接：{0}，状态码 {1}：{2} ").format(
                        exc.response.url,
                        exc.response.status_code,
                        exc.response.text,
                    )
                )

    def gen_odin_tt(self):
        """
        生成请求必带的odin_tt (Generate the essential odin_tt for requests)
        """

        try:
                response = self.client.get(self.odin_tt_conf["url"])
                response.raise_for_status()

                odin_tt = httpx.Cookies(response.cookies).get("odin_tt")

                if odin_tt is None:
                    raise APIResponseError(_("{0} 内容不符合要求").format("odin_tt"))

                return odin_tt

            # 捕获所有与 httpx 请求相关的异常情况 (Captures all httpx request-related exceptions)
        except httpx.TimeoutException as exc:
                raise APITimeoutError(
                    _(
                        "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                    ).format(
                        _("请求端点超时"),
                        self.odin_tt_conf["url"],
                        ClientConfManager.proxies(),
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
                        self.odin_tt_conf["url"],
                        ClientConfManager.proxies(),
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
                        self.odin_tt_conf["url"],
                        ClientConfManager.proxies(),
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
                        self.odin_tt_conf["url"],
                        ClientConfManager.proxies(),
                        self.__class__.__name__,
                        exc,
                    )
                )

        except httpx.HTTPStatusError as exc:
                # 捕获 httpx 的状态代码错误 (captures specific status code errors from httpx)
                if response.status_code == 401:
                    raise APIUnauthorizedError(
                        _(
                            "参数验证失败，请更新 F2 配置文件中的 {0}，以匹配 {1} 新规则"
                        ).format("odin_tt", "tiktok")
                    )

                elif response.status_code == 404:
                    raise APINotFoundError(_("{0} 无法找到API端点").format("odin_tt"))
                else:
                    raise APIResponseError(
                        _("链接：{0}，状态码 {1}：{2} ").format(
                            exc.response.url,
                            exc.response.status_code,
                            exc.response.text,
                        )
                    )


class XBogusManager:
    @classmethod
    def str_2_endpoint(
        cls,
        user_agent: str,
        endpoint: str,
    ) -> str:
        try:
            final_endpoint = XB(user_agent).getXBogus(endpoint)
        except Exception as e:
            raise RuntimeError(_("生成X-Bogus失败: {0})").format(e))

        return final_endpoint[0]

    @classmethod
    def model_2_endpoint(
        cls,
        user_agent: str,
        base_endpoint: str,
        params: dict,
    ) -> str:
        # 检查params是否是一个字典 (Check if params is a dict)
        if not isinstance(params, dict):
            raise TypeError(_("参数必须是字典类型"))

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])

        try:
            xb_value = XB(user_agent).getXBogus(param_str)
        except Exception as e:
            raise RuntimeError(_("生成X-Bogus失败: {0})").format(e))

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}&X-Bogus={xb_value[1]}"

        return final_endpoint


class SecUserIdFetcher(BaseCrawler):
    """
    SecUserIdFetcher 类用于从 TikTok 用户主页链接中提取用户的 sec_uid 和 unique_id。

    该类继承自 BaseCrawler，利用其中的 aclient 进行 HTTP 请求。主要包含四个方法：
    - get_secuid: 异步类方法，用于获取单个 TikTok 用户的 sec_uid。
    - get_all_secuid: 异步类方法，用于获取多个 TikTok 用户的 sec_uid 列表。
    - get_uniqueid: 异步类方法，用于获取单个 TikTok 用户的 unique_id。
    - get_all_uniqueid: 异步类方法，用于获取多个 TikTok 用户的 unique_id 列表。

    类属性:
    - _TIKTOK_SECUID_PARREN: 编译后的正则表达式，用于匹配 sec_uid。
    - _TIKTOK_UNIQUEID_PARREN: 编译后的正则表达式，用于匹配 unique_id。
    - _TIKTOK_NOTFOUND_PARREN: 编译后的正则表达式，用于检查页面是否不存在。
    - proxies: 从 ClientConfManager 获取的代理配置。

    方法:
    - __init__: 初始化 SecUserIdFetcher 实例，并调用父类的初始化方法。
    - get_secuid: 异步类方法，接受一个用户主页链接，返回对应用户的 sec_uid。
    - get_all_secuid: 异步类方法，接受一个用户主页链接列表，返回对应用户的 sec_uid 列表。
    - get_uniqueid: 异步类方法，接受一个用户主页链接，返回对应用户的 unique_id。
    - get_all_uniqueid: 异步类方法，接受一个用户主页链接列表，返回对应用户的 unique_id 列表。

    异常处理:
    - 在 HTTP 请求过程中，处理可能出现的 TimeoutException、NetworkError、ProtocolError、ProxyError 和 HTTPStatusError 异常，并记录相应的错误信息。

    使用示例:
        # 获取单个用户的 sec_uid
        url = "https://www.tiktok.com/@someuser"
        sec_uid = await SecUserIdFetcher.get_secuid(url)

        # 获取多个用户的 sec_uid 列表
        urls = [
            "https://www.tiktok.com/@user1",
            "https://www.tiktok.com/@user2",
            "https://www.tiktok.com/@user3"
        ]
        sec_uids = await SecUserIdFetcher.get_all_secuid(urls)

        # 获取单个用户的 unique_id
        unique_id = await SecUserIdFetcher.get_uniqueid(url)

        # 获取多个用户的 unique_id 列表
        unique_ids = await SecUserIdFetcher.get_all_uniqueid(urls)
    """

    _TIKTOK_SECUID_PARREN = re.compile(
        r"<script id=\"__UNIVERSAL_DATA_FOR_REHYDRATION__\" type=\"application/json\">(.*?)</script>"
    )
    _TIKTOK_UNIQUEID_PARREN = re.compile(r"/@([^/?]*)")
    _TIKTOK_NOTFOUND_PARREN = re.compile(r"notfound")

    proxies = ClientConfManager.proxies()

    def __init__(self):
        super().__init__(proxies=self.proxies)

    @classmethod
    async def get_secuid(cls, url: str) -> str:
        """
        获取TikTok用户sec_uid。

        Args:
            url: 用户主页链接

        Returns:
            sec_uid: 用户唯一标识

        Raises:
            TypeError: 如果输入的 URL 不是字符串。
            APINotFoundError: 如果输入的 URL 不合法或页面不可用。
            APIResponseError: 如果在响应中未找到 sec_uid。
            ConnectionError: 如果接口状态码异常。
            APITimeoutError: 如果请求端点超时。
            APIConnectionError: 如果网络连接失败。
            APIUnauthorizedError: 如果请求协议错误。
        """

        if not isinstance(url, str):
            raise TypeError("输入参数必须是字符串")

        url = extract_valid_urls(url)

        if url is None:
            raise APINotFoundError("输入的URL不合法。类名：{0}".format(cls.__name__))

        # 创建一个实例以访问 aclient
        instance = cls()

        try:
            response = await instance.aclient.get(url, follow_redirects=True)
            if response.status_code in {200, 444}:
                if cls._TIKTOK_NOTFOUND_PARREN.search(str(response.url)):
                    raise APINotFoundError(
                        "页面不可用，可能是由于区域限制（代理）造成的。"
                    )

                match = cls._TIKTOK_SECUID_PARREN.search(str(response.text))
                if not match:
                    raise APIResponseError(
                        _(
                            "未在响应中找到 {0}，检查链接是否为用户主页。类名：{1}"
                        ).format("sec_uid", cls.__name__)
                    )

                data = json.loads(match.group(1))
                default_scope = data.get("__DEFAULT_SCOPE__", {})
                user_detail = default_scope.get("webapp.user-detail", {})
                user_info = user_detail.get("userInfo", {}).get("user", {})
                sec_uid = user_info.get("secUid")

                if sec_uid is None:
                    raise RuntimeError(_("获取 {0} 失败").format("sec_uid"))

                return sec_uid
            else:
                raise ConnectionError("接口状态码异常，请检查重试")

        except httpx.TimeoutException as exc:
            logger.error(traceback.format_exc())
            raise APITimeoutError(
                "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}".format(
                    "请求端点超时", url, cls.proxies, cls.__name__, exc
                )
            )

        except httpx.NetworkError as exc:
            logger.error(traceback.format_exc())
            raise APIConnectionError(
                "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}".format(
                    "网络连接失败，请检查当前网络环境",
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProtocolError as exc:
            logger.error(traceback.format_exc())
            raise APIUnauthorizedError(
                "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}".format(
                    "请求协议错误", url, cls.proxies, cls.__name__, exc
                )
            )

        except httpx.ProxyError as exc:
            logger.error(traceback.format_exc())
            raise APIConnectionError(
                "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}".format(
                    "请求代理错误", url, cls.proxies, cls.__name__, exc
                )
            )

        except httpx.HTTPStatusError as exc:
            logger.error(traceback.format_exc())
            raise APIResponseError(
                "{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}".format(
                    "状态码错误", url, cls.proxies, cls.__name__, exc
                )
            )

    @classmethod
    async def get_all_secuid(cls, urls: list) -> list:
        """
        获取多个TikTok用户的sec_uid。

        Args:
            urls: 用户主页链接列表

        Returns:
            secuids: 用户sec_uid列表

        Raises:
            TypeError: 如果输入的 URL 列表不是列表类型。
            APINotFoundError: 如果输入的 URL 列表不合法。
        """

        if not isinstance(urls, list):
            raise TypeError("参数必须是列表类型")

        urls = extract_valid_urls(urls)

        if urls == []:
            raise APINotFoundError(
                "输入的URL List不合法。类名：{0}".format(cls.__name__)
            )

        secuids = [cls.get_secuid(url) for url in urls]
        return await asyncio.gather(*secuids)

    @classmethod
    async def get_uniqueid(cls, url: str) -> str:
        """
        获取TikTok用户unique_id。

        Args:
            url: 用户主页链接

        Returns:
            unique_id: 用户唯一标识

        Raises:
            TypeError: 如果输入的 URL 不是字符串。
            APINotFoundError: 如果输入的 URL 不合法或页面不可用。
            APIResponseError: 如果在响应中未找到 unique_id。
            ConnectionError: 如果接口状态码异常。
            APITimeoutError: 如果请求端点超时。
            APIConnectionError: 如果网络连接失败。
            APIUnauthorizedError: 如果请求协议错误。
        """

        if not isinstance(url, str):
            raise TypeError("输入参数必须是字符串")

        url = extract_valid_urls(url)

        if url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))

        # 创建一个实例以访问 aclient
        instance = cls()

        try:
            response = await instance.aclient.get(url, follow_redirects=True)
            if response.status_code in {200, 444}:
                if cls._TIKTOK_NOTFOUND_PARREN.search(str(response.url)):
                    raise APINotFoundError(
                        "页面不可用，可能是由于区域限制（代理）造成的。"
                    )

                match = cls._TIKTOK_UNIQUEID_PARREN.search(str(response.url))
                if not match:
                    raise APIResponseError(_("未在响应中找到 {0}").format("unique_id"))

                unique_id = match.group(1)

                if unique_id is None:
                    raise RuntimeError(
                        _("获取 {0} 失败，{1}").format("unique_id", response.url)
                    )

                return unique_id

            else:
                raise ConnectionError("接口状态码异常，请检查重试")

        except httpx.TimeoutException as exc:
            logger.error(traceback.format_exc())
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    "请求端点超时",
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.NetworkError as exc:
            logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    "网络连接失败，请检查当前网络环境",
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProtocolError as exc:
            logger.error(traceback.format_exc())
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    "请求协议错误",
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProxyError as exc:
            logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    "请求代理错误",
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.HTTPStatusError as exc:
            logger.error(traceback.format_exc())
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    "状态码错误",
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

    @classmethod
    async def get_all_uniqueid(cls, urls: list) -> list:
        """
        获取多个TikTok用户的unique_id。

        Args:
            urls: 用户主页链接列表

        Returns:
            unique_ids: 用户unique_id列表

        Raises:
            TypeError: 如果输入的 URL 列表不是列表类型。
            APINotFoundError: 如果输入的 URL 列表不合法。
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        urls = extract_valid_urls(urls)

        if urls == []:
            raise APINotFoundError(
                _("输入的URL List不合法。类名：{0}").format(cls.__name__)
            )

        unique_ids = [cls.get_uniqueid(url) for url in urls]
        return await asyncio.gather(*unique_ids)


class AwemeIdFetcher(BaseCrawler):
    """
    AwemeIdFetcher 类用于从 TikTok 视频链接中提取视频的 aweme_id。

    该类继承自 BaseCrawler，利用其中的 aclient 进行 HTTP 请求。主要包含两个方法：
    - get_aweme_id: 异步类方法，用于获取单个 TikTok 视频的 aweme_id。
    - get_all_aweme_id: 异步类方法，用于获取多个 TikTok 视频的 aweme_id 列表。

    类属性:
    - _TIKTOK_AWEMEID_PARREN: 编译后的正则表达式，用于匹配 aweme_id。
    - _TIKTOK_NOTFOUND_PARREN: 编译后的正则表达式，用于检查页面是否不存在。
    - proxies: 从 ClientConfManager 获取的代理配置。

    方法:
    - __init__: 初始化 AwemeIdFetcher 实例，并调用父类的初始化方法。
    - get_aweme_id: 异步类方法，接受一个视频链接，返回对应视频的 aweme_id。
    - get_all_aweme_id: 异步类方法，接受一个视频链接列表，返回对应视频的 aweme_id 列表。

    异常处理:
    - 在 HTTP 请求过程中，处理可能出现的 TimeoutException、NetworkError、ProtocolError、ProxyError 和 HTTPStatusError 异常，并记录相应的错误信息。

    使用示例:
        # 获取单个视频的 aweme_id
        url = "https://www.tiktok.com/@scarlettjonesuk/video/7255716763118226715"
        aweme_id = await AwemeIdFetcher.get_aweme_id(url)

        # 获取多个视频的 aweme_id 列表
        urls = [
            "https://www.tiktok.com/@scarlettjonesuk/video/7255716763118226715",
            "https://www.tiktok.com/@scarlettjonesuk/video/7255716763118226715?is_from_webapp=1&sender_device=pc&web_id=7306060721837852167"
        ]
        aweme_ids = await AwemeIdFetcher.get_all_aweme_id(urls)
    """

    _TIKTOK_AWEMEID_PARREN = re.compile(r"video/(\d*)")
    _TIKTOK_NOTFOUND_PARREN = re.compile(r"notfound")

    proxies = ClientConfManager.proxies()

    def __init__(self):
        super().__init__(proxies=self.proxies)

    @classmethod
    async def get_aweme_id(cls, url: str) -> str:
        """
        获取TikTok作品aweme_id。

        Args:
            url: 作品链接

        Returns:
            aweme_id: 作品唯一标识

        Raises:
            TypeError: 如果输入的 URL 不是字符串。
            APINotFoundError: 如果输入的 URL 不合法或页面不可用。
            APIResponseError: 如果在响应中未找到 aweme_id。
            ConnectionError: 如果接口状态码异常。
            APITimeoutError: 如果请求端点超时。
            APIConnectionError: 如果网络连接失败。
            APIUnauthorizedError: 如果请求协议错误。
        """

        if not isinstance(url, str):
            raise TypeError("输入参数必须是字符串")

        url = extract_valid_urls(url)

        if url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))

        # 创建一个实例以访问 aclient
        instance = cls()

        try:
            response = await instance.aclient.get(url, follow_redirects=True)
            if response.status_code in {200, 444}:
                if cls._TIKTOK_NOTFOUND_PARREN.search(str(response.url)):
                    raise APINotFoundError(
                        "页面不可用，可能是由于区域限制（代理）造成的。类名：{0}".format(
                            cls.__name__
                        )
                    )

                match = cls._TIKTOK_AWEMEID_PARREN.search(str(response.url))
                if not match:
                    raise APIResponseError(
                        _("未在响应中找到 {0}，请检查链接。类名：{1}").format(
                            "aweme_id", cls.__name__
                        )
                    )

                aweme_id = match.group(1)

                if aweme_id is None:
                    raise RuntimeError(
                        _("获取 {0} 失败，{1}").format("aweme_id", response.url)
                    )

                return aweme_id
            else:
                raise ConnectionError(
                    _("接口状态码异常 {0}，请检查重试").format(response.status_code)
                )

        except httpx.TimeoutException as exc:
            logger.error(traceback.format_exc())
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求端点超时"),
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.NetworkError as exc:
            logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("网络连接失败，请检查当前网络环境"),
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProtocolError as exc:
            logger.error(traceback.format_exc())
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求协议错误"),
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProxyError as exc:
            logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求代理错误"),
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.HTTPStatusError as exc:
            logger.error(traceback.format_exc())
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("状态码错误"),
                    url,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

    @classmethod
    async def get_all_aweme_id(cls, urls: list) -> list:
        """
        获取多个TikTok视频的aweme_id。

        Args:
            urls: 视频链接列表

        Returns:
            aweme_ids: 视频的唯一标识列表

        Raises:
            TypeError: 如果输入的 URL 列表不是列表类型。
            APINotFoundError: 如果输入的 URL 列表不合法。
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        urls = extract_valid_urls(urls)

        if urls == []:
            raise APINotFoundError(
                _("输入的URL List不合法。类名：{0}").format(cls.__name__)
            )

        aweme_ids = [cls.get_aweme_id(url) for url in urls]
        return await asyncio.gather(*aweme_ids)


def format_file_name(
    naming_template: str,
    aweme_data: dict = {},
    custom_fields: dict = {},
) -> str:
    """
    根据配置文件的全局格式化文件名
    (Format file name according to the global conf file)

    Args:
        aweme_data (dict): 抖音数据的字典 (dict of douyin data)
        naming_template (str): 文件的命名模板, 如 "{create}_{desc}" (Naming template for files, such as "{create}_{desc}")
        custom_fields (dict): 用户自定义字段, 用于替代默认的字段值 (Custom fields for replacing default field values)

    Note:
        windows 文件名长度限制为 255 个字符, 开启了长文件名支持后为 32,767 个字符
        (Windows file name length limit is 255 characters, 32,767 characters after long file name support is enabled)
        Unix 文件名长度限制为 255 个字符
        (Unix file name length limit is 255 characters)
        取去除后的50个字符, 加上后缀, 一般不会超过255个字符
        (Take the removed 50 characters, add the suffix, and generally not exceed 255 characters)
        详细信息请参考: https://en.wikipedia.org/wiki/Filename#Length
        (For more information, please refer to: https://en.wikipedia.org/wiki/Filename#Length)

    Returns:
        str: 格式化的文件名 (Formatted file name)
    """

    # 为不同系统设置不同的文件名长度限制
    os_limit = {
        "win32": 200,
        "cygwin": 60,
        "darwin": 60,
        "linux": 60,
    }

    fields = {
        "create": aweme_data.get("createTime", ""),  # 长度固定19
        "nickname": aweme_data.get("nickname", ""),  # 最长30
        "uniqueId": aweme_data.get("uniqueId", ""),
        "aweme_id": aweme_data.get("aweme_id", ""),  # 长度固定19
        "desc": split_filename(aweme_data.get("desc", ""), os_limit),
        "uid": aweme_data.get("uid", ""),  # 固定11
    }

    if custom_fields:
        # 更新自定义字段
        fields.update(custom_fields)

    try:
        return naming_template.format(**fields)
    except KeyError as e:
        raise KeyError(_("文件名模板字段 {0} 不存在，请检查").format(e))


def create_user_folder(kwargs: dict, uniqueId: Union[str, int]) -> Path:
    """
    根据提供的配置文件和uniqueId，创建对应的保存目录。
    (Create the corresponding save directory according to the provided conf file and uniqueId.)

    Args:
        kwargs (dict): 配置文件，字典格式。(Conf file, dict format)
        uniqueId (Union[str, int]): 用户的uniqueId，允许字符串或整数。  (User uniqueId, allow strings or integers)

    Note:
        如果未在配置文件中指定路径，则默认为 "Download"。
        (If the path is not specified in the conf file, it defaults to "Download".)
        仅支持相对路径。
        (Only relative paths are supported.)

    Raises:
        TypeError: 如果 kwargs 不是字典格式，将引发 TypeError。
        (If kwargs is not in dict format, TypeError will be raised.)
    """

    # 确定函数参数是否正确
    if not isinstance(kwargs, dict):
        raise TypeError("kwargs 参数必须是字典")

    # 创建基础路径
    base_path = Path(kwargs.get("path", "Download"))

    # 添加下载模式和用户名
    user_path = (
        base_path / "tiktok" / kwargs.get("mode", "PLEASE_SETUP_MODE") / str(uniqueId)
    )

    # 获取绝对路径并确保它存在
    resolve_user_path = user_path.resolve()

    # 创建目录
    resolve_user_path.mkdir(parents=True, exist_ok=True)

    return resolve_user_path


def rename_user_folder(old_path: Path, new_uniqueId: str) -> Path:
    """
    重命名用户目录 (Rename User Folder).

    Args:
        old_path (Path): 旧的用户目录路径 (Path of the old user folder)
        new_uniqueId (str): 新的用户uniqueId (New user uniqueId)

    Returns:
        Path: 重命名后的用户目录路径 (Path of the renamed user folder)
    """
    # 获取目标目录的父目录 (Get the parent directory of the target folder)
    parent_directory = old_path.parent

    # 构建新目录路径 (Construct the new directory path)
    new_path = old_path.rename(parent_directory / new_uniqueId).resolve()

    return new_path


def create_or_rename_user_folder(
    kwargs: dict, local_user_data: dict, current_uniqueId: str
) -> Path:
    """
    创建或重命名用户目录 (Create or rename user directory)

    Args:
        kwargs (dict): 配置参数 (Conf parameters)
        local_user_data (dict): 本地用户数据 (Local user data)
        current_uniqueId (str): 当前用户uniqueId (Current user uniqueId)

    Returns:
        user_path (Path): 用户目录路径 (User directory path)
    """
    user_path = create_user_folder(kwargs, current_uniqueId)

    if not local_user_data:
        return user_path

    if local_user_data.get("uniqueId") != current_uniqueId:
        # uniqueId不一致，触发目录更新操作
        user_path = rename_user_folder(user_path, current_uniqueId)

    return user_path

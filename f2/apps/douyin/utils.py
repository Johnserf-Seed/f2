# path: f2/apps/douyin/utils.py

import f2
import re
import json
import time
import httpx
import qrcode
import random
import asyncio
import warnings
import traceback

from typing import Union
from pathlib import Path
from urllib.parse import urlparse

from f2.apps.douyin.algorithm.webcast_signature import DouyinWebcastSignature
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.xbogus import XBogus as XB
from f2.utils.abogus import ABogus as AB, BrowserFingerprintGenerator as BrowserFpGen
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

    client_conf = ConfigManager(f2.F2_CONFIG_FILE_PATH).get_config("f2")
    douyin_conf = client_conf.get("douyin", {})

    @classmethod
    def client(cls) -> dict:
        return cls.douyin_conf

    @classmethod
    def conf_version(cls) -> str:
        return cls.client_conf.get("version", "unknown")

    @classmethod
    def encryption(cls) -> dict:
        return cls.client().get("encryption", "ab")

    @classmethod
    def base_request_model(cls) -> dict:
        return cls.client().get("BaseRequestModel", {})

    @classmethod
    def base_live_model(cls) -> dict:
        return cls.client().get("BaseLiveModel", {})

    @classmethod
    def brm_version(cls) -> dict:
        return cls.base_request_model().get("version", {})

    @classmethod
    def brm_browser(cls) -> dict:
        return cls.base_request_model().get("browser", {})

    @classmethod
    def brm_engine(cls) -> dict:
        return cls.base_request_model().get("engine", {})

    @classmethod
    def brm_os(cls) -> dict:
        return cls.base_request_model().get("os", {})

    @classmethod
    def blm_language(cls) -> str:
        return cls.base_live_model().get("language", "")

    @classmethod
    def blm_browser(cls) -> dict:
        return cls.base_live_model().get("browser", {})

    @classmethod
    def proxies(cls) -> dict:
        return cls.client().get("proxies", {})

    @classmethod
    def headers(cls) -> dict:
        return cls.client().get("headers", {})

    @classmethod
    def wss(cls) -> dict:
        return cls.client().get("wss", {})

    @classmethod
    def user_agent(cls) -> str:
        return cls.headers().get("User-Agent", "")

    @classmethod
    def referer(cls) -> str:
        return cls.headers().get("Referer", "")

    @classmethod
    def msToken(cls) -> dict:
        return cls.client().get("msToken", {})

    @classmethod
    def ttwid(cls) -> dict:
        return cls.client().get("ttwid", {})

    @classmethod
    def webid(cls) -> dict:
        return cls.client().get("webid", {})


class TokenManager(BaseCrawler):
    """
    TokenManager 类用于生成和管理与抖音相关的 token，包括 msToken 和 ttwid。

    该类继承自 BaseCrawler，利用其中的 HTTP 客户端来发送请求。

    类属性:
    - token_conf: 配置 msToken 的相关信息。
    - ttwid_conf: 配置 ttwid 的相关信息。
    - proxies: 代理配置。
    - user_agent: 用户代理字符串。
    - mstoken_headers: 生成 msToken 的请求头。
    - ttwid_headers: 生成 ttwid 的请求头。

    类方法:
    - __init__: 初始化 TokenManager 实例，并调用父类的初始化方法。
    - gen_real_msToken: 类方法，生成真实的 msToken，当出现错误时返回虚假的值。
    - gen_false_msToken: 类方法，生成随机 msToken。
    - gen_ttwid: 类方法，生成请求必带的 ttwid。

    异常处理:
    - 在 HTTP 请求过程中，处理可能出现的 TimeoutException、NetworkError、ProtocolError、ProxyError 和 HTTPStatusError 异常，并记录相应的错误信息。

    使用示例:
    ```python
        # 生成真实的 msToken
        msToken = TokenManager.gen_real_msToken()

        # 生成虚假的 msToken
        false_msToken = TokenManager.gen_false_msToken()

        # 生成 ttwid
        ttwid = TokenManager.gen_ttwid()

        # 生成 webid
        webid = TokenManager.gen_webid()
    ```
    """

    token_conf = ClientConfManager.msToken()
    ttwid_conf = ClientConfManager.ttwid()
    webid_conf = ClientConfManager.webid()
    proxies = ClientConfManager.proxies()
    user_agent = ClientConfManager.user_agent()
    mstoken_headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": user_agent,
    }
    ttwid_headers = {
        "User-Agent": user_agent,
        "Content-Type": "application/json; charset=utf-8",
    }
    webid_headers = {
        "User-Agent": user_agent,
        "Content-Type": "application/json; charset=UTF-8",
        "Referer": "https://www.douyin.com/",
    }

    def __init__(self):
        super().__init__(proxies=self.proxies)

    @classmethod
    def gen_real_msToken(cls) -> str:
        """
        生成真实的 msToken。

        Returns:
            str: 生成的 msToken。

        Raises:
            APITimeoutError: 请求超时错误。
            APIConnectionError: 网络连接错误。
            APIUnauthorizedError: 请求协议错误。
            APIResponseError: 状态码错误或响应内容不符合要求。
        """

        instance = cls()

        try:
            payload = json.dumps(
                {
                    "magic": instance.token_conf["magic"],
                    "version": instance.token_conf["version"],
                    "dataType": instance.token_conf["dataType"],
                    "strData": instance.token_conf["strData"],
                    "ulr": instance.token_conf["ulr"],
                    "tspFromClient": get_timestamp(),
                }
            )
            response = instance.client.post(
                instance.token_conf["url"],
                content=payload,
                headers=instance.mstoken_headers,
            )
            response.raise_for_status()

            msToken = str(httpx.Cookies(response.cookies).get("msToken"))
            if len(msToken) not in [164, 184]:
                raise APIResponseError(_("{0} 内容不符合要求").format("msToken"))

            logger.debug(_("生成真实的msToken"))
            return msToken

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求端点超时"),
                    instance.token_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.NetworkError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("网络连接失败，请检查当前网络环境"),
                    instance.token_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProtocolError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求协议错误"),
                    instance.token_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProxyError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求代理错误"),
                    instance.token_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.HTTPStatusError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("状态码错误"),
                    instance.token_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

    @classmethod
    def gen_false_msToken(cls) -> str:
        """生成随机 msToken (Generate random msToken)"""
        false_msToken = gen_random_str(182) + "=="
        logger.debug(_("生成虚假的 msToken：{0}").format(false_msToken))
        return false_msToken

    @classmethod
    def gen_ttwid(cls) -> str:
        """
        生成请求必带的 ttwid。

        Returns:
            str: 生成的 ttwid。

        Raises:
            APITimeoutError: 请求超时错误。
            APIConnectionError: 网络连接错误。
            APIUnauthorizedError: 请求协议错误。
            APIResponseError: 状态码错误或响应内容不符合要求。
        """

        instance = cls()

        try:
            response = instance.client.post(
                instance.ttwid_conf["url"],
                content=instance.ttwid_conf["data"],
                headers=instance.ttwid_headers,
            )
            response.raise_for_status()

            ttwid = httpx.Cookies(response.cookies).get("ttwid")

            if ttwid is None:
                raise APIResponseError(
                    _("ttwid: 检查没有通过, 请更新配置文件中的 ttwid")
                )

            return ttwid

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求端点超时"),
                    instance.ttwid_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.NetworkError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("网络连接失败，请检查当前网络环境"),
                    instance.ttwid_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProtocolError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求协议错误"),
                    instance.ttwid_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProxyError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求代理错误"),
                    instance.ttwid_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.HTTPStatusError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("状态码错误"),
                    instance.ttwid_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

    @classmethod
    def gen_webid(cls) -> str:
        """
        生成个性化追踪webid (Generate personalized tracking webid)

        Returns:
            str: 生成的webid (Generated webid)

        Raises:
            APITimeoutError: 请求超时错误 (Request timeout error)
            APIConnectionError: 网络连接错误 (Network connection error)
            APIUnauthorizedError: 请求协议错误 (Request protocol error)
            APIResponseError: 状态码错误或响应内容不符合要求 (Status code error or response content does not meet the requirements)
        """

        instance = cls()

        body = json.dumps(
            {
                "app_id": instance.webid_conf["body"]["app_id"],
                "referer": instance.webid_conf["body"]["referer"],
                "url": instance.webid_conf["body"]["url"],
                "user_agent": instance.webid_conf["body"]["user_agent"],
                "user_unique_id": "",
            }
        )

        try:
            response = instance.client.post(
                instance.webid_conf["url"],
                content=body,
                headers=instance.webid_headers,
            )
            response.raise_for_status()

            webid = response.json().get("web_id")
            if not webid:
                raise APIResponseError(_("{0} 内容不符合要求").format("webid"))

            return webid

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求端点超时"),
                    instance.webid_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.NetworkError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("网络连接失败，请检查当前网络环境"),
                    instance.webid_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProtocolError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求协议错误"),
                    instance.webid_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProxyError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求代理错误"),
                    instance.webid_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.HTTPStatusError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("状态码错误"),
                    instance.webid_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )


class VerifyFpManager:
    @classmethod
    def gen_verify_fp(cls) -> str:
        """
        生成verifyFp 与 s_v_web_id (Generate verifyFp)
        """
        base_str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        t = len(base_str)
        milliseconds = int(round(time.time() * 1000))
        base36 = ""
        while milliseconds > 0:
            remainder = milliseconds % 36
            if remainder < 10:
                base36 = str(remainder) + base36
            else:
                base36 = chr(ord("a") + remainder - 10) + base36
            milliseconds = int(milliseconds / 36)
        r = base36
        o = [""] * 36
        o[8] = o[13] = o[18] = o[23] = "_"
        o[14] = "4"

        for i in range(36):
            if not o[i]:
                n = 0 or int(random.random() * t)
                if i == 19:
                    n = 3 & n | 8
                o[i] = base_str[n]

        return "verify_" + r + "_" + "".join(o)

    @classmethod
    def gen_s_v_web_id(cls) -> str:
        return cls.gen_verify_fp()


class WebcastSignatureManager:
    @classmethod
    def model_2_endpoint(
        cls,
        user_agent: str,
        base_endpoint: str,
        params: dict,
    ) -> str:
        warnings.warn(
            _(
                "WebcastSignatureManager.model_2_endpoint 方法已弃用，将在未来版本中移除。"
            ),
            DeprecationWarning,
            stacklevel=2,
        )

        if not isinstance(params, dict):
            raise TypeError(_("参数必须是字典类型"))

        param_str = ",".join([f"{k}={v}" for k, v in params.items()])

        try:
            signature = DouyinWebcastSignature(user_agent).get_signature(param_str)
        except Exception as e:
            trace_logger.error(traceback.format_exc())
            raise RuntimeError(_("生成signature失败: {0})").format(e))

        separator = "&" if "?" in base_endpoint else "?"

        return f"{base_endpoint}{separator}{param_str}&signature={signature}"


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
            trace_logger.error(traceback.format_exc())
            raise RuntimeError(_("生成X-Bogus失败: {0})").format(e))

        return final_endpoint[0]

    @classmethod
    def model_2_endpoint(
        cls,
        user_agent: str,
        base_endpoint: str,
        params: dict,
    ) -> str:
        if not isinstance(params, dict):
            raise TypeError(_("参数必须是字典类型"))

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])

        try:
            xb_value = XB(user_agent).getXBogus(param_str)
        except Exception as e:
            trace_logger.error(traceback.format_exc())
            raise RuntimeError(_("生成X-Bogus失败: {0})").format(e))

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}&X-Bogus={xb_value[1]}"

        return final_endpoint


class ABogusManager:
    @classmethod
    def str_2_endpoint(
        cls,
        user_agent: str,
        params: str,
        request_type: str = "",
    ) -> str:
        try:
            browser_fp = BrowserFpGen.generate_fingerprint("Edge")
            final_endpoint = AB(fp=browser_fp, user_agent=user_agent).generate_abogus(
                params, request_type
            )
        except Exception as e:
            trace_logger.error(traceback.format_exc())
            raise RuntimeError(_("生成A-Bogus失败: {0})").format(e))

        return final_endpoint[0]

    @classmethod
    def model_2_endpoint(
        cls,
        user_agent: str,
        base_endpoint: str,
        params: dict,
        request_type: str = "",
    ) -> str:
        if not isinstance(params, dict):
            raise TypeError(_("参数必须是字典类型"))

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])

        try:
            browser_fp = BrowserFpGen.generate_fingerprint("Edge")
            ab_value = AB(fp=browser_fp, user_agent=user_agent).generate_abogus(
                param_str, request_type
            )
        except Exception as e:
            trace_logger.error(traceback.format_exc())
            raise RuntimeError(_("生成A-Bogus失败: {0})").format(e))

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}&a_bogus={ab_value[1]}"

        return final_endpoint


class SecUserIdFetcher(BaseCrawler):
    """
    SecUserIdFetcher 用于从给定的 URL 中获取 sec_user_id。

    该类继承自 BaseCrawler，并利用其 HTTP 客户端功能来发送请求。

    类属性:
    - _DOUYIN_URL_PATTERN (re.Pattern): 抖音用户主页 URL 的正则表达式模式。
    - _REDIRECT_URL_PATTERN (re.Pattern): 重定向 URL 中 sec_uid 的正则表达式模式。
    - proxies (dict): 代理配置。

    方法:
    - get_sec_user_id: 从单个 URL 中获取 sec_user_id。
    - get_all_sec_user_id: 从 URL 列表中获取所有 sec_user_id。

    异常处理:
    - 在 HTTP 请求过程中，处理可能出现的 TimeoutException、NetworkError、ProtocolError、ProxyError 和 HTTPStatusError 异常，并记录相应的错误信息。

    使用示例:
    ```python
        # 获取单个用户的 sec_user_id
        url = "https://www.douyin.com/user/MS4wLjABAAAAEc8EKgWVEpEQoDRRp8_M53psgc-BoKqre-jICyt6aBA"
        sec_user_id = await SecUserIdFetcher.get_sec_user_id(url)

        # 获取多个用户的 sec_user_id
        urls = [
            "https://www.douyin.com/user/MS4wLjABAAAAEc8EKgWVEpEQoDRRp8_M53psgc-BoKqre-jICyt6aBA",
            "https://v.douyin.com/i2wyU53P/",
        ]
        sec_user_ids = await SecUserIdFetcher.get_all_sec_user_id(urls)
    ```
    """

    _DOUYIN_URL_PATTERN = re.compile(r"user/([^/?]*)")
    _REDIRECT_URL_PATTERN = re.compile(r"sec_uid=([^&]*)")
    proxies = ClientConfManager.proxies()

    def __init__(self):
        super().__init__(proxies=self.proxies)

    @classmethod
    async def get_sec_user_id(cls, url: str) -> str:
        """
        从单个url中获取sec_user_id (Get sec_user_id from a single url)

        Args:
            url (str): 输入的url (Input url)

        Returns:
            str: 匹配到的sec_user_id (Matched sec_user_id)。

        Raises:
            TypeError: 参数不是字符串类型。
            APINotFoundError: 输入的URL不合法。
            APITimeoutError: 请求超时。
            APIConnectionError: 网络连接失败。
            APIUnauthorizedError: 请求协议错误。
            APIResponseError: 未找到sec_user_id或状态码错误。
        """

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        url = extract_valid_urls(url)

        if url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))

        # 解析URL并检查主机
        parsed_url = urlparse(url)
        host = parsed_url.hostname

        if host is None:
            raise APINotFoundError(
                _("无法解析URL的主机部分。类名：{0}".format(cls.__name__))
            )

        pattern = (
            cls._REDIRECT_URL_PATTERN
            if host == "v.douyin.com" or host.endswith(".v.douyin.com")
            else cls._DOUYIN_URL_PATTERN
        )
        # 创建一个实例以访问 aclient
        instance = cls()

        try:
            response = await instance.aclient.get(url, follow_redirects=True)
            if response.status_code in {200, 444}:
                match = pattern.search(str(response.url))
                if match:
                    return match.group(1)
                else:
                    raise APIResponseError(
                        _(
                            "未在响应的地址中找到sec_user_id，检查链接是否为用户主页类名：{0}"
                        ).format(cls.__name__)
                    )
            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求端点超时"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.NetworkError as exc:
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
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求协议错误"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.ProxyError as exc:
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求代理错误"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.HTTPStatusError as exc:
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("状态码错误"), url, cls.proxies, cls.__name__, exc
                )
            )

    @classmethod
    async def get_all_sec_user_id(cls, urls: list) -> list:
        """
        获取列表sec_user_id列表 (Get list sec_user_id list)

        Args:
            urls (list): 用户url列表 (User url list)

        Returns:
            list: 用户sec_user_id列表 (User sec_user_id list)

        Raises:
            TypeError: 参数不是列表类型。
            APINotFoundError: 输入的URL List不合法。
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        if urls == []:
            raise APINotFoundError(
                _("输入的URL List不合法。类名：{0}").format(cls.__name__)
            )

        sec_user_ids = [cls.get_sec_user_id(url) for url in urls]
        return await asyncio.gather(*sec_user_ids)


class AwemeIdFetcher(BaseCrawler):
    """
    AwemeIdFetcher 用于从给定的 URL 中获取 aweme_id。

    该类继承自 BaseCrawler，并利用其 HTTP 客户端功能来发送请求。

    类属性:
    - _DOUYIN_VIDEO_URL_PATTERN (re.Pattern): 抖音视频 URL 的正则表达式模式。
    - _DOUYIN_NOTE_URL_PATTERN (re.Pattern): 抖音笔记 URL 的正则表达式模式。
    - proxies (dict): 代理配置。

    方法:
    - get_aweme_id: 从单个 URL 中获取 aweme_id。
    - get_all_aweme_id: 从 URL 列表中获取所有 aweme_id。

    异常处理:
    - 在 HTTP 请求过程中，处理可能出现的 TimeoutException、NetworkError、ProtocolError、ProxyError 和 HTTPStatusError 异常，并记录相应的错误信息。

    使用示例:
    ```python
        # 获取单个作品的 aweme_id
        url = "https://www.douyin.com/video/6969696969696969696"
        aweme_id = await AwemeIdFetcher.get_aweme_id(url)

        # 获取多个作品的 aweme_id
        urls = [
            "https://www.douyin.com/video/6969696969696969696",
            "https://www.douyin.com/note/6969696969696969696",
            "https://v.douyin.com/tttttttt/",
        ]
        aweme_ids = await AwemeIdFetcher.get_all_aweme_id(urls)
    ```
    """

    _DOUYIN_VIDEO_URL_PATTERN = re.compile(r"video/([^/?]*)")
    _DOUYIN_NOTE_URL_PATTERN = re.compile(r"note/([^/?]*)")
    proxies = ClientConfManager.proxies()

    def __init__(self):
        super().__init__(proxies=self.proxies)

    @classmethod
    async def get_aweme_id(cls, url: str) -> str:
        """
        从单个url中获取aweme_id (Get aweme_id from a single url)

        Args:
            url (str): 输入的url (Input url)

        Returns:
            str: 匹配到的aweme_id (Matched aweme_id)。

        Raises:
            TypeError: 参数不是字符串类型。
            APINotFoundError: 输入的URL不合法。
            APITimeoutError: 请求超时。
            APIConnectionError: 网络连接失败。
            APIUnauthorizedError: 请求协议错误。
            APIResponseError: 未找到aweme_id或状态码错误。
        """

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        url = extract_valid_urls(url)

        if url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))

        # 创建一个实例以访问 aclient
        instance = cls()

        try:
            response = await instance.aclient.get(url, follow_redirects=True)
            response.raise_for_status()

            video_pattern = cls._DOUYIN_VIDEO_URL_PATTERN
            note_pattern = cls._DOUYIN_NOTE_URL_PATTERN

            match = video_pattern.search(str(response.url))
            if match:
                aweme_id = match.group(1)
            elif match := note_pattern.search(str(response.url)):
                aweme_id = match.group(1)
            else:
                raise APIResponseError(
                    _(
                        "未在响应的地址中找到aweme_id，当前链接暂时不支持。类名：{0}"
                    ).format(cls.__name__)
                )

            return aweme_id

        except httpx.TimeoutException as exc:
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求端点超时"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.NetworkError as exc:
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
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求协议错误"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.ProxyError as exc:
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求代理错误"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.HTTPStatusError as exc:
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("状态码错误"), url, cls.proxies, cls.__name__, exc
                )
            )

    @classmethod
    async def get_all_aweme_id(cls, urls: list) -> list:
        """
        获取视频aweme_id,传入列表url都可以解析出aweme_id (Get video aweme_id, pass in the list url can parse out aweme_id)

        Args:
            urls (list): 列表url (list url)

        Returns:
            list: 视频的唯一标识，返回列表 (The unique identifier of the video, return list)

        Raises:
            TypeError: 参数不是列表类型。
            APINotFoundError: 输入的URL List不合法。
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        if urls == []:
            raise APINotFoundError(
                _("输入的URL List不合法。类名：{0}").format(cls.__name__)
            )

        aweme_ids = [cls.get_aweme_id(url) for url in urls]
        return await asyncio.gather(*aweme_ids)


class MixIdFetcher(BaseCrawler):
    """
    MixIdFetcher 用于从给定的 URL 中获取 mix_id。

    该类继承自 BaseCrawler，并利用其 HTTP 客户端功能来发送请求。

    类属性:
    - _DOUYIN_MIX_URL_PATTERN (re.Pattern): 抖音合集 URL 的正则表达式模式。
    - proxies (dict): 代理配置。

    方法:
    - get_mix_id: 从单个 URL 中获取 mix_id。
    - get_all_mix_id: 从 URL 列表中获取所有 mix_id。

    异常处理:
    - 在 HTTP 请求过程中，处理可能出现的 TimeoutException、NetworkError、ProtocolError、ProxyError 和 HTTPStatusError 异常，并记录相应的错误信息。

    使用示例:
    ```python
        # 获取单个合集的 mix_id
        url = "https://www.douyin.com/collection/7360898383181809676"
        mix_id = await MixIdFetcher.get_mix_id(url)

        # 获取多个合集的 mix_id
        urls = [
            "https://www.douyin.com/collection/6812345678901234567",
            "https://www.douyin.com/collection/6812345678901234568",
        ]
        mix_ids = await MixIdFetcher.get_all_mix_id(urls)
    ```
    """

    _DOUYIN_MIX_URL_PATTERN = re.compile(r"collection/([^/?]*)")
    proxies = ClientConfManager.proxies()

    def __init__(self):
        super().__init__(proxies=self.proxies)

    @classmethod
    async def get_mix_id(cls, url: str) -> str:
        """
        从单个url中获取mix_id (Get mix_id from a single url)

        Args:
            url (str): 输入的url (Input url)

        Returns:
            str: 匹配到的mix_id (Matched mix_id)。

        Raises:
            TypeError: 参数不是字符串类型。
            APINotFoundError: 输入的URL不合法。
            APITimeoutError: 请求超时。
            APIConnectionError: 网络连接失败。
            APIUnauthorizedError: 请求协议错误。
            APIResponseError: 未找到mix_id或状态码错误。
        """

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        url = extract_valid_urls(url)

        if url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))

        instance = cls()

        try:
            response = await instance.aclient.get(url, follow_redirects=True)
            response.raise_for_status()

            mix_pattern = cls._DOUYIN_MIX_URL_PATTERN

            match = mix_pattern.search(str(response.url))
            if match:
                mix_id = match.group(1)
            else:
                raise APIResponseError(
                    _("未在响应的地址中找到mix_id，检查链接是否为合集页")
                )
            return mix_id

        except httpx.TimeoutException as exc:
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求端点超时"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.NetworkError as exc:
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
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求协议错误"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.ProxyError as exc:
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求代理错误"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.HTTPStatusError as exc:
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("状态码错误"), url, cls.proxies, cls.__name__, exc
                )
            )

    @classmethod
    async def get_all_mix_id(cls, urls: list) -> list:
        """
        获取合集mix_id,传入列表url都可以解析出mix_id (Get video mix_id, pass in the list url can parse out aweme_id)

        Args:
            urls (list): 列表url (list url)

        Returns:
            list: 视频的唯一标识，返回列表 (The unique identifier of the video, return list)

        Raises:
            TypeError: 参数不是列表类型。
            APINotFoundError: 输入的URL List不合法。
        """
        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        if urls == []:
            raise APINotFoundError(
                _("输入的URL List不合法。类名：{0}").format(cls.__name__)
            )

        mix_ids = [cls.get_mix_id(url) for url in urls]
        return await asyncio.gather(*mix_ids)


class WebCastIdFetcher(BaseCrawler):
    """
    WebCastIdFetcher 用于从给定的 URL 中获取 webcast_id。

    该类继承自 BaseCrawler，并利用其 HTTP 客户端功能来发送请求。

    类属性:
    - _DOUYIN_LIVE_URL_PATTERN (re.Pattern): 抖音直播 URL 的正则表达式模式。
    - _DOUYIN_LIVE_URL_PATTERN2 (re.Pattern): 抖音直播 URL 的第二种正则表达式模式。
    - _DOUYIN_ROOM_URL_PATTERN (re.Pattern): 抖音直播 URL 的第三种正则表达式模式。
    - proxies (dict): 代理配置。

    方法:
    - get_webcast_id: 从单个 URL 中获取 webcast_id。
    - get_all_webcast_id: 从 URL 列表中获取所有 webcast_id。
    - get_room_id: 从单个 URL 中获取 room_id。
    - get_all_room_id: 从 URL 列表中获取所有 room_id。

    异常处理:
    - 在 HTTP 请求过程中，处理可能出现的 TimeoutException、NetworkError、ProtocolError、ProxyError 和 HTTPStatusError 异常，并记录相应的错误信息。

    使用示例:
    ```python
        # 获取单个直播的 webcast_id
        url = "https://live.douyin.com/36299127202"
        webcast_id = await WebCastIdFetcher.get_webcast_id(url)

        # 获取多个直播的 webcast_id
        urls = [
            "https://live.douyin.com/36299127202",
            "https://live.douyin.com/36299127202?enter_from_merge=link_share&enter_method=copy_link_share&action_type=click&from=web_code_link",
        ]
        webcast_ids = await WebCastIdFetcher.get_all_webcast_id(urls)

        # 获取单个直播的 room_id (仅APP端分享链接)
        url = "https://v.douyin.com/i8tBR7hX/"
        room_id = await WebCastIdFetcher.get_room_id(url)

        # 获取多个直播的 room_id (仅APP端分享链接)
        urls = [
            'https://webcast.amemv.com/douyin/webcast/reflow/7318296342189919011?u_code=l1j9bkbd&did=MS4wLjABAAAAEs86TBQPNwAo-RGrcxWyCdwKhI66AK3Pqf3ieo6HaxI&iid=MS4wLjABAAAA0ptpM-zzoliLEeyvWOCUt-_dQza4uSjlIvbtIazXnCY&with_sec_did=1&use_link_command=1&ecom_share_track_params=&extra_params={"from_request_id":"20231230162057EC005772A8EAA0199906","im_channel_invite_id":"0"}&user_id=3644207898042206&liveId=7318296342189919011&from=share&style=share&enter_method=click_share&roomId=7318296342189919011&activity_info={}',
            "https://v.douyin.com/i8tBR7hX/",
        ]
        room_ids = await WebCastIdFetcher.get_all_room_id(urls)
    ```
    """

    _DOUYIN_LIVE_URL_PATTERN = re.compile(r"live/([^/?]*)")
    _DOUYIN_LIVE_URL_PATTERN2 = re.compile(r"http[s]?://live.douyin.com/(\d+)")
    _DOUYIN_ROOM_URL_PATTERN = re.compile(r"reflow/([^/?]*)")
    proxies = ClientConfManager.proxies()

    def __init__(self):
        super().__init__(proxies=self.proxies)

    @classmethod
    async def get_webcast_id(cls, url: str) -> str:
        """
        从单个url中获取webcast_id (Get webcast_id from a single url)

        Args:
            url (str): 输入的url (Input url)

        Returns:
            str: 匹配到的webcast_id (Matched webcast_id)。

        Raises:
            TypeError: 参数不是字符串类型。
            APINotFoundError: 输入的URL不合法。
            APITimeoutError: 请求超时。
            APIConnectionError: 网络连接失败。
            APIUnauthorizedError: 请求协议错误。
            APIResponseError: 未找到webcast_id或状态码错误。
        """

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        url = extract_valid_urls(url)

        if url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))

        instance = cls()

        try:
            response = await instance.aclient.get(url, follow_redirects=True)
            response.raise_for_status()
            url = str(response.url)

            live_pattern = cls._DOUYIN_LIVE_URL_PATTERN
            live_pattern2 = cls._DOUYIN_LIVE_URL_PATTERN2
            room_pattern = cls._DOUYIN_ROOM_URL_PATTERN

            if live_pattern.search(url):
                match = live_pattern.search(url)
            elif live_pattern2.search(url):
                match = live_pattern2.search(url)
            # 辅助用户使用新方法，因为大部分第一次使用的用户都不会使用新方法
            elif room_pattern.search(url):
                match = room_pattern.search(url)
                logger.warning(
                    _(
                        "该链接返回的是room_id，请使用`fetch_user_live_videos_by_room_id`接口处理APP端分享链接。"
                    )
                )
            else:
                raise APIResponseError(
                    _("未在响应的地址中找到webcast_id，检查链接是否为直播页")
                )

            return match.group(1)
        except httpx.TimeoutException as exc:
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求端点超时"), url, cls.proxies, cls.__name__, exc)
            )
        except httpx.NetworkError as exc:
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
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求协议错误"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.ProxyError as exc:
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求代理错误"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.HTTPStatusError as exc:
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("状态码错误"), url, cls.proxies, cls.__name__, exc
                )
            )

    @classmethod
    async def get_all_webcast_id(cls, urls: list) -> list:
        """
        获取直播webcast_id,传入列表url都可以解析出webcast_id (Get live webcast_id, pass in the list url can parse out webcast_id)

        Args:
            urls (list): 列表url (list url)

        Returns:
            list: 直播的唯一标识，返回列表 (The unique identifier of the live, return list)

        Raises:
            TypeError: 参数不是列表类型。
            APINotFoundError: 输入的URL List不合法。
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        if urls == []:
            raise APINotFoundError(
                _("输入的URL List不合法。类名：{0}").format(cls.__name__)
            )

        webcast_ids = [cls.get_webcast_id(url) for url in urls]
        return await asyncio.gather(*webcast_ids)

    @classmethod
    async def get_room_id(cls, url: str) -> str:
        """
        从单个url中获取room_id (Get room_id from a single url)

        Args:
            url (str): 输入的url (Input url)

        Returns:
            str: 匹配到的room_id (Matched room_id)。

        Raises:
            TypeError: 参数不是字符串类型。
            APINotFoundError: 输入的URL不合法。
            APITimeoutError: 请求超时。
            APIConnectionError: 网络连接失败。
            APIUnauthorizedError: 请求协议错误。
            APIResponseError: 未找到room_id或状态码错误。
        """

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        url = extract_valid_urls(url)

        if url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))

        instance = cls()

        try:
            response = await instance.aclient.get(url, follow_redirects=True)
            response.raise_for_status()
            url = str(response.url)

            pattern = cls._DOUYIN_ROOM_URL_PATTERN
            match = pattern.search(url)
            if match:
                return match.group(1)
            else:
                raise APIResponseError(
                    _("未在响应的地址中找到room_id，检查链接是否为直播页")
                )

        except httpx.TimeoutException as exc:
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求端点超时"), url, cls.proxies, cls.__name__, exc)
            )
        except httpx.NetworkError as exc:
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
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求协议错误"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.ProxyError as exc:
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(_("请求代理错误"), url, cls.proxies, cls.__name__, exc)
            )

        except httpx.HTTPStatusError as exc:
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("状态码错误"), url, cls.proxies, cls.__name__, exc
                )
            )

    @classmethod
    async def get_all_room_id(cls, urls: list) -> list:
        """
        获取直播room_id,传入列表url都可以解析出room_id (Get live room_id, pass in the list url can parse out room_id)

        Args:
            urls (list): 列表url (list url)

        Returns:
            list: 直播的唯一标识，返回列表 (The unique identifier of the live, return list)

        Raises:
            TypeError: 参数不是列表类型。
            APINotFoundError: 输入的URL List不合法。
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        if urls == []:
            raise APINotFoundError(
                _("输入的URL List不合法。类名：{0}").format(cls.__name__)
            )

        room_ids = [cls.get_room_id(url) for url in urls]
        return await asyncio.gather(*room_ids)


def format_file_name(
    naming_template: str,
    aweme_data: dict = {},
    custom_fields: dict = {},
) -> str:
    """
    根据配置文件的全局格式化文件名
    (Format file name according to the global conf file)

    Args:
        naming_template (str): 文件的命名模板, 如 "{create}_{desc}" (Naming template for files, such as "{create}_{desc}")
        aweme_data (dict): 抖音数据的字典 (dict of douyin data)
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
        "cygwin": 200,
        "darwin": 200,
        "linux": 200,
    }

    fields = {
        "create": aweme_data.get("create_time", ""),  # 长度固定19
        "nickname": aweme_data.get("nickname", ""),  # 最长30
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


def create_user_folder(kwargs: dict, nickname: Union[str, int]) -> Path:
    """
    根据提供的配置文件和昵称，创建对应的保存目录。
    (Create the corresponding save directory according to the provided conf file and nickname.)

    Args:
        kwargs (dict): 配置文件，字典格式。(Conf file, dict format)
        nickname (Union[str, int]): 用户的昵称，允许字符串或整数。  (User nickname, allow strings or integers)

    Note:
        如果未在配置文件中指定路径，则默认为 "Download"。
        (If the path is not specified in the conf file, it defaults to "Download".)
        支持绝对与相对路径。
        (Support absolute and relative paths)

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
        base_path / "douyin" / kwargs.get("mode", "PLEASE_SETUP_MODE") / str(nickname)
    )

    # 获取绝对路径并确保它存在
    resolve_user_path = user_path.resolve()

    # 创建目录
    resolve_user_path.mkdir(parents=True, exist_ok=True)

    return resolve_user_path


def rename_user_folder(old_path: Path, new_nickname: str) -> Path:
    """
    重命名用户目录 (Rename User Folder).

    Args:
        old_path (Path): 旧的用户目录路径 (Path of the old user folder)
        new_nickname (str): 新的用户昵称 (New user nickname)

    Returns:
        Path: 重命名后的用户目录路径 (Path of the renamed user folder)
    """
    # 获取目标目录的父目录 (Get the parent directory of the target folder)
    parent_directory = old_path.parent

    # 构建新目录路径 (Construct the new directory path)
    new_path = old_path.rename(parent_directory / new_nickname).resolve()

    return new_path


def create_or_rename_user_folder(
    kwargs: dict, local_user_data: dict, current_nickname: str
) -> Path:
    """
    创建或重命名用户目录 (Create or rename user directory)

    Args:
        kwargs (dict): 配置参数 (Conf parameters)
        local_user_data (dict): 本地用户数据 (Local user data)
        current_nickname (str): 当前用户昵称 (Current user nickname)

    Returns:
        user_path (Path): 用户目录路径 (User directory path)
    """
    user_path = create_user_folder(kwargs, current_nickname)

    if not local_user_data:
        return user_path

    if local_user_data.get("nickname") != current_nickname:
        # 昵称不一致，触发目录更新操作
        user_path = rename_user_folder(user_path, current_nickname)

    return user_path


def show_qrcode(qrcode_url: str, show_image: bool = False) -> None:
    """
    显示二维码 (Show QR code)

    Args:
        qrcode_url (str): 登录二维码链接 (Login QR code link)
        show_image (bool): 是否显示图像，True 表示显示，False 表示在控制台显示
        (Whether to display the image, True means display, False means display in the console)

    Deprecated:
        show_qrcode() 方法已弃用，将在未来版本中移除。
        (show_qrcode() method is deprecated and will be removed in future versions.)
    """
    warnings.warn(
        _("show_qrcode() 方法已弃用，将在未来版本中移除。"),
        DeprecationWarning,
        stacklevel=2,
    )

    if show_image:
        # 创建并显示QR码图像
        qr_code_img = qrcode.make(qrcode_url)
        qr_code_img.show()
    else:
        # 在控制台以 ASCII 形式打印二维码
        qr = qrcode.QRCode()
        qr.add_data(qrcode_url)
        qr.make(fit=True)
        # 在控制台以 ASCII 形式打印二维码
        qr.print_ascii(invert=True)


def json_2_lrc(data: Union[str, list, dict]) -> str:
    """
    从抖音原声json格式歌词生成lrc格式歌词
    (Generate lrc lyrics format from Douyin original json lyrics format)

    Args:
        data (Union[str, list, dict]): 抖音原声json格式歌词 (Douyin original json lyrics format)

    Returns:
        str: 生成的lrc格式歌词 (Generated lrc format lyrics)
    """
    try:
        lrc_lines = []
        for item in data:
            text = item["text"]
            time_seconds = float(item["timeId"])
            minutes = int(time_seconds // 60)
            seconds = int(time_seconds % 60)
            milliseconds = int((time_seconds % 1) * 1000)
            time_str = f"{minutes:02}:{seconds:02}.{milliseconds:03}"
            lrc_lines.append(f"[{time_str}] {text}")
    except KeyError as e:
        raise KeyError(_("歌词数据字段错误：{0}").format(e))
    except RuntimeError as e:
        raise RuntimeError(_("生成歌词文件失败：{0}，请检查歌词 `data` 内容").format(e))
    except TypeError as e:
        raise TypeError(_("歌词数据类型错误：{0}").format(e))
    return "\n".join(lrc_lines)

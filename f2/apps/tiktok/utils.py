# path: f2/apps/tiktok/utils.py

import asyncio
import json
import re
import time
import traceback
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
from urllib.parse import quote

import httpx

import f2
from f2.crawlers.base_crawler import BaseCrawler
from f2.exceptions.api_exceptions import (
    APIConnectionError,
    APINotFoundError,
    APIResponseError,
    APITimeoutError,
    APIUnauthorizedError,
)
from f2.exceptions.conf_exceptions import InvalidConfError
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.config.conf_manager import ConfigManager
from f2.utils.crypto.bytedance.xbogus import XBogus as XB
from f2.utils.crypto.bytedance.xgnarly import XGnarly
from f2.utils.file.name import split_filename
from f2.utils.file.path import get_user_folder_path, migrate_user_folders
from f2.utils.http.cookie import join_set_cookie_headers, parse_cookie_str
from f2.utils.http.proxy import prefer_proxies
from f2.utils.string.formatter import extract_valid_urls
from f2.utils.string.generator import gen_random_str
from f2.utils.time.timestamp import get_timestamp


class ClientConfManager:
    """
    用于管理客户端配置 (Used to manage client configuration)
    """

    client_conf = ConfigManager(f2.F2_CONFIG_FILE_PATH).get_config("f2")
    tiktok_conf = client_conf.get("tiktok", {})

    @classmethod
    def client(cls) -> dict:
        return cls.tiktok_conf

    @classmethod
    def conf_version(cls) -> str:
        return cls.client_conf.get("version", "unknown")

    @classmethod
    def wss(cls) -> dict:
        return cls.client().get("wss", {})

    @classmethod
    def base_request_model(cls) -> dict:
        return cls.client().get("BaseRequestModel", {})

    @classmethod
    def brm_browser(cls) -> dict:
        return cls.base_request_model().get("browser", {})

    @classmethod
    def brm_device(cls) -> dict:
        return cls.base_request_model().get("device", {})

    @classmethod
    def proxies(cls) -> dict:
        return cls.client().get("proxies", {})

    @classmethod
    def headers(cls) -> dict:
        return cls.client().get("headers", {})

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
    def odin_tt(cls) -> dict:
        return cls.client().get("odin_tt", {})


class TokenManager(BaseCrawler):
    """
    TokenManager 类用于生成和管理 TikTok 请求所需的各种令牌。

    该类继承自 BaseCrawler，利用其中的 client 进行 HTTP 请求。主要包含以下方法：
    - gen_real_msToken: 生成真实的 msToken。
    - cached_msToken: 返回进程内缓存的真实 msToken，首次调用时才生成。
    - gen_false_msToken: 生成虚假的 msToken。
    - gen_ttwid: 生成 ttwid。
    - gen_odin_tt: 生成 odin_tt。

    类属性:
    - token_conf: 从 ClientConfManager 获取的 msToken 配置。
    - ttwid_conf: 从 ClientConfManager 获取的 ttwid 配置（ttwid/check 已不再下发 ttwid，gen_ttwid 不再使用）。
    - odin_tt_conf: 从 ClientConfManager 获取的 odin_tt 配置。
    - proxies: 从 ClientConfManager 获取的代理配置。
    - mstoken_headers: 生成 msToken 请求所需的 HTTP 头信息。
    - ttwid_headers: 生成 ttwid 请求所需的 HTTP 头信息。
    """

    # 首次打开首页时服务器会下发 ttwid
    _TTWID_URL = "https://www.tiktok.com/"

    token_conf = ClientConfManager.msToken()
    ttwid_conf = ClientConfManager.ttwid()
    odin_tt_conf = ClientConfManager.odin_tt()
    proxies = ClientConfManager.proxies()
    user_agent = ClientConfManager.user_agent()
    mstoken_headers = {
        "Content-Type": "application/json",
        "User-Agent": user_agent,
    }
    ttwid_headers = {
        "Cookie": ttwid_conf.get("cookie"),
        "Content-Type": "text/plain",
        "User-Agent": user_agent,
    }
    odin_tt_headers = {
        "Referer": ClientConfManager.referer(),
        "User-Agent": user_agent,
    }
    # 进程内缓存的真实 msToken，由 cached_msToken 按需生成
    _msToken_cache: Optional[str] = None

    def __init__(self):
        super().__init__(proxies=self.proxies)

    @classmethod
    def gen_real_msToken(cls) -> str:
        """
        生成真实的 msToken。

        Returns:
            msToken: 生成的 msToken

        Raises:
            APITimeoutError: 如果请求超时。
            APIConnectionError: 如果网络连接失败。
            APIUnauthorizedError: 如果请求协议错误。
            APIResponseError: 如果响应不符合要求。
        """

        instance = cls()

        try:
            payload = json.dumps(
                {
                    "magic": instance.token_conf["magic"],
                    "version": instance.token_conf["version"],
                    "dataType": instance.token_conf["dataType"],
                    "strData": instance.token_conf["strData"],
                    "tspFromClient": get_timestamp(),
                }
            )
            response = instance.client.post(
                instance.token_conf["url"],
                content=payload,
                headers=instance.mstoken_headers,
            )
            response.raise_for_status()

            msToken = httpx.Cookies(response.cookies).get("msToken")

            # 长度随 SDK 版本变化（2026-09 起为 168，此前为 152），只检查是否下发
            if not msToken:
                raise APIResponseError(_("{0} 内容不符合要求").format("msToken"))

            logger.debug(_("生成真实的 msToken：{0}").format(msToken))
            return msToken

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
            raise APITimeoutError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
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
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
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
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
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
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
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
        finally:
            instance.client.close()

    @classmethod
    def cached_msToken(cls) -> str:
        """
        返回进程内缓存的真实 msToken。

        首次调用时才通过 gen_real_msToken 联网生成，之后复用同一个值；
        请求模型以此作为 msToken 的默认值，因此导入模块不会联网。
        生成失败时不缓存，下一次调用会重新生成。

        Returns:
            str: 真实的 msToken。

        Raises:
            APITimeoutError: 请求超时错误。
            APIConnectionError: 网络连接错误。
            APIUnauthorizedError: 请求协议错误。
            APIResponseError: 状态码错误或响应内容不符合要求。
        """

        if cls._msToken_cache is None:
            cls._msToken_cache = cls.gen_real_msToken()
        return cls._msToken_cache

    @classmethod
    def gen_false_msToken(cls) -> str:
        """
        生成随机的虚假 msToken。

        Returns:
            false_msToken: 生成的虚假 msToken
        """
        false_msToken = gen_random_str(150) + "=="
        logger.debug(_("生成虚假的 msToken：{0}").format(false_msToken))
        return false_msToken

    @classmethod
    def gen_ttwid(cls) -> str:
        """
        生成请求必带的 ttwid：读取打开 TikTok 首页时服务器下发的 cookie。

        Returns:
            ttwid: 生成的 ttwid

        Raises:
            APITimeoutError: 如果请求超时。
            APIConnectionError: 如果网络连接失败。
            APIUnauthorizedError: 如果请求协议错误。
            APIResponseError: 如果响应不符合要求。
        """

        instance = cls()

        try:
            # 2026-09 起 ttwid/check 只做校验、不再下发 ttwid，首次打开首页时才会下发
            response = instance.client.get(
                cls._TTWID_URL,
                headers={"User-Agent": cls.user_agent},
                follow_redirects=True,
            )
            response.raise_for_status()

            ttwid = httpx.Cookies(response.cookies).get("ttwid")

            if ttwid is None:
                raise APIResponseError(_("{0} 生成失败").format("ttwid"))

            logger.debug(_("生成 ttwid：{0}").format(str(ttwid)))
            return str(ttwid)

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
            raise APITimeoutError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("请求端点超时"),
                    cls._TTWID_URL,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.NetworkError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("网络连接失败，请检查当前网络环境"),
                    cls._TTWID_URL,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProtocolError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIUnauthorizedError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("请求协议错误"),
                    cls._TTWID_URL,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProxyError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("请求代理错误"),
                    cls._TTWID_URL,
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
                    cls._TTWID_URL,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )
        finally:
            instance.client.close()

    @classmethod
    def gen_odin_tt(cls) -> str:
        """
        生成 odin_tt。TikTok 已不再向未登录用户下发 odin_tt，拿不到时抛出 APIResponseError。

        Returns:
            odin_tt: 生成的 odin_tt

        Raises:
            APITimeoutError: 如果请求超时。
            APIConnectionError: 如果网络连接失败。
            APIUnauthorizedError: 如果请求协议错误。
            APIResponseError: 如果响应不符合要求。
        """

        instance = cls()

        try:
            response = instance.client.get(
                instance.odin_tt_conf["url"],
                headers=instance.odin_tt_headers,
                follow_redirects=True,
            )
            # response.raise_for_status()

            odin_tt = httpx.Cookies(response.cookies).get("odin_tt")

            # 2026-09 实测游客 cookie 中已没有 odin_tt，只有登录后的 cookie 才有
            if odin_tt is None:
                raise APIResponseError(
                    _(
                        "TikTok 已不再向未登录用户下发 odin_tt，请从登录后的浏览器 cookie 中复制"
                    )
                )

            return odin_tt

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
            raise APITimeoutError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("请求端点超时"),
                    instance.odin_tt_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.NetworkError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("网络连接失败，请检查当前网络环境"),
                    instance.odin_tt_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProtocolError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIUnauthorizedError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("请求协议错误"),
                    instance.odin_tt_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProxyError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("请求代理错误"),
                    instance.odin_tt_conf["url"],
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
                    instance.odin_tt_conf["url"],
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )
        finally:
            instance.client.close()


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
            raise ValueError(_("生成X-Bogus失败: {0})").format(e))

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
            raise ValueError(_("生成X-Bogus失败: {0})").format(e))

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}&X-Bogus={xb_value[1]}"

        return final_endpoint


class XGnarlyManager:
    """
    为 TikTok 网页接口生成签名参数 (Sign TikTok web API requests)

    按网页 SDK 的顺序在业务参数之后追加 X-Dynosaur、msToken、X-Bogus（固定为 1）与 X-Gnarly。
    参数值与网页一样按 RFC 3986 编码（括号、分号、斜杠等都会编码），签名覆盖的就是这串字节，
    签名后不能再重新编码；msToken 只取 cookie 中已有的值，没有时留空，不会伪造，
    伪造的 msToken 会让接口返回空内容。
    """

    @classmethod
    def model_2_endpoint(
        cls,
        user_agent: str,
        base_endpoint: str,
        params: dict,
        cookie: str = "",
    ) -> str:
        """
        返回带签名参数的请求地址 (Return the signed request URL)

        Args:
            user_agent (str): 请求使用的 User-Agent，必须与请求头一致
            base_endpoint (str): 接口地址
            params (dict): 业务参数，按字典顺序拼接
            cookie (str): 请求使用的 cookie，从中读取 msToken

        Returns:
            str: 签名后的请求地址
        """
        # 检查params是否是一个字典 (Check if params is a dict)
        if not isinstance(params, dict):
            raise TypeError(_("参数必须是字典类型"))

        ms_token = parse_cookie_str(cookie or "").get("msToken", "")
        # 2026-09-26 的浏览器抓包中，X-Dynosaur 的查询串哈希对应按 RFC 3986 完整编码的参数值，
        # 编码后的内容只含非保留字符与 %XX，encode_query 不会再改动
        pairs = [
            (str(key), quote(str(value), safe="")) for key, value in params.items()
        ]

        try:
            signed_query, _unused = XGnarly(user_agent).sign(pairs, ms_token=ms_token)
        except Exception as e:
            raise ValueError(_("生成 X-Gnarly 失败：{0}").format(e)) from e

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"
        return f"{base_endpoint}{separator}{signed_query}"


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
    - _TIKTOK_SECUID_URL_PARREN: 编译后的正则表达式，用于从 /user/<sec_uid> 形式的链接中提取 sec_uid。
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
    ```python
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
    ```
    """

    _TIKTOK_SECUID_PARREN = re.compile(
        r"<script id=\"__UNIVERSAL_DATA_FOR_REHYDRATION__\" type=\"application/json\">(.*?)</script>"
    )
    _TIKTOK_SECUID_URL_PARREN = re.compile(r"/user/(MS4wLjABAAAA[\w-]+)")
    _TIKTOK_UNIQUEID_PARREN = re.compile(r"/@([^/?]*)")
    _TIKTOK_NOTFOUND_PARREN = re.compile(r"notfound")

    # 主页 HTML 中的用户信息（webapp.user-detail，与用户信息接口的响应结构相同），按 sec_uid 缓存
    _USER_DETAIL_TTL = 600
    _user_details: Dict[str, Tuple[float, dict]] = {}

    proxies = ClientConfManager.proxies()

    def __init__(self, proxies: Optional[dict] = None):
        # 应用配置或 --proxies 中的代理优先，没有配置时使用客户端配置中的代理
        super().__init__(proxies=prefer_proxies(proxies, self.proxies))

    @classmethod
    async def get_secuid(cls, url: str, proxies: Optional[dict] = None) -> str:
        """
        获取TikTok用户sec_uid。

        Args:
            url: 用户主页链接
            proxies (dict): 调用方的代理配置，没有配置代理时使用客户端配置中的代理 (Proxies of the caller)

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
            raise TypeError(_("输入参数必须是字符串"))

        extracted_url = extract_valid_urls(url)

        if extracted_url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))
        url = extracted_url

        # /user/<sec_uid> 形式的链接本身带着 sec_uid，而它的页面里没有用户数据（#366），直接从链接提取
        url_match = cls._TIKTOK_SECUID_URL_PARREN.search(url)
        if url_match:
            return url_match.group(1)

        # 创建一个实例以访问 aclient
        instance = cls(proxies)

        try:
            # 主页 HTML 不需要 msToken，不带 cookie 也能取到 sec_uid（2026-09-26 实测）；
            # 旧的 msToken 生成接口已失效，带上它反而会在请求前就报错
            headers = {
                "User-Agent": ClientConfManager.user_agent(),
                "Referer": url,
            }
            response = await instance.aclient.get(
                url, headers=headers, follow_redirects=True
            )
            if response.status_code in {200, 444}:
                if cls._TIKTOK_NOTFOUND_PARREN.search(str(response.url)):
                    raise APINotFoundError(
                        _(
                            "页面不可用，可能是由于区域限制（代理）造成的。类名：{0}"
                        ).format(cls.__name__)
                    )

                match = cls._TIKTOK_SECUID_PARREN.search(str(response.text))
                if not match:
                    raise APIResponseError(
                        _("未在响应中找到 {0}，请检查链接。类名：{1}").format(
                            "__UNIVERSAL_DATA_FOR_REHYDRATION__", cls.__name__
                        )
                    )

                data = json.loads(match.group(1))
                default_scope = data.get("__DEFAULT_SCOPE__", {})

                if "/video/" in url:
                    video_detail = default_scope.get("webapp.video-detail", {})
                    user_info = (
                        video_detail.get("itemInfo", {})
                        .get("itemStruct", {})
                        .get("author", {})
                    )
                    sec_uid = user_info.get("secUid", None)
                else:
                    user_detail = default_scope.get("webapp.user-detail", {})
                    user_info = user_detail.get("userInfo", {}).get("user", {})
                    sec_uid = user_info.get("secUid", None)
                    if sec_uid:
                        cls._user_details[sec_uid] = (time.monotonic(), user_detail)
                    else:
                        # 账号不存在或被封禁时主页仍返回 200，只在 statusCode 中说明（如 10221、209002）
                        raise APINotFoundError(
                            _(
                                "主页中没有用户信息（statusCode：{0}），账号可能不存在、已被封禁或在当前地区不可见"
                            ).format(user_detail.get("statusCode"))
                        )

                if sec_uid is None:
                    raise ValueError(_("获取 {0} 失败").format("sec_uid"))

                return sec_uid
            else:
                raise APIResponseError(_("接口状态码异常，请检查重试"))

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format("请求端点超时", url, instance.proxies, cls.__name__, exc)
            )

        except httpx.NetworkError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    "网络连接失败，请检查当前网络环境",
                    url,
                    instance.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProtocolError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIUnauthorizedError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format("请求协议错误", url, instance.proxies, cls.__name__, exc)
            )

        except httpx.ProxyError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format("请求代理错误", url, instance.proxies, cls.__name__, exc)
            )

        except httpx.HTTPStatusError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    "状态码错误", url, instance.proxies, cls.__name__, exc
                )
            )
        finally:
            await instance.close()

    @classmethod
    def remember_user_detail(cls, sec_uid: str, detail: dict) -> None:
        """缓存用户信息，供 cached_user_detail 使用 (Cache a user detail)"""
        cls._user_details[sec_uid] = (time.monotonic(), detail)

    @classmethod
    def cached_user_detail(cls, sec_uid: str) -> Optional[dict]:
        """
        get_secuid 打开主页时取得的用户信息，10 分钟内有效 (User detail seen on the profile page)

        用户信息接口对游客 cookie 只返回空内容，而主页 HTML 中的用户信息游客也能取得，
        结构与接口响应相同（userInfo.user、userInfo.stats）。

        Returns:
            Optional[dict]: 用户信息，没有或已过期时为 None
        """
        cached = cls._user_details.get(sec_uid)
        if not cached or time.monotonic() - cached[0] > cls._USER_DETAIL_TTL:
            cls._user_details.pop(sec_uid, None)
            return None
        return cached[1]

    @classmethod
    async def get_all_secuid(cls, urls: list, proxies: Optional[dict] = None) -> list:
        """
        获取多个TikTok用户的sec_uid。

        Args:
            urls: 用户主页链接列表
            proxies (dict): 调用方的代理配置，没有配置代理时使用客户端配置中的代理 (Proxies of the caller)

        Returns:
            secuids: 用户sec_uid列表

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

        secuids = [cls.get_secuid(url, proxies) for url in urls]
        return await asyncio.gather(*secuids)

    @classmethod
    async def get_uniqueid(cls, url: str, proxies: Optional[dict] = None) -> str:
        """
        获取TikTok用户unique_id。

        Args:
            url: 用户主页链接
            proxies (dict): 调用方的代理配置，没有配置代理时使用客户端配置中的代理 (Proxies of the caller)

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
            raise TypeError(_("输入参数必须是字符串"))

        extracted_url = extract_valid_urls(url)

        if extracted_url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))
        url = extracted_url

        # 创建一个实例以访问 aclient
        instance = cls(proxies)

        try:
            headers = {
                "User-Agent": ClientConfManager.user_agent(),
                "Referer": url,
            }
            response = await instance.aclient.get(
                url, headers=headers, follow_redirects=True
            )

            if response.status_code in {200, 444}:
                if cls._TIKTOK_NOTFOUND_PARREN.search(str(response.url)):
                    raise APINotFoundError(
                        _(
                            "页面不可用，可能是由于区域限制（代理）造成的。类名：{0}"
                        ).format(cls.__name__)
                    )

                match = cls._TIKTOK_UNIQUEID_PARREN.search(str(response.url))
                if not match:
                    raise APIResponseError(
                        _("未在响应中找到 {0}，请检查链接。类名：{1}").format(
                            "unique_id", cls.__name__
                        )
                    )

                unique_id = match.group(1)

                if unique_id is None:
                    raise ValueError(
                        _("获取 {0} 失败，{1}").format("unique_id", str(response.url))
                    )

                return unique_id

            else:
                raise APIResponseError(_("接口状态码异常，请检查重试"))

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    "请求端点超时",
                    url,
                    instance.proxies,
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
                    "网络连接失败，请检查当前网络环境",
                    url,
                    instance.proxies,
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
                    "请求协议错误",
                    url,
                    instance.proxies,
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
                    "请求代理错误",
                    url,
                    instance.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.HTTPStatusError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    "状态码错误",
                    url,
                    instance.proxies,
                    cls.__name__,
                    exc,
                )
            )
        finally:
            await instance.close()

    @classmethod
    async def get_all_uniqueid(cls, urls: list, proxies: Optional[dict] = None) -> list:
        """
        获取多个TikTok用户的unique_id。

        Args:
            urls: 用户主页链接列表
            proxies (dict): 调用方的代理配置，没有配置代理时使用客户端配置中的代理 (Proxies of the caller)

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

        unique_ids = [cls.get_uniqueid(url, proxies) for url in urls]
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
    ```python
        # 获取单个视频的 aweme_id
        url = "https://www.tiktok.com/@scarlettjonesuk/video/7255716763118226715"
        aweme_id = await AwemeIdFetcher.get_aweme_id(url)

        # 获取多个视频的 aweme_id 列表
        urls = [
            "https://www.tiktok.com/@scarlettjonesuk/video/7255716763118226715",
            "https://www.tiktok.com/@scarlettjonesuk/video/7255716763118226715?is_from_webapp=1&sender_device=pc&web_id=7306060721837852167"
        ]
        aweme_ids = await AwemeIdFetcher.get_all_aweme_id(urls)
    ```
    """

    _TIKTOK_AWEMEID_PARREN = re.compile(r"video/(\d*)")
    _TIKTOK_NOTFOUND_PARREN = re.compile(r"notfound")

    proxies = ClientConfManager.proxies()

    def __init__(self, proxies: Optional[dict] = None):
        # 应用配置或 --proxies 中的代理优先，没有配置时使用客户端配置中的代理
        super().__init__(proxies=prefer_proxies(proxies, self.proxies))

    @classmethod
    async def get_aweme_id(cls, url: str, proxies: Optional[dict] = None) -> str:
        """
        获取TikTok作品aweme_id。

        Args:
            url: 作品链接
            proxies (dict): 调用方的代理配置，没有配置代理时使用客户端配置中的代理 (Proxies of the caller)

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
            raise TypeError(_("输入参数必须是字符串"))

        extracted_url = extract_valid_urls(url)

        if extracted_url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))
        url = extracted_url

        # 创建一个实例以访问 aclient
        instance = cls(proxies)

        try:
            response = await instance.aclient.get(url, follow_redirects=True)
            if response.status_code in {200, 444}:
                if cls._TIKTOK_NOTFOUND_PARREN.search(str(response.url)):
                    raise APINotFoundError(
                        _(
                            "页面不可用，可能是由于区域限制（代理）造成的。类名：{0}"
                        ).format(cls.__name__)
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
                    raise ValueError(
                        _("获取 {0} 失败，{1}").format("aweme_id", str(response.url))
                    )

                return aweme_id
            else:
                raise APIResponseError(_("接口状态码异常，请检查重试"))

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
            raise APITimeoutError(
                _(
                    "{0}。 链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}"
                ).format(
                    _("请求端点超时"),
                    url,
                    instance.proxies,
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
                    url,
                    instance.proxies,
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
                    url,
                    instance.proxies,
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
                    url,
                    instance.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.HTTPStatusError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIResponseError(
                _("{0}。链接：{1} 代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("状态码错误"),
                    url,
                    instance.proxies,
                    cls.__name__,
                    exc,
                )
            )
        finally:
            await instance.close()

    @classmethod
    async def get_all_aweme_id(cls, urls: list, proxies: Optional[dict] = None) -> list:
        """
        获取多个TikTok视频的aweme_id。

        Args:
            urls: 视频链接列表
            proxies (dict): 调用方的代理配置，没有配置代理时使用客户端配置中的代理 (Proxies of the caller)

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

        aweme_ids = [cls.get_aweme_id(url, proxies) for url in urls]
        return await asyncio.gather(*aweme_ids)


class DeviceIdManager(BaseCrawler):
    """
    DeviceIdManager 类用于生成设备 ID和 tt_chain_token。
    设备 ID 和 tt_chain_token 是 TikTok API 请求的必要参数。

    该类继承自 BaseCrawler，利用其中的 aclient 进行 HTTP 请求。主要包含两个方法：
    - gen_device_id: 异步类方法，用于生成设备 ID。
    - gen_device_ids: 异步类方法，用于生成多个设备 ID。

    类属性:
    - _DEVICE_ID_PARTTERN: 编译后的正则表达式，用于匹配设备 ID。
    - _DEVICE_ID_URL: 设备 ID 生成器的 URL。
    - _device_id_headers: 类方法，构建设备 ID 生成器的请求头。
    - proxies: 从 ClientConfManager 获取的代理配置。

    方法:
    - __init__: 初始化 DeviceIdManager 实例，并调用父类的初始化方法。
    - gen_device_id: 异步类方法，用于生成设备 ID。
    - gen_device_ids: 异步类方法，用于生成多个设备 ID。

    异常处理:
    - 在 HTTP 请求过程中，处理可能出现的 TimeoutException、NetworkError、ProtocolError、ProxyError 和 HTTPStatusError 异常，并记录相应的错误信息。

    使用示例:
    ```python
        # 生成单个设备 ID
        device = await DeviceIdManager.gen_device_id()
        deviceId = device["deviceId"]
        tt_chain_token = device["cookie"]

        # 生成单个设备 ID，返回完整的 cookie 信息
        device = await DeviceIdManager.gen_device_id(full_cookie=True)
        deviceId = device["deviceId"]
        cookie = device["cookie"]

        # 生成多个设备 ID
        devices = await DeviceIdManager.gen_device_ids(3)
        deviceIds = devices["deviceId"]
        tt_chain_tokens = devices["cookies"]

        # 生成多个设备 ID，返回完整的 cookie 信息
        devices = await DeviceIdManager.gen_device_ids(3, full_cookie=True)
        deviceIds = devices["deviceId"]
        cookies = devices["cookie"]
    ```
    """

    # 预编译正则表达式
    _DEVICE_ID_PARTTERN = re.compile(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">\s*(.*?)\s*</script>',
        re.DOTALL,
    )

    _DEVICE_ID_URL = "https://www.tiktok.com/"
    _DEVICE_ID_FULL_URL = "https://www.tiktok.com/explore"

    proxies = ClientConfManager.proxies()

    def __init__(self):
        super().__init__(proxies=self.proxies)

    @classmethod
    def _device_id_headers(cls) -> dict:
        """设备 ID 生成器的请求头，首页 HTML 不需要 msToken (Headers for the device ID page)"""
        return {"User-Agent": ClientConfManager.user_agent()}

    @classmethod
    async def gen_device_id(cls, full_cookie: bool = False) -> dict:
        """
        生成设备 ID。

        Args:
            full_cookie(bool): 是否返回完整的 cookie 信息，默认为 False。

        Returns:
            dict: 生成的设备 ID 和 tt_chain_token

        Notes:
            full_cookie为True时，返回完整的cookie信息，否则只返回tt_chain_token。默认即可。

        Raises:
            APITimeoutError: 如果请求超时。
            APIConnectionError: 如果网络连接失败。
            APIUnauthorizedError: 如果请求协议错误。
            APIResponseError: 如果响应不符合要求。
        """

        instance = cls()

        try:
            response = await instance.aclient.get(
                (
                    instance._DEVICE_ID_URL
                    if not full_cookie
                    else instance._DEVICE_ID_FULL_URL
                ),
                headers=instance._device_id_headers(),
                follow_redirects=True,
            )
            response.raise_for_status()

            # 增加检查匹配结果是否为 None 的逻辑
            match = instance._DEVICE_ID_PARTTERN.search(response.text)
            if match is None:
                raise APIResponseError(_("未能找到所需的设备 ID 信息"))

            data = match.group(1).strip()
            # 逐个读取 Set-Cookie 头，避免值里带逗号时被截断（同 #434）
            cookie = join_set_cookie_headers(response.headers)
            deviceId = (
                json.loads(data)
                .get("__DEFAULT_SCOPE__", {})
                .get("webapp.app-context", {})
                .get("wid")
            )

            if deviceId is None:
                raise APIResponseError(_("{0} 生成失败").format("deviceId"))

            if cookie is None:
                raise APIResponseError(_("{0} 生成失败").format("tt_chain_token"))

            return {"deviceId": deviceId, "cookie": cookie}

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
            raise APITimeoutError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("请求端点超时"),
                    instance._DEVICE_ID_URL,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.NetworkError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIConnectionError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("网络连接失败，请检查当前网络环境"),
                    instance._DEVICE_ID_URL,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )

        except httpx.ProtocolError as exc:
            trace_logger.error(traceback.format_exc())
            raise APIUnauthorizedError(
                _("{0}。链接：{1}，代理：{2}，异常类名：{3}，异常详细信息：{4}").format(
                    _("请求协议错误"),
                    instance._DEVICE_ID_URL,
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
                    instance._DEVICE_ID_URL,
                    cls.proxies,
                    cls.__name__,
                    exc,
                )
            )
        finally:
            await instance.close()

    @classmethod
    async def gen_device_ids(cls, count: int, full_cookie: bool = False) -> dict:
        """
        生成多个设备 ID。

        Args:
            count: 生成的设备 ID 数量

        Returns:
            device_ids: 生成的设备 ID 字典

        Raises:
            TypeError: 如果输入的 count 不是整数。
            ValueError: 如果输入的 count 小于 1。
        """

        if not isinstance(count, int):
            raise TypeError(_("count 必须是整数"))

        if not isinstance(full_cookie, bool):
            raise TypeError(_("full_cookie 必须是布尔值"))

        if count < 1:
            raise ValueError(_("count 参数必须大于 0"))

        if count > 10:
            logger.warning(_("生成设备 ID 数量过多，可能会导致请求失败。"))
            count = 10

        tasks = [cls.gen_device_id(full_cookie) for _ in range(count)]
        results = await asyncio.gather(*tasks)

        device_ids = [result["deviceId"] for result in results]
        cookies = [result["cookie"] for result in results]

        return {"deviceId": device_ids, "cookie": cookies}


def normalize_cursor(cursor, default: Optional[int] = None) -> Optional[int]:
    """
    把分页游标统一转换为整数 (Normalize a pagination cursor to int)

    TikTok 接口返回的 cursor 有时是字符串、有时是整数，与整数比较前需要先统一类型（#270）。

    Args:
        cursor: 接口返回或配置中的游标 (Cursor from the API or config)
        default (Optional[int]): 无法解析时返回的值 (Value returned when parsing fails)

    Returns:
        Optional[int]: 整数游标 (Integer cursor)
    """

    try:
        return int(cursor)
    except (TypeError, ValueError):
        return default


def format_file_name(
    naming_template: str,
    aweme_data: Optional[dict] = None,
    custom_fields: Optional[dict] = None,
) -> str:
    """
    根据配置文件的全局格式化文件名
    (Format file name according to the global conf file)

    Args:
        naming_template (str): 文件的命名模板, 如 "{create}_{desc}" (Naming template for files, such as "{create}_{desc}")
        aweme_data (dict): 抖音数据的字典 (dict of tiktok data)
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

    if not naming_template:
        raise InvalidConfError(key="naming", value=naming_template)

    if not aweme_data:
        raise APIResponseError(_("缺少视频数据信息，无法格式化文件名"), status_code=400)

    # 为不同系统设置不同的文件名长度限制
    os_limit = {
        "win32": 200,
        "cygwin": 200,
        "darwin": 200,
        "linux": 200,
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

    # 获取绝对路径，与重命名用户目录时的路径计算一致
    user_path = get_user_folder_path(kwargs, "tiktok", uniqueId)

    # 创建目录
    user_path.mkdir(parents=True, exist_ok=True)

    return user_path


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

    Note:
        uniqueId 变化时，把各下载模式下旧 uniqueId 的目录都重命名为新 uniqueId，
        已下载的文件随目录保留；某个模式下新 uniqueId 的目录已存在时，
        该模式的两个目录都保持不变。
        (When the uniqueId changes, the folders of the old uniqueId are renamed to the
        new uniqueId in every download mode, keeping the downloaded files; in a mode
        where a folder of the new uniqueId already exists, both folders are left as
        they are.)
    """
    local_uniqueId = local_user_data.get("uniqueId") if local_user_data else None

    if local_uniqueId and current_uniqueId and local_uniqueId != current_uniqueId:
        # uniqueId不一致，把各下载模式下旧 uniqueId 的目录重命名为新 uniqueId
        user_path = migrate_user_folders(
            kwargs, "tiktok", local_uniqueId, current_uniqueId
        )
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path

    return create_user_folder(kwargs, current_uniqueId)

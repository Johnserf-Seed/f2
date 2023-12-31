# path: f2/apps/tiktok/utils.py

import f2
import re
import json
import time
import httpx
import random
import asyncio

from typing import Union
from pathlib import Path
from urllib.parse import quote, unquote
from typing import Dict, Optional, Union
from httpx import URL, Proxy


from f2.i18n.translator import _
from f2.log.logger import logger
from f2.utils.xbogus import XBogus as XB
from f2.utils.conf_manager import ConfigManager
from f2.utils.utils import gen_random_str, get_timestamp, extract_valid_urls
from f2.exceptions.api_exceptions import (
    APIError,
    APIConnectionError,
    APIResponseError,
    APIUnavailableError,
    APIUnauthorizedError,
    APINotFoundError,
)


class TokenManager:
    tk_manager = ConfigManager(f2.APP_CONFIG_FILE_PATH)
    token_conf = tk_manager.get_config("tiktok").get("msToken", None)
    ttwid_conf = tk_manager.get_config("tiktok").get("ttwid", None)
    odin_tt_conf = tk_manager.get_config("tiktok").get("odin_tt", None)
    proxies_conf = tk_manager.get_config("tiktok").get("proxies", None)
    proxies = {
        "http://": proxies_conf.get("http"),
        "https://": proxies_conf.get("https"),
    }

    @classmethod
    def gen_real_msToken(cls) -> str:
        """
        生成真实的msToken,当出现错误时返回虚假的值
        (Generate a real msToken and return a false value when an error occurs)
        """

        payload = json.dumps(
            {
                "magic": cls.token_conf["magic"],
                "version": cls.token_conf["version"],
                "dataType": cls.token_conf["dataType"],
                "strData": cls.token_conf["strData"],
                "tspFromClient": get_timestamp(),
            }
        )

        headers = {
            "User-Agent": cls.token_conf["User-Agent"],
            "Content-Type": "application/json",
        }

        transport = httpx.HTTPTransport(retries=5)
        with httpx.Client(transport=transport, proxies=dict(cls.proxies)) as client:
            try:
                response = client.post(
                    cls.token_conf["url"], headers=headers, content=payload
                )

                if response.status_code == 401:
                    raise APIUnauthorizedError(
                        _("由于某些错误, 无法获取msToken")
                    )  # (Unauthorized request,Unable to get msToken)
                elif response.status_code == 404:
                    raise APINotFoundError(_("无法找到API端点"))

                msToken = str(httpx.Cookies(response.cookies).get("msToken"))

                if len(msToken) != 148:
                    raise APIResponseError(
                        _("msToken: 检查没有通过, 请更新tiktok配置文件中msToken的url里的msToken")
                    )

                return msToken

            except httpx.RequestError:
                # 捕获所有与 httpx 请求相关的异常情况 (Captures all httpx request-related exceptions)
                raise APIConnectionError(_("连接端点失败: {0}").format(cls.token_conf["url"]))

            except httpx.HTTPStatusError as e:
                # 捕获 httpx 的状态代码错误 (captures specific status code errors from httpx)
                raise APIResponseError(
                    f"HTTP Status Code {e.response.status_code}: {e.response.text}"
                )

            except APIError as e:
                e.display_error()
                # 返回虚假的msToken (Return a fake msToken)
                logger.debug(_("生成虚假的msToken"))
                return cls.gen_false_msToken()

    @classmethod
    def gen_false_msToken(cls) -> str:
        """生成随机msToken (Generate random msToken)"""
        return gen_random_str(146) + "=="

    @classmethod
    def gen_ttwid(cls) -> str:
        """
        生成请求必带的ttwid (Generate the essential ttwid for requests)
        """
        headers = {"Cookie": cls.ttwid_conf.get("cookie"), "Content-Type": "text/plain"}
        transport = httpx.HTTPTransport(retries=5)
        with httpx.Client(transport=transport, proxies=dict(cls.proxies)) as client:
            try:
                response = client.post(
                    cls.ttwid_conf["url"],
                    headers=headers,
                    content=cls.ttwid_conf["data"],
                )

                if response.status_code == 401:
                    raise APIUnauthorizedError(_("401 由于某些错误, 无法获取ttwid"))
                elif response.status_code == 404:
                    raise APINotFoundError(_("404 无法找到API端点"))

                ttwid = httpx.Cookies(response.cookies).get("ttwid")

                if ttwid is None:
                    raise APIResponseError(_("ttwid: 检查没有通过, 请更新配置文件中的ttwid"))

                return ttwid

            except httpx.RequestError:
                # 捕获所有与 httpx 请求相关的异常情况 (Captures all httpx request-related exceptions)
                raise APIConnectionError(
                    _("连接端点失败: {0}").format(cls.ttwid_conf["url"])
                )  # (Failed to connect to endpoint)

            except httpx.HTTPStatusError as e:
                # 捕获 httpx 的状态代码错误 (captures specific status code errors from httpx)
                raise APIResponseError(
                    f"HTTP Status Code {e.response.status_code}: {e.response.text}"
                )

            except APIError as e:
                e.display_error()
                time.sleep(2)
                exit(0)

    @classmethod
    def gen_odin_tt(cls):
        """
        生成请求必带的odin_tt (Generate the essential odin_tt for requests)
        """
        transport = httpx.HTTPTransport(retries=5)
        with httpx.Client(transport=transport, proxies=dict(cls.proxies)) as client:
            try:
                response = client.get(cls.odin_tt_conf["url"])

                if response.status_code == 401:
                    raise APIUnauthorizedError(
                        _("401 由于某些错误, 无法获取ttwid")
                    )  # (Unauthorized request,Unable to get ttwid)
                elif response.status_code == 404:
                    raise APINotFoundError(_("404 无法找到API端点"))

                odin_tt = httpx.Cookies(response.cookies).get("odin_tt")

                if odin_tt is None:
                    raise APIResponseError(_("odin_tt: 检查没有通过, 请更新配置文件中的odin_tt"))

                return odin_tt

            except httpx.RequestError:
                # 捕获所有与 httpx 请求相关的异常情况 (Captures all httpx request-related exceptions)
                raise APIConnectionError(
                    _("连接端点失败: {0}").format(cls.odin_tt_conf["url"])
                )  # (Failed to connect to endpoint)

            except httpx.HTTPStatusError as e:
                # 捕获 httpx 的状态代码错误 (captures specific status code errors from httpx)
                raise APIResponseError(
                    f"HTTP Status Code {e.response.status_code}: {e.response.text}"
                )

            except APIError as e:
                e.display_error()
                time.sleep(2)
                exit(0)


class XBogusManager:
    @classmethod
    def str_2_endpoint(cls, endpoint: str) -> str:
        try:
            final_endpoint = XB().getXBogus(endpoint)
        except Exception as e:
            raise RuntimeError(_("生成X-Bogus失败: {0})").format(e))

        return final_endpoint[0]

    @classmethod
    def model_2_endpoint(cls, base_endpoint: str, params: dict) -> str:
        # 检查params是否是一个字典 (Check if params is a dict)
        if not isinstance(params, dict):
            raise TypeError(_("参数必须是字典类型"))

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])

        try:
            xb_value = XB().getXBogus(param_str)
        except Exception as e:
            raise RuntimeError(_("生成X-Bogus失败: {0})").format(e))

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}&X-Bogus={xb_value[1]}"

        return final_endpoint


class SecUserIdFetcher:
    _TIKTOK_SECUID_PARREN = re.compile(
        r"<script id=\"__UNIVERSAL_DATA_FOR_REHYDRATION__\" type=\"application/json\">(.*?)</script>"
    )
    _TIKTOK_UNIQUEID_PARREN = re.compile(r"/@([^/?]*)")

    @classmethod
    async def get_secuid(cls, url: str) -> str:
        """
        获取TikTok用户sec_uid
        Args:
            url: 用户主页链接
        Return:
            sec_uid: 用户唯一标识
        """

        # 进行参数检查
        if not isinstance(url, str):
            raise TypeError("输入参数必须是字符串")

        # 提取有效URL
        url = extract_valid_urls(url)

        transport = httpx.AsyncHTTPTransport(retries=5)
        async with httpx.AsyncClient(
            transport=transport, proxies=dict(TokenManager.proxies), timeout=10
        ) as client:
            try:
                response = await client.get(url, follow_redirects=True)

                if response.status_code in {200, 444}:
                    match = cls._TIKTOK_SECUID_PARREN.search(str(response.text))
                    if not match:
                        raise APIResponseError(_("未在响应中找到sec_uid"))

                    # 提取SIGI_STATE对象中的sec_uid
                    data = json.loads(match.group(1))
                    default_scope = data.get("__DEFAULT_SCOPE__", {})
                    user_detail = default_scope.get("webapp.user-detail", {})
                    user_info = user_detail.get("userInfo", {}).get("user", {})
                    sec_uid = user_info.get("secUid")

                    if sec_uid is None:
                        raise RuntimeError(_("获取sec_uid失败, {0}".format(user_info)))

                    return sec_uid
                else:
                    raise ConnectionError(_("接口状态码异常, 请检查重试"))

            except httpx.RequestError:
                raise APIConnectionError(_("连接端点失败: {0}").format(url))

            except APIError as e:
                e.display_error()
                await asyncio.sleep(2)
                exit(0)

    @classmethod
    async def get_all_secuid(cls, urls: list) -> list:
        """
        获取列表secuid列表 (Get list sec_user_id list)

        Args:
            urls: list: 用户url列表 (User url list)

        Return:
            secuids: list: 用户secuid列表 (User secuid list)
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        secuids = [cls.get_secuid(url) for url in urls]
        return await asyncio.gather(*secuids)

    @classmethod
    async def get_uniqueid(cls, url: str) -> str:
        """
        获取TikTok用户unique_id
        Args:
            url: 用户主页链接
        Return:
            unique_id: 用户唯一id
        """

        # 进行参数检查
        if not isinstance(url, str):
            raise TypeError("输入参数必须是字符串")

        # 提取有效URL
        url = str(extract_valid_urls(url))

        transport = httpx.AsyncHTTPTransport(retries=5)
        async with httpx.AsyncClient(
            transport=transport, proxies=dict(TokenManager.proxies), timeout=10
        ) as client:
            try:
                response = await client.get(url, follow_redirects=True)

                if response.status_code in {200, 444}:
                    match = cls._TIKTOK_UNIQUEID_PARREN.search(str(response.url))
                    if not match:
                        raise APIResponseError(
                            _("未在响应中找到unique_id")
                        )  # (No unique_id found in the address of the response)

                    unique_id = match.group(1)

                    if unique_id is None:
                        raise RuntimeError(_("获取unique_id失败, {0}".format(response.url)))

                    return unique_id
                else:
                    raise ConnectionError(
                        _("接口状态码异常 {0}, 请检查重试").format(response.status_code)
                    )

            except httpx.RequestError:
                raise APIConnectionError(_("连接端点失败: {0}").format(url))

            except APIError as e:
                e.display_error()
                await asyncio.sleep(2)
                exit(0)

    @classmethod
    async def get_all_uniqueid(cls, urls: list) -> list:
        """
        获取列表unique_id列表 (Get list sec_user_id list)

        Args:
            urls: list: 用户url列表 (User url list)

        Return:
            unique_ids: list: 用户unique_id列表 (User unique_id list)
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        unique_ids = [cls.get_uniqueid(url) for url in urls]
        return await asyncio.gather(*unique_ids)


class AwemeIdFetcher:
    # https://www.tiktok.com/@scarlettjonesuk/video/7255716763118226715
    # https://www.tiktok.com/@scarlettjonesuk/video/7255716763118226715?is_from_webapp=1&sender_device=pc&web_id=7306060721837852167

    # 预编译正则表达式
    _TIKTOK_AWEMEID_PARREN = re.compile(r"video/(\d*)")

    @classmethod
    async def get_aweme_id(cls, url: str) -> str:
        """
        获取TikTok作品aweme_id
        Args:
            url: 作品链接
        Return:
            aweme_id: 作品唯一标识
        """

        # 进行参数检查
        if not isinstance(url, str):
            raise TypeError("输入参数必须是字符串")

        # 提取有效URL
        url = str(extract_valid_urls(url))

        transport = httpx.AsyncHTTPTransport(retries=5)
        async with httpx.AsyncClient(
            transport=transport, proxies=dict(TokenManager.proxies), timeout=10
        ) as client:
            try:
                response = await client.get(url, follow_redirects=True)

                if response.status_code in {200, 444}:
                    match = cls._TIKTOK_AWEMEID_PARREN.search(str(response.url))
                    if not match:
                        raise APIResponseError(_("未在响应中找到aweme_id"))

                    aweme_id = match.group(1)

                    if aweme_id is None:
                        raise RuntimeError(_("获取aweme_id失败, {0}".format(response.url)))

                    return aweme_id
                else:
                    raise ConnectionError(
                        _("接口状态码异常 {0}, 请检查重试").format(response.status_code)
                    )

            except httpx.RequestError:
                raise APIConnectionError(_("连接端点失败: {0}").format(url))

            except APIError as e:
                e.display_error()
                await asyncio.sleep(2)
                exit(0)


def format_file_name(
    naming_template: str,
    aweme_data: dict = {},
    custom_fields: dict = {},
    desc_length_limit: int = 200,
) -> str:
    """
    根据配置文件的全局格式化文件名
    (Format file name according to the global conf file)

    Args:
        aweme_data (dict): 抖音数据的字典 (dict of douyin data)
        naming_template (str): 文件的命名模板, 如 "{create}_{desc}" (Naming template for files, such as "{create}_{desc}")
        custom_fields (dict): 用户自定义字段, 用于替代默认的字段值 (Custom fields for replacing default field values)
        desc_length_limit (int): 控制 'desc' 字段的长度限制 (Control the length limit of the 'desc' field)

    Note:
        windows 文件名长度限制为 255 个字符, 开启了长文件名支持后为 32,767 个字符
        (Windows file name length limit is 255 characters, 32,767 characters after long file name support is enabled)
        Unix 文件名长度限制为 255 个字符
        (Unix file name length limit is 255 characters)
        取去除后的20个字符, 加上后缀, 一般不会超过255个字符
        (Take the removed 20 characters, add the suffix, and generally not exceed 255 characters)

    Returns:
        str: 格式化的文件名 (Formatted file name)
    """
    # 如果字典中没有对应的键，则使用用户自定义的字段
    # (If there is no corresponding key in the dictionary, use the user-defined field)
    fields = {
        "create": "",
        "nickname": "",
        "aweme_id": "",
        "desc": "",
        "uid": "",
    }

    if custom_fields:
        fields.update(custom_fields)
    else:
        fields = {
            "create": aweme_data.get("create_time", ""),
            "nickname": aweme_data.get("nickname", ""),
            "aweme_id": aweme_data.get("aweme_id", ""),
            "desc": aweme_data.get("desc", ""),
            "uid": aweme_data.get("uid", ""),
        }

    # 处理 'desc' 字段的长度限制
    if desc_length_limit is not None and len(fields["desc"]) > desc_length_limit:
        half_limit = desc_length_limit // 2 - 6
        fields[
            "desc"
        ] = f"{fields['desc'][:half_limit]}......{fields['desc'][-half_limit:]}"

    return naming_template.format(**fields)


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
        仅支持相对路径。
        (Only relative paths are supported.)

    Raises:
        TypeError: 如果 kwargs 不是字典格式，将引发 TypeError。
        (If kwargs is not in dict format, TypeError will be raised.)
    """

    # 确定函数参数是否正确
    if not isinstance(kwargs, dict):
        raise TypeError("kwargs 参数必须是字典")  # (The kwargs parameter must be a dict)

    # 创建基础路径
    base_path = Path(kwargs.get("path", "Download"))

    # 添加下载模式和用户名
    user_path = (
        base_path / "tiktok" / kwargs.get("mode", "PLEASE_SETUP_MODE") / str(nickname)
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

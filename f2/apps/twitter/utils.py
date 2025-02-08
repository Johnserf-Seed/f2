# path: f2/apps/twitter/utils.py

import f2
import re
import httpx
import asyncio
import traceback

from typing import Union
from pathlib import Path
from urllib.parse import urlparse

from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.conf_manager import ConfigManager
from f2.utils.utils import extract_valid_urls, split_filename
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
    twitter_conf = client_conf.get("twitter", {})

    @classmethod
    def client(cls) -> dict:
        return cls.twitter_conf

    @classmethod
    def conf_version(cls) -> str:
        return cls.client_conf.get("version", "unknown")

    @classmethod
    def proxies(cls) -> dict:
        return cls.twitter_conf.get("proxies", {})

    @classmethod
    def headers(cls) -> dict:
        return cls.twitter_conf.get("headers", {})

    @classmethod
    def user_agent(cls) -> str:
        return cls.headers().get("User-Agent", "")

    @classmethod
    def referer(cls) -> str:
        return cls.headers().get("Referer", "")

    @classmethod
    def authorization(cls) -> str:
        return cls.headers().get("Authorization", "")

    @classmethod
    def x_csrf_token(cls) -> str:
        return cls.headers().get("X-Csrf-Token", "")


class ModelManager:

    @classmethod
    def model_2_endpoint(
        cls,
        base_endpoint: str,
        params: dict,
    ) -> str:
        if not isinstance(params, dict):
            raise TypeError(_("参数必须是字典类型"))

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}"

        return final_endpoint


class UniqueIdFetcher(BaseCrawler):
    # https://x.com/CaroylnG61544
    # https://x.com/CaroylnG61544/
    # https://x.com/CaroylnG61544/followers
    # https://x.com/CaroylnG61544/status/1440000000000000000
    # https://twitter.com/CaroylnG61544/status/1440000000000000000/photo/1

    # 预编译正则表达式
    _UNIQUE_ID_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?(twitter\.com|x\.com)/(?:@)?([a-zA-Z0-9_]+)"
    )

    @classmethod
    async def get_unique_id(cls, url: str) -> str:
        """
        从用户URL中提取用户ID
        (Extract user ID from user URL)

        Args:
            url (str): 用户URL (User URL)

        Returns:
            str: 用户唯一ID (User Unique Id)
        """

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        url = extract_valid_urls(url)

        if url is None:
            raise (
                APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))
            )

        # 创建一个实例以访问 aclient
        instance = cls()

        try:
            headers = {
                "User-Agent": ClientConfManager.user_agent(),
                "Referer": url,
            }
            response = await instance.aclient.get(
                url, headers=headers, follow_redirects=True
            )

            match = cls._UNIQUE_ID_PATTERN.search(str(response.url))
            if match:
                return match.group(2)
            else:
                raise APIResponseError(
                    _(
                        "未在响应的地址中找到unique_id，检查链接是否为用户链接。类名：{0}"
                    ).format(cls.__name__)
                )

        except httpx.TimeoutException as exc:
            trace_logger.error(traceback.format_exc())
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
            trace_logger.error(traceback.format_exc())
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
            trace_logger.error(traceback.format_exc())
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
            trace_logger.error(traceback.format_exc())
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

    @classmethod
    async def get_all_unique_ids(cls, urls: list) -> list:
        """
        从用户URL列表中提取所有用户唯一ID
        (Extract all unique ids from the list of user URLs)

        Args:
            urls (list): 用户URL列表 (List of user URLs)

        Returns:
            list: 用户唯一ID列表 (List of unique ids)
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        # 获取所有用户ID
        if urls == []:
            raise (
                APINotFoundError(
                    _("输入的URL List不合法。类名：{0}").format(cls.__name__)
                )
            )

        unique_ids = [cls.get_unique_id(url) for url in urls]
        return await asyncio.gather(*unique_ids)


class TweetIdFetcher(BaseCrawler):
    # 预编译正则表达式
    _TWEET_URL_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?(?:twitter|x)\.com/.*/status/(\d+)(?:/|\?|#.*$|$)"
    )

    @classmethod
    async def get_tweet_id(cls, url: str) -> str:
        """
        从推文URL中提取推文ID
        (Extract tweet ID from tweet URL)

        Args:
            url (str): 推文URL (Tweet URL)

        Returns:
            str: 推文ID (Tweet ID)
        """

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        url = extract_valid_urls(url)

        if url is None:
            raise (
                APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))
            )

        # 创建一个实例以访问 aclient
        instance = cls()

        # 解析URL并检查主机
        parsed_url = urlparse(url)
        host = parsed_url.hostname

        if host is None:
            raise APINotFoundError(
                _("无法解析URL的主机部分。类名：{0}".format(cls.__name__))
            )
        try:
            if "t.co" in host:
                response = await instance.aclient.get(
                    url, headers=ClientConfManager.headers(), follow_redirects=True
                )
                url = response.text

            match = cls._TWEET_URL_PATTERN.search(url)
            if match:
                return match.group(1)
            else:
                raise APIResponseError(
                    _(
                        "未在响应的地址中找到tweet_id，检查链接是否为推文链接。类名：{0}"
                    ).format(cls.__name__),
                    response.status_code,
                )

        except httpx.HTTPStatusError:
            raise APINotFoundError(
                _("未找到推文，请检查推文链接是否正确。类名：{0}").format(cls.__name__)
            )

        except httpx.RequestError as exc:
            raise APIConnectionError(
                _(
                    "请求端点失败，请检查当前网络环境。 链接：{0}，代理：{1}，异常类名：{2}，异常详细信息：{3}"
                ).format(url, ClientConfManager.proxies(), cls.__name__, exc)
            )

    @classmethod
    async def get_all_tweet_ids(cls, urls: list) -> list:
        """
        从推文URL列表中提取所有推文ID
        (Extract all tweet IDs from the list of tweet URLs)

        Args:
            urls (list): 推文URL列表 (List of tweet URLs)

        Returns:
            list: 推文ID列表 (List of tweet IDs)
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        # 获取所有推文ID
        if urls == []:
            raise (
                APINotFoundError(
                    _("输入的URL List不合法。类名：{0}").format(cls.__name__)
                )
            )

        tweet_ids = [cls.get_tweet_id(url) for url in urls]
        return await asyncio.gather(*tweet_ids)


def format_file_name(
    naming_template: str,
    tweet_data: dict = {},
    custom_fields: dict = {},
) -> str:
    """
    根据配置文件的全局格式化文件名
    (Format file name according to the global conf file)

    Args:
        naming_template (str): 文件的命名模板, 如 "{create}_{desc}" (Naming template for files, such as "{create}_{desc}")
        tweet_data (dict): 推文数据的字典 (dict of twitter data)
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
        "create": tweet_data.get("tweet_created_at", ""),  # 长度固定19
        "nickname": tweet_data.get("nickname", ""),  # 不固定
        "tweet_id": tweet_data.get("tweet_id", ""),  # 长度固定19
        "desc": split_filename(tweet_data.get("tweet_desc", ""), os_limit),
        "uid": tweet_data.get("user_unique_id", ""),  # 不固定
    }

    if custom_fields:
        # 更新自定义字段
        fields.update(custom_fields)

    try:
        return naming_template.format(**fields)
    except KeyError as e:
        raise KeyError(_("文件名模板字段 {0} 不存在，请检查".format(e)))


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
        base_path / "twitter" / kwargs.get("mode", "PLEASE_SETUP_MODE") / str(nickname)
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


def extract_desc(text):
    """
    提取推特标题，抛弃从 "https" 开始及其后的内容，包括其前一个空格。

    Args:
        text (str): 原始推文内容

    Returns:
        str: 提取后的标题
    """

    text = text.strip()  # 去掉两端空格
    https_index = text.find("https")  # 查找 "https" 的起始位置

    if https_index != -1:  # 如果存在 "https"
        # 找到 "https" 前第一个空格的位置
        cutoff_index = text.rfind(" ", 0, https_index)
        if cutoff_index != -1:
            return text[:cutoff_index].strip()  # 返回截断后的部分
    return text.strip()  # 如果没有 "https"，返回去掉两端空格后的内容

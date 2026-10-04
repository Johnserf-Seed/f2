# path: f2/apps/twitter/utils.py

import asyncio
import contextlib
import html
import json
import os
import re
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Tuple, Union
from urllib.parse import parse_qs, urlparse

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
from f2.utils.config import user_config
from f2.utils.config.conf_manager import ConfigManager
from f2.utils.file.name import split_filename
from f2.utils.file.path import get_user_folder_path, migrate_user_folders
from f2.utils.http.proxy import prefer_proxies
from f2.utils.string.formatter import extract_valid_urls


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
    # x.com 的保留路径，不是用户名；未登录时访问用户页面会被跳转到 /i/flow/login
    _RESERVED_PATHS = frozenset(
        {
            "i",
            "home",
            "explore",
            "search",
            "notifications",
            "messages",
            "settings",
            "compose",
            "intent",
            "share",
            "hashtag",
            "login",
            "logout",
            "signup",
            "tos",
            "privacy",
        }
    )

    proxies = ClientConfManager.proxies()

    def __init__(self, proxies: Optional[dict] = None):
        # 应用配置或 --proxies 中的代理优先，没有配置时使用客户端配置中的代理
        super().__init__(proxies=prefer_proxies(proxies, self.proxies))

    @classmethod
    def _match_unique_id(cls, url: str) -> Optional[str]:
        """从链接中取出用户名，x.com 的保留路径不算 (Extract the username from a URL)"""
        match = cls._UNIQUE_ID_PATTERN.search(url)
        if match and match.group(2).lower() not in cls._RESERVED_PATHS:
            return match.group(2)
        return None

    @classmethod
    async def get_unique_id(cls, url: str, proxies: Optional[dict] = None) -> str:
        """
        从用户URL中提取用户ID
        (Extract user ID from user URL)

        Args:
            url (str): 用户URL (User URL)
            proxies (dict): 调用方的代理配置，没有配置代理时使用客户端配置中的代理 (Proxies of the caller)

        Returns:
            str: 用户唯一ID (User Unique Id)
        """

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        extracted_url = extract_valid_urls(url)

        if extracted_url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))
        url = extracted_url

        # 链接里已经带着用户名时直接取出。x.com 未登录时会把用户页面跳转到登录页
        # （/i/flow/login），此前请求后再从地址里提取，拿到的是保留路径 i
        unique_id = cls._match_unique_id(url)
        if unique_id:
            return unique_id

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

            final_url = str(response.url)
            # 被跳转到登录页时，原来的地址在 redirect_after_login 参数中
            redirect = parse_qs(urlparse(final_url).query).get(
                "redirect_after_login", [""]
            )[0]
            unique_id = cls._match_unique_id(final_url) or (
                cls._match_unique_id(f"https://x.com{redirect}")
                if redirect.startswith("/")
                else None
            )
            if unique_id:
                return unique_id
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

    @classmethod
    async def get_all_unique_ids(
        cls, urls: list, proxies: Optional[dict] = None
    ) -> list:
        """
        从用户URL列表中提取所有用户唯一ID
        (Extract all unique ids from the list of user URLs)

        Args:
            urls (list): 用户URL列表 (List of user URLs)
            proxies (dict): 调用方的代理配置，没有配置代理时使用客户端配置中的代理 (Proxies of the caller)

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

        unique_ids = [cls.get_unique_id(url, proxies) for url in urls]
        return await asyncio.gather(*unique_ids)


class TweetIdFetcher(BaseCrawler):
    # 预编译正则表达式
    _TWEET_URL_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?(?:twitter|x)\.com/.*/status/(\d+)(?:/|\?|#.*$|$)"
    )

    proxies = ClientConfManager.proxies()

    def __init__(self, proxies: Optional[dict] = None):
        # 应用配置或 --proxies 中的代理优先，没有配置时使用客户端配置中的代理
        super().__init__(proxies=prefer_proxies(proxies, self.proxies))

    @classmethod
    async def get_tweet_id(cls, url: str, proxies: Optional[dict] = None) -> str:
        """
        从推文URL中提取推文ID
        (Extract tweet ID from tweet URL)

        Args:
            url (str): 推文URL (Tweet URL)
            proxies (dict): 调用方的代理配置，没有配置代理时使用客户端配置中的代理 (Proxies of the caller)

        Returns:
            str: 推文ID (Tweet ID)
        """

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        extracted_url = extract_valid_urls(url)

        if extracted_url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))
        url = extracted_url

        # 创建一个实例以访问 aclient
        instance = cls(proxies)

        # 解析URL并检查主机
        parsed_url = urlparse(url)
        host = parsed_url.hostname

        if host is None:
            raise APINotFoundError(
                _("无法解析URL的主机部分。类名：{0}").format(cls.__name__)
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
    async def get_all_tweet_ids(
        cls, urls: list, proxies: Optional[dict] = None
    ) -> list:
        """
        从推文URL列表中提取所有推文ID
        (Extract all tweet IDs from the list of tweet URLs)

        Args:
            urls (list): 推文URL列表 (List of tweet URLs)
            proxies (dict): 调用方的代理配置，没有配置代理时使用客户端配置中的代理 (Proxies of the caller)

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

        tweet_ids = [cls.get_tweet_id(url, proxies) for url in urls]
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

    if not naming_template:
        raise InvalidConfError(key="naming", value=naming_template)

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
        raise KeyError(_("文件名模板字段 {0} 不存在，请检查").format(e))


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

    Note:
        昵称变化时，把各下载模式下旧昵称的目录都重命名为新昵称，已下载的文件随目录保留；
        某个模式下新昵称的目录已存在时，该模式的两个目录都保持不变。
        (When the nickname changes, the folders of the old nickname are renamed to the
        new nickname in every download mode, keeping the downloaded files; in a mode
        where a folder of the new nickname already exists, both folders are left as
        they are.)
    """
    local_nickname = local_user_data.get("nickname") if local_user_data else None

    if local_nickname and current_nickname and local_nickname != current_nickname:
        # 昵称不一致，把各下载模式下旧昵称的目录重命名为新昵称
        user_path = migrate_user_folders(
            kwargs, "twitter", local_nickname, current_nickname
        )
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path

    return create_user_folder(kwargs, current_nickname)


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

    # 获取绝对路径，与重命名用户目录时的路径计算一致
    user_path = get_user_folder_path(kwargs, "twitter", nickname)

    # 创建目录
    user_path.mkdir(parents=True, exist_ok=True)

    return user_path


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


def sort_mp4_urls(variants: Any) -> List[str]:
    """
    从视频变体中取出 MP4 链接，按码率从低到高排列，最后一个清晰度最高。

    变体里还有 application/x-mpegURL 的 m3u8 播放列表，它不是视频文件，
    直接保存会得到只有几 KB 的文本（#436）；接口返回的顺序也不保证按码率排列。

    Args:
        variants (Any): 单个变体字典，或变体字典的列表

    Returns:
        List[str]: MP4 链接列表
    """
    if isinstance(variants, dict):
        variants = [variants]
    mp4_variants = [
        variant
        for variant in variants or []
        if isinstance(variant, dict)
        and variant.get("content_type") == "video/mp4"
        and variant.get("url")
    ]
    mp4_variants.sort(key=lambda variant: variant.get("bitrate") or 0)
    return [variant["url"] for variant in mp4_variants]


def best_mp4_url(variants: Any) -> Optional[str]:
    """返回码率最高的 MP4 链接，没有 MP4 时返回 None"""
    urls = sort_mp4_urls(variants)
    return urls[-1] if urls else None


# 视频与动图的媒体类型，动图（GIF）在接口中也是 MP4 视频
VIDEO_MEDIA_TYPES = ("video", "animated_gif")


def media_items(media_list: Any) -> List[dict]:
    """
    取出推文中每个媒体的类型与下载链接
    (Get the type and download link of each media in a tweet)

    图片取 media_url_https，视频与动图取码率最高的 MP4。一条推文可以同时包含图片与视频，
    也可以有多个视频，需要逐个下载。

    Args:
        media_list (Any): extended_entities.media 或 entities.media

    Returns:
        List[dict]: [{"type": 媒体类型, "url": 下载链接}]，没有可用链接时 url 为 None
    """
    items = []
    for media in media_list if isinstance(media_list, list) else []:
        if not isinstance(media, dict):
            continue
        media_type = media.get("type")
        if media_type in VIDEO_MEDIA_TYPES:
            url = best_mp4_url((media.get("video_info") or {}).get("variants"))
        else:
            url = media.get("media_url_https")
        items.append({"type": media_type, "url": url})
    return items


def tweet_created_at_to_timestamp(created_at: Any) -> Optional[int]:
    """
    将推文的发布时间转换为秒级时间戳
    (Convert the publish time of a tweet to a UNIX timestamp in seconds)

    Args:
        created_at (Any): 发布时间，如 "Wed Oct 01 16:36:07 +0000 2026"

    Returns:
        Optional[int]: 秒级时间戳，无法解析时返回 None
    """
    if not isinstance(created_at, str):
        return None
    try:
        return int(
            datetime.strptime(created_at.strip(), "%a %b %d %H:%M:%S %z %Y").timestamp()
        )
    except ValueError:
        return None


def tweet_full_text(result: Any) -> str:
    """
    推文的完整文案，用于保存 desc.txt
    (The complete text of a tweet, saved to desc.txt)

    - 长推文（超过 280 字）的 legacy.full_text 只有前 279 个字，完整内容在 note_tweet 中
    - 转推取原推文的完整内容，保留 "RT @用户名: " 前缀
    - t.co 短链接换成原始链接；指向推文媒体本身的短链接去掉，媒体会单独下载
    - 还原 &amp; 等 HTML 转义

    文件名中的 {desc} 仍由 extract_desc 生成，取第一个链接之前的内容，不受影响。

    Args:
        result (Any): 推文数据，即 tweet_results.result (Tweet result)

    Returns:
        str: 完整文案，不是推文时为空字符串 (Complete text, empty when not a tweet)
    """
    if not isinstance(result, dict):
        return ""
    legacy = result.get("legacy") or {}

    retweeted = (legacy.get("retweeted_status_result") or {}).get("result")
    if isinstance(retweeted, dict) and retweeted.get("legacy"):
        author = (retweeted.get("core") or {}).get("user_results") or {}
        screen_name = ((author.get("result") or {}).get("legacy") or {}).get(
            "screen_name"
        )
        text = tweet_full_text(retweeted)
        return f"RT @{screen_name}: {text}" if screen_name else text

    note = ((result.get("note_tweet") or {}).get("note_tweet_results") or {}).get(
        "result"
    ) or {}
    if isinstance(note, dict) and note.get("text"):
        text = note["text"]
        urls = (note.get("entity_set") or {}).get("urls") or []
    else:
        text = legacy.get("full_text") or ""
        urls = (legacy.get("entities") or {}).get("urls") or []

    for url in urls:
        if isinstance(url, dict) and url.get("url") and url.get("expanded_url"):
            text = text.replace(url["url"], url["expanded_url"])
    media = (legacy.get("extended_entities") or legacy.get("entities") or {}).get(
        "media"
    ) or []
    for item in media:
        if isinstance(item, dict) and item.get("url"):
            text = text.replace(item["url"], "")
    return html.unescape(text).strip()


def extract_desc(text):
    """
    提取推特标题，抛弃从 "https" 开始及其后的内容，包括其前一个空格。

    Args:
        text (str): 原始推文内容

    Returns:
        str: 提取后的标题
    """

    # 部分推文的 full_text 为 null（#436、#404）
    if not text:
        return ""

    text = text.strip()  # 去掉两端空格
    https_index = text.find("https")  # 查找 "https" 的起始位置

    if https_index != -1:  # 如果存在 "https"
        # 找到 "https" 前第一个空格的位置
        cutoff_index = text.rfind(" ", 0, https_index)
        if cutoff_index != -1:
            return text[:cutoff_index].strip()  # 返回截断后的部分
    return text.strip()  # 如果没有 "https"，返回去掉两端空格后的内容


class GraphQLOperation(NamedTuple):
    """网页脚本中定义的 GraphQL 查询 (A GraphQL operation defined in X's web scripts)"""

    query_id: str
    features: Tuple[str, ...] = ()
    # 被替换的内置 queryId：F2 更新内置值后，替换旧值的缓存记录不再使用
    replaces: str = ""


# 网页脚本中的查询定义，例如：
# {queryId:"KybxDj9RrADIITXlGG8kpw",operationName:"UserByScreenName",
#  operationType:"query",metadata:{featureSwitches:["..."],fieldToggles:["..."]}}
_OPERATION_PATTERN = re.compile(
    r'queryId:"(?P<query_id>[\w-]+)",operationName:"(?P<name>\w+)",'
    r'operationType:"\w+"(?:,metadata:\{featureSwitches:\[(?P<features>[^\]]*)\])?'
)
# 已登录页面加载的入口脚本
_MAIN_SCRIPT_PATTERN = re.compile(
    r"https://abs\.twimg\.com/responsive-web/client-web[\w-]*/main\.\w+\.js"
)
# webpack 运行时中按需加载的脚本：编号到名称、编号到哈希的两张表，例如
# (({34778:"shared~bundle.BookmarkFolders~bundle.Bookmarks"})[e]||e)+"."
# +({34778:"0b251bfed83c436a"})[e]+"a.js"
_CHUNK_MAP_PATTERN = re.compile(
    r'\(\{(?P<names>[^{}]*)\}\)\[\w+\]\|\|\w+\)\+"\."\+'
    r'\(\{(?P<hashes>[^{}]*)\}\)\[\w+\]\+"(?P<suffix>[\w.]*\.js)"'
)
_CHUNK_ENTRY_PATTERN = re.compile(r'(\w+):"([^"]+)"')


def graphql_cache_path() -> Path:
    """从网页脚本中获取的 queryId 的缓存文件 (~/.f2/cache/twitter_graphql.json)"""
    return user_config.user_config_dir() / "cache" / "twitter_graphql.json"


def load_graphql_cache() -> Dict[str, GraphQLOperation]:
    """
    读取缓存的查询，文件不存在或无法解析时返回空字典
    (Load cached operations; an empty dict when the file is missing or invalid)

    Returns:
        Dict[str, GraphQLOperation]: 以查询名为键 (Keyed by operation name)
    """
    path = graphql_cache_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as e:
        logger.debug(_("无法读取推特接口的 queryId 缓存 {0}：{1}").format(path, e))
        return {}

    entries = data.get("operations") if isinstance(data, dict) else None
    operations: Dict[str, GraphQLOperation] = {}
    for name, entry in entries.items() if isinstance(entries, dict) else []:
        if not isinstance(entry, dict):
            continue
        query_id, replaces = entry.get("query_id"), entry.get("replaces")
        if isinstance(query_id, str) and isinstance(replaces, str):
            features = entry.get("features")
            operations[name] = GraphQLOperation(
                query_id,
                (
                    tuple(f for f in features if isinstance(f, str))
                    if isinstance(features, list)
                    else ()
                ),
                replaces,
            )
    return operations


def save_graphql_cache(operations: Dict[str, GraphQLOperation]) -> Optional[Path]:
    """
    把查询写入缓存文件，先写临时文件再替换，多个进程同时写入时不会写出半个文件
    (Write operations to the cache file atomically)

    缓存只是为了省去内置值失效后每次运行的重复获取，写入失败时只记录警告。

    Returns:
        Optional[Path]: 缓存文件路径，写入失败时为 None
    """
    path = graphql_cache_path()
    data = {
        "updated_at": int(time.time()),
        "operations": {
            name: {
                "query_id": operation.query_id,
                "replaces": operation.replaces,
                "features": list(operation.features),
            }
            for name, operation in sorted(operations.items())
        },
    }
    temp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        os.replace(temp, path)
    except OSError as e:
        logger.warning(_("无法保存推特接口的 queryId 缓存 {0}：{1}").format(path, e))
        with contextlib.suppress(OSError):
            temp.unlink(missing_ok=True)
        return None
    return path


def parse_graphql_operations(script: str) -> Dict[str, GraphQLOperation]:
    """
    从网页脚本中读取 GraphQL 查询的 queryId 与所需的功能开关
    (Read queryIds and feature switches of GraphQL operations from a web script)

    Args:
        script (str): 脚本内容 (Script content)

    Returns:
        Dict[str, GraphQLOperation]: 以查询名为键 (Keyed by operation name)
    """
    return {
        match["name"]: GraphQLOperation(
            match["query_id"],
            tuple(re.findall(r'"([^"]+)"', match["features"] or "")),
        )
        for match in _OPERATION_PATTERN.finditer(script or "")
    }


def find_main_script(html: str) -> Optional[str]:
    """从 x.com 已登录的页面中找到入口脚本 main.js 的地址"""
    match = _MAIN_SCRIPT_PATTERN.search(html or "")
    return match.group(0) if match else None


def find_chunk_scripts(
    html: str, main_script: str, keywords: Iterable[str]
) -> List[str]:
    """
    找到名称包含关键字的按需加载脚本，按名称从短到长排列
    (Find on-demand scripts whose names contain any keyword, shortest name first)

    收藏等接口的查询不在 main.js 中，而在 shared~bundle.BookmarkFolders~bundle.Bookmarks
    这样按需加载的脚本里。

    Args:
        html (str): x.com 已登录的页面 (Logged-in x.com page)
        main_script (str): 入口脚本地址，按需加载的脚本与它在同一目录 (URL of main.js)
        keywords (Iterable[str]): 名称中的关键字，如查询名 (Keywords such as the operation name)

    Returns:
        List[str]: 脚本地址 (Script URLs)
    """
    match = _CHUNK_MAP_PATTERN.search(html or "")
    if not match:
        return []
    names = dict(_CHUNK_ENTRY_PATTERN.findall(match["names"]))
    hashes = dict(_CHUNK_ENTRY_PATTERN.findall(match["hashes"]))
    base = main_script.rsplit("/", 1)[0]
    keywords = [keyword for keyword in keywords if keyword]
    chunks = sorted(
        (
            (name, chunk_id)
            for chunk_id, name in names.items()
            if chunk_id in hashes and any(keyword in name for keyword in keywords)
        ),
        key=lambda chunk: (len(chunk[0]), chunk[0]),
    )
    return [
        f"{base}/{name}.{hashes[chunk_id]}{match['suffix']}"
        for name, chunk_id in chunks
    ]

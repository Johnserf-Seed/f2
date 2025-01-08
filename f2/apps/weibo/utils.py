# path: f2/apps/weibo/utils.py

import f2
import re
import httpx
import asyncio

from typing import Union
from pathlib import Path
from urllib.parse import unquote

from f2.i18n.translator import _
from f2.log.logger import logger
from f2.utils.conf_manager import ConfigManager
from f2.utils.utils import extract_valid_urls, split_filename, split_set_cookie
from f2.crawlers.base_crawler import BaseCrawler
from f2.exceptions.api_exceptions import (
    APIConnectionError,
    APIResponseError,
    APIUnavailableError,
    APIUnauthorizedError,
    APINotFoundError,
)


class ClientConfManager:
    """
    用于管理客户端配置 (Used to manage client configuration)
    """

    client_conf = ConfigManager(f2.F2_CONFIG_FILE_PATH).get_config("f2")
    weibo_conf = client_conf.get("weibo", {})

    @classmethod
    def client(cls) -> dict:
        return cls.weibo_conf

    @classmethod
    def conf_version(cls) -> str:
        return cls.client_conf.get("version", "unknown")

    @classmethod
    def proxies(cls) -> dict:
        return cls.weibo_conf.get("proxies", {})

    @classmethod
    def visitor(cls) -> dict:
        return cls.weibo_conf.get("visitor", {})

    @classmethod
    def headers(cls) -> dict:
        return cls.weibo_conf.get("headers", {})

    @classmethod
    def user_agent(cls) -> str:
        return cls.headers().get("User-Agent", "")

    @classmethod
    def referer(cls) -> str:
        return cls.headers().get("Referer", "")


class ModelManager:

    @classmethod
    def model_2_endpoint(cls, base_endpoint: str, params: dict = ...) -> str:
        if not params:
            return base_endpoint

        if not isinstance(params, dict):
            raise ValueError("参数必须是字典类型")

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}"

        return final_endpoint


class VisitorManager(BaseCrawler):
    """
    用于管理访客Cookie生成 (Used to manage visitor information)
    """

    visitor_conf = ClientConfManager.visitor()
    proxies = ClientConfManager.proxies()

    visitor_headers = {
        "User-Agent": ClientConfManager.user_agent(),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    def __init__(self):
        super().__init__(proxies=self.proxies)

    @classmethod
    async def gen_visitor(cls) -> str:
        """
        生成访客Cookie (Generate visitor information)

        Args:
            kwargs (dict): 配置参数 (Conf parameters)

        Returns:
            str: 访客cookie (Visitor cookie)
        """

        instance = cls()

        try:
            payload = {
                "cb": instance.visitor_conf["cb"],
                "tid": instance.visitor_conf["tid"],
                "from": instance.visitor_conf["from"],
            }

            response = await instance.aclient.post(
                instance.visitor_conf["url"],
                data=payload,
                headers=instance.visitor_headers,
            )
            response.raise_for_status()

            visitor_cookie = split_set_cookie(response.headers.get("set-cookie", ""))
            return visitor_cookie

        except httpx.RequestError as exc:
            # 捕获所有与 httpx 请求相关的异常情况 (Captures all httpx request-related exceptions)
            raise APIConnectionError(
                _(
                    "请求端点失败，请检查当前网络环境。 链接：{0}，代理：{1}，异常类名：{2}，异常详细信息：{3}"
                ).format(
                    instance.visitor_conf["url"],
                    instance.proxies,
                    instance.__name__,
                    exc,
                )
            )

        except httpx.HTTPStatusError as e:
            # 捕获 httpx 的状态代码错误 (captures specific status code errors from httpx)
            if e.response.status_code == 401:
                raise APIUnauthorizedError(
                    _(
                        "参数验证失败，请更新 F2 配置文件中的 {0}，以匹配 {1} 新规则"
                    ).format("visitor", "weibo")
                )

            elif e.response.status_code == 404:
                raise APINotFoundError(_("{0} 无法找到API端点").format("visitor"))
            else:
                raise APIResponseError(
                    _("链接：{0}，状态码 {1}：{2} ").format(
                        str(e.response.url), e.response.status_code, e.response.text
                    )
                )


class WeiboIdFetcher:
    # 预编译正则表达式
    # (Pre-compile regular expression)

    # weibo.com/2265830070/O8DM0BLLm
    # https://weibo.com/2265830070/O8DM0BLLm
    # https://weibo.com/2265830070/O8DM0BLLm/
    # https://weibo.com/2265830070/O8DM0BLLm/?test=123

    # https://www.weibo.com/2265830070/5020595169001740
    # https://www.weibo.com/2265830070/5020595169001740?test=123
    # https://www.weibo.com/2265830070/5020595169001740/
    # https://www.weibo.com/2265830070/5020595169001740/?test=123
    # www.weibo.com/2265830070/5020595169001740
    _WEIBO_ID_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?(?:weibo\.com|weibo\.cn|m\.weibo\.cn)/(?:\d{10}|status)/(\w{9}|\w{16})(?:/|\?|#.*$|$)"
    )

    @classmethod
    async def get_weibo_id(cls, url: str) -> str:
        """
        从微博链接中提取微博ID
        (Extract weibo ID from weibo link)

        Args:
            url (str): 微博链接 (weibo link)

        Returns:
            str: 微博ID (weibo ID)
        """

        if not url:
            raise ValueError(_("微博链接不能为空"))

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        url = extract_valid_urls(url)

        if url is None:
            raise APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))

        match = cls._WEIBO_ID_PATTERN.search(url)

        if match:
            return match.group(1)
        else:
            raise APINotFoundError(
                _(
                    "未在响应的地址中找到weibo_id，检查链接是否为微博链接。类名：{0}"
                ).format(cls.__name__)
            )

    @classmethod
    async def get_all_weibo_id(cls, urls: list) -> list:
        """
        从微博链接列表中提取微博ID
        (Extract weibo ID from weibo link)

        Args:
            urls (list): 微博链接 (Weibo link list)

        Returns:
            list: 微博ID列表 (Weibo ID list)
        """

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        # 从链接中提取微博ID
        if urls == []:
            raise (
                APINotFoundError(
                    _("输入的URL List不合法。类名：{0}").format(cls.__name__)
                )
            )

        weibo_ids = [cls.get_weibo_id(url) for url in urls]
        return await asyncio.gather(*weibo_ids)


class WeiboUidFetcher:
    # 预编译正则表达式
    # (Pre-compile regular expression)

    # https://weibo.com/u/2265830070
    # https://weibo.com/u/2265830070/
    # https://weibo.com/u/2265830070?test=123
    # https://weibo.com/2265830070
    # https://weibo.com/2265830070?test=123
    # https://weibo.com/2265830070/
    # https://weibo.com/2265830070/?test=123
    _WEIBO_COM_UID_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?(?:weibo\.com|weibo\.cn|m\.weibo\.cn)/(?:u/)?(\d{10})(?:/|\?|$)"
    )

    @classmethod
    async def get_weibo_uid(cls, url: str) -> str:
        """
        从微博主页链接中提取微博UID
        (Extract weibo UID from weibo link)

        Args:
            url (str): 微博链接 (Weibo link)

        Returns:
            str: 微博UID (Weibo UID)
        """

        if not url:
            raise ValueError(_("微博主页链接不能为空"))

        if not isinstance(url, str):
            raise TypeError(_("参数必须是字符串类型"))

        # 提取有效URL
        url = extract_valid_urls(url)

        if url is None:
            raise (
                APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))
            )

        match = cls._WEIBO_COM_UID_PATTERN.search(url)
        if match:
            return match.group(1)
        else:
            raise APINotFoundError(
                _(
                    "未在响应的地址中找到weibo_uid，检查链接是否为微博主页链接。类名：{0}"
                ).format(cls.__name__)
            )

    @classmethod
    async def get_all_weibo_uid(cls, urls: list) -> list:
        """
        从微博主页链接列表中提取微博UID
        (Extract weibo UID from weibo link)

        Args:
            urls (list): 微博链接 (Weibo link list)

        Returns:
            list: 微博UID列表 (Weibo UID list)
        """

        if not urls:
            raise ValueError(_("微博链接列表不能为空"))

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        # 从链接中提取微博ID
        if urls == []:
            raise (
                APINotFoundError(
                    _("输入的URL List不合法。类名：{0}").format(cls.__name__)
                )
            )

        weibo_uids = [cls.get_weibo_uid(url) for url in urls]
        return await asyncio.gather(*weibo_uids)


class WeiboScreenNameFetcher:
    # 预编译正则表达式
    # (Pre-compile regular expression)

    # https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1
    # https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1/
    # https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1?test=123
    # https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1/?test=123
    # https://weibo.com/n/自我充电功能丧失
    # https://weibo.com/n/自我充电功能丧失/
    # https://weibo.com/n/自我充电功能丧失?test=123
    # https://weibo.com/n/自我充电功能丧失/?test=123

    _WEIBO_COM_NAME_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?(?:weibo\.com|weibo\.cn|m\.weibo\.cn)/n/([^/?#]+)"
    )

    @classmethod
    async def get_weibo_screen_name(cls, url: str) -> str:
        """
        从微博链接中提取URL编码的昵称并解码
        (Extract encoded name from weibo link and decode it)

        Args:
            url (str): 微博链接 (Weibo link)

        Returns:
            str: 解码后的微博名称 (Decoded Weibo name)
        """
        if not url:
            raise ValueError("微博链接不能为空")

        if not isinstance(url, str):
            raise TypeError("参数必须是字符串类型")

        # 提取有效URL
        url = extract_valid_urls(url)

        if url is None:
            raise (
                APINotFoundError(_("输入的URL不合法。类名：{0}").format(cls.__name__))
            )

        match = cls._WEIBO_COM_NAME_PATTERN.search(url)
        if match:
            # URL解码
            return unquote(match.group(1))
        else:
            raise APINotFoundError(
                _(
                    "未在响应的地址中找到screen_name，检查链接是否为微博昵称链接。类名：{0}"
                ).format(cls.__name__)
            )

    @classmethod
    async def get_all_weibo_screen_name(cls, urls: list) -> list:
        """
        从微博链接列表中提取URL编码的昵称并解码
        (Extract encoded name from weibo link list and decode it)

        Args:
            urls (list): 微博链接 (Weibo link list)

        Returns:
            list: 解码后的微博名称列表 (Decoded Weibo name list)
        """
        if not urls:
            raise ValueError(_("微博链接列表不能为空"))

        if not isinstance(urls, list):
            raise TypeError(_("参数必须是列表类型"))

        # 提取有效URL
        urls = extract_valid_urls(urls)

        # 从链接中提取微博ID
        if urls == []:
            raise (
                APINotFoundError(
                    _("输入的URL List不合法。类名：{0}").format(cls.__name__)
                )
            )

        weibo_screen_names = [cls.get_weibo_screen_name(url) for url in urls]
        return await asyncio.gather(*weibo_screen_names)


def format_file_name(
    naming_template: str,
    weibo_data: dict = {},
    custom_fields: dict = {},
) -> str:
    """
    根据配置文件的全局格式化文件名
    (Format file name according to the global conf file)

    Args:
        naming_template (str): 文件的命名模板, 如 "{create}_{desc}" (Naming template for files, such as "{create}_{desc}")
        weibo_data (dict): 微博数据的字典 (dict of weibo data)
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
        "create": weibo_data.get("weibo_created_at", ""),  # 长度固定19
        "nickname": weibo_data.get("nickname", ""),  # 最长30
        "weibo_id": weibo_data.get("weibo_id", ""),  # 长度固定19
        "desc": split_filename(weibo_data.get("weibo_desc", ""), os_limit),
        "uid": weibo_data.get("uid", ""),  # 固定10
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
        base_path / "weibo" / kwargs.get("mode", "PLEASE_SETUP_MODE") / str(nickname)
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
    提取微博标题，抛弃从 "http" 开始及其后的内容，包括其前一个空格。

    Args:
        text (str): 原始微博内容

    Returns:
        str: 提取后的标题
    """

    text = text.strip()  # 去掉两端空格
    http_index = text.find("http")  # 查找 "http" 的起始位置

    if http_index != -1:  # 如果存在 "http"
        # 找到 "http" 前第一个空格的位置
        cutoff_index = text.rfind(" ", 0, http_index)
        if cutoff_index != -1:
            return text[:cutoff_index].strip()  # 返回截断后的部分
    return text.strip()  # 如果没有 "http"，返回去掉两端空格后的内容

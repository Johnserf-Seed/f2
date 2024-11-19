# path: f2/utils/utils.py

import f2
import re
import sys
import httpx
import random
import asyncio
import secrets
import datetime
import traceback
import browser_cookie3
import importlib_resources

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from typing import Any, Dict, List, Union

from f2.log.logger import logger
from f2.i18n.translator import _

# 生成一个 16 字节的随机字节串 (Generate a random byte string of 16 bytes)
seed_bytes = secrets.token_bytes(16)

# 将字节字符串转换为整数 (Convert the byte string to an integer)
seed_int = int.from_bytes(seed_bytes, "big")

# 设置随机种子 (Seed the random module)
random.seed(seed_int)


def gen_random_str(randomlength: int) -> str:
    """
    根据传入长度产生随机字符串 (Generate a random string based on the given length)

    Args:
        randomlength (int): 需要生成的随机字符串的长度 (The length of the random string to be generated)

    Returns:
        str: 生成的随机字符串 (The generated random string)
    """

    base_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
    return "".join(random.choice(base_str) for _ in range(randomlength))


def get_timestamp(unit: str = "milli") -> int:
    """
    根据给定的单位获取当前时区的时间戳 (Get the current time based on the given unit)

    Args:
        unit (str): 时间单位，可以是 "milli"、"sec"、"min" 等
            (The time unit, which can be "milli", "sec", "min", etc.)

    Returns:
        int: 根据给定单位的当前时间 (The current time based on the given unit)
    """

    now = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime(
        1970, 1, 1, tzinfo=datetime.timezone.utc
    )
    if unit == "milli":
        return int(now.total_seconds() * 1000)
    elif unit == "sec":
        return int(now.total_seconds())
    elif unit == "min":
        return int(now.total_seconds() / 60)
    else:
        raise ValueError(_("不支持的时间单位：{0}").format(unit))


def timestamp_2_str(
    timestamp: Union[str, int, float, list],
    format: str = "%Y-%m-%d %H-%M-%S",
    tz: datetime.timezone = datetime.timezone(datetime.timedelta(hours=8)),
) -> Union[str, int, float, list]:
    """
    将 UNIX 时间戳转换为东八区北京时间格式化字符串使用

    Args:
        timestamp (Union[str, int, float, list]): 要转换的 UNIX 时间戳
        format (str, optional): 返回的日期时间字符串的格式，默认为 '%Y-%m-%d %H-%M-%S'。
        tz (datetime.timezone, optional): 时区，默认为东八区北京时间

    Returns:
        Union[str, int, float, list]: 格式化的日期时间字符串
    """

    # 处理空或无效时间戳
    if timestamp in [None, "None"]:
        return _("Invalid timestamp")

    if timestamp in [0, "0"]:
        return datetime.datetime.now(tz=tz).strftime(format)

    # 递归处理列表中的时间戳
    def convert(ts):
        if isinstance(ts, str):
            # 处理类似 "Wed Jun 01 10:23:01 +0800 2022" 的格式
            if len(ts) == 30:
                return datetime.datetime.strptime(ts, "%a %b %d %H:%M:%S %z %Y")
            else:
                try:
                    timestamp_value = float(ts)
                    if timestamp_value > 1e10:
                        timestamp_value /= 1000
                    return datetime.datetime.fromtimestamp(timestamp_value, tz=tz)
                except ValueError:
                    raise TypeError(_("无效的时间戳字符串: {0}").format(ts))
        elif isinstance(ts, (int, float)):
            timestamp_value = float(ts)
            if timestamp_value > 1e10:
                timestamp_value /= 1000
            return datetime.datetime.fromtimestamp(timestamp_value, tz=tz)
        else:
            raise TypeError(_("不支持的时间戳类型: {0}").format(type(ts)))

    # 如果是列表，则递归处理每个时间戳
    if isinstance(timestamp, list):
        return [
            (
                convert(ts).strftime(format)
                if not isinstance(ts, list)
                else [convert(t).strftime(format) for t in ts]
            )
            for ts in timestamp
        ]

    # 处理单个时间戳
    return convert(timestamp).strftime(format)


def str_2_timestamp(
    date_str: str,
    format: str = "%Y-%m-%d %H-%M-%S",
    unit: str = "milli",
    tz: datetime.timezone = datetime.timezone(datetime.timedelta(hours=8)),
) -> int:
    """
    将日期时间字符串转换为 UNIX 时间戳

    Args:
        date_str (str): 要转换的日期时间字符串 (The date-time string to be converted)
        format (str, optional): 日期时间字符串的格式，默认为 '%Y-%m-%d %H-%M-%S'。
                                (The format for the date-time string, defaults to '%Y-%m-%d %H-%M-%S')
        unit (str, optional): 时间单位，默认为 'milli'。 (The time unit, defaults to 'milli')
        tz (datetime.timezone, optional): 时区，默认为东八区北京时间 (The timezone, defaults to UTC+8)

    Returns:
        int: UNIX 时间戳 (The UNIX timestamp)
    """

    date_obj = datetime.datetime.strptime(date_str, format)
    if unit == "milli":
        return int(date_obj.replace(tzinfo=tz).timestamp() * 1000)
    elif unit == "sec":
        return int(date_obj.replace(tzinfo=tz).timestamp())
    elif unit == "min":
        return int(date_obj.replace(tzinfo=tz).timestamp() / 60)
    else:
        raise ValueError(_("不支持的时间单位：{0}").format(unit))


def interval_2_timestamp(
    interval: str,
    date_type: str = "start",
    format: str = "%Y-%m-%d %H-%M-%S",
    unit: str = "milli",
    tz: datetime.timezone = datetime.timezone(datetime.timedelta(hours=8)),
) -> int:
    """
    将日期区间字符串转换为 UNIX 时间戳

    Args:
        interval (str): 日期区间字符串，格式为 '2022-01-01|2023-01-01' (The date range string, formatted as '2022-01-01|2023-01-01')
        date_type (str, optional): 'start' 表示使用开始日期，'end' 表示使用结束日期 (Whether to use the start or end date, defaults to 'start')
        format (str, optional): 日期字符串的格式，默认为 '%Y-%m-%d' (The date string format, defaults to '%Y-%m-%d')
        unit (str, optional): 时间单位，默认为 'milli' (The time unit, defaults to 'milli')
        tz (datetime.timezone, optional): 时区，默认为东八区北京时间 (The timezone, defaults to UTC+8)

    Returns:
        int: UNIX 时间戳 (The UNIX timestamp)
    """

    if not interval:
        logger.warning(_("日期区间为空，无法转换为时间戳"))
        return 0

    try:
        start_date, end_date = interval.split("|")
        if date_type == "start":
            date_str = f"{start_date} 00-00-00"
        elif date_type == "end":
            date_str = f"{end_date} 23-59-59"
        else:
            logger.warning(_("不支持的日期类型：{0}").format(date_type))
            return 0

        return str_2_timestamp(date_str, format, unit, tz)
    except ValueError:
        logger.error(_("日期区间参数格式错误，请查阅文档后重试"))
        logger.error(traceback.format_exc())
    return 0


def split_set_cookie(cookie_str: str) -> str:
    """
    拆分Set-Cookie字符串并拼接 (Split the Set-Cookie string and concatenate)

    Args:
        cookie_str (str): 待拆分的Set-Cookie字符串 (The Set-Cookie string to be split)

    Returns:
        str: 拼接后的Cookie字符串 (Concatenated cookie string)
    """

    if not isinstance(cookie_str, str):
        raise TypeError(_("cookie_str 参数应为字符串"))

    # 拆分Set-Cookie字符串,避免错误地在expires字段的值中分割字符串 (Split the Set-Cookie string, avoiding incorrect splitting on the value of the 'expires' field)
    # 拆分每个Cookie字符串，只获取第一个分段（即key=value部分） / Split each Cookie string, only getting the first segment (i.e., key=value part)
    # 拼接所有的Cookie (Concatenate all cookies)
    return ";".join(
        cookie.split(";")[0] for cookie in re.split(", (?=[a-zA-Z])", cookie_str)
    )


def split_dict_cookie(cookie_dict: Dict) -> str:
    """
    拆分Cookie字典并拼接 (Split the Cookie dictionary and concatenate)

    Args:
        cookie_dict (dict): 待拆分的Cookie字典 (The Cookie dictionary to be split)

    Returns:
        str: 拼接后的Cookie字符串 (Concatenated cookie string)
    """
    return "; ".join(f"{key}={value}" for key, value in cookie_dict.items())


def extract_valid_urls(inputs: Union[str, List[str]]) -> Union[str, List[str], None]:
    """
    从输入中提取有效的URL (Extract valid URLs from input)

    Args:
        inputs (Union[str, list[str]]): 输入的字符串或字符串列表 (Input string or list of strings)

    Returns:
        Union[str, list[str]]: 提取出的有效URL或URL列表 (Extracted valid URL or list of URLs)
    """
    url_pattern = re.compile(r"https?://\S+")

    # 如果输入是单个字符串
    if isinstance(inputs, str):
        match = url_pattern.search(inputs)
        return match.group(0) if match else None

    # 如果输入是字符串列表
    elif isinstance(inputs, list):
        valid_urls = []

        for input_str in inputs:
            matches = url_pattern.findall(input_str)
            if matches:
                valid_urls.extend(matches)

        return valid_urls


def _get_first_item_from_list(_list: List) -> List:
    """
    从列表中提取第一个项目 (Extract the first item from a list)

    .. deprecated:: 0.0.1.6
        `_get_first_item_from_list` 在 0.0.1.7 版本及之后将被移除。
        本方法不再有替代方案。 (This function will be removed in version 0.0.1.7 or later.
        No replacement will be provided.)

    Args:
        _list (List): 输入的列表 (Input list)

    Returns:
        List: 提取出的第一个项目 (The extracted first item)
    """
    import warnings

    warnings.warn(
        _(
            "_get_first_item_from_list is deprecated and will be removed in version 0.0.1.7. "
        ),
        _("No replacement will be provided."),
        DeprecationWarning,
        stacklevel=2,
    )
    # 检查是否是列表 (Check if it's a list)
    if _list and isinstance(_list, list):
        # 如果列表里第一个还是列表则提起每一个列表的第一个值
        # (If the first one in the list is still a list then bring up the first value of each list)
        if isinstance(_list[0], list):
            return [inner[0] for inner in _list if inner]
        # 如果只是普通列表，则返回这个列表包含的第一个项目作为新列表
        # (If it's just a regular list, return the first item wrapped in a list)
        else:
            return [_list[0]]
    return []


def get_resource_path(filepath: str) -> Path:
    """
    获取资源文件的路径 (Get the path of the resource file)

    Args:
        filepath: str: 文件路径 (file path)
    """

    return importlib_resources.files("f2") / filepath


def replaceT(obj: Union[str, Any]) -> Union[str, Any]:
    """
    替换文案非法字符 (Replace illegal characters in the text)

    Args:
        obj (str): 传入对象 (Input object)

    Returns:
        new: 处理后的内容 (Processed content)
    """

    reSub = r"[^\u4e00-\u9fa5a-zA-Z0-9#]"

    if isinstance(obj, list):
        return [re.sub(reSub, "_", i) if isinstance(i, str) else i or "" for i in obj]

    if isinstance(obj, str):
        return re.sub(reSub, "_", obj)

    return obj


def split_filename(text: str, os_limit: Dict) -> str:
    """
    根据操作系统的字符限制分割文件名，并用 '......' 代替。

    Args:
        text (str): 要计算的文本
        os_limit (dict): 操作系统的字符限制字典

    Returns:
        str: 分割后的文本
    """
    # 获取操作系统名称和文件名长度限制
    os_name = sys.platform
    filename_length_limit = os_limit.get(os_name, 200)

    # 计算中文字符长度（中文字符长度*3）
    chinese_length = sum(1 for char in text if "\u4e00" <= char <= "\u9fff") * 3
    # 计算英文字符长度
    english_length = sum(1 for char in text if char.isalpha())
    # 计算下划线数量
    num_underscores = text.count("_")

    # 计算总长度
    total_length = chinese_length + english_length + num_underscores

    # 如果总长度超过操作系统限制或手动设置的限制，则根据限制进行分割
    if total_length > filename_length_limit:
        split_index = min(total_length, filename_length_limit) // 2 - 6
        split_text = text[:split_index] + "......" + text[-split_index:]
        return split_text
    else:
        return text


def ensure_path(path: Union[str, Path]) -> Path:
    """确保路径是一个Path对象 (Ensure the path is a Path object)"""
    return Path(path) if isinstance(path, str) else path


def get_cookie_from_browser(browser_choice: str, domain: str = "") -> dict:
    """
    根据用户选择的浏览器获取domain的cookie。

    Args:
        browser_choice (str): 用户选择的浏览器名称

    Returns:
        str: *.domain的cookie值
    """

    if not browser_choice or not domain:
        return ""

    BROWSER_FUNCTIONS = {
        "chrome": browser_cookie3.chrome,
        "firefox": browser_cookie3.firefox,
        "edge": browser_cookie3.edge,
        "opera": browser_cookie3.opera,
        "opera_gx": browser_cookie3.opera_gx,
        "safari": browser_cookie3.safari,
        "chromium": browser_cookie3.chromium,
        "brave": browser_cookie3.brave,
        "vivaldi": browser_cookie3.vivaldi,
        "librewolf": browser_cookie3.librewolf,
    }
    cj_function = BROWSER_FUNCTIONS.get(browser_choice)
    cj = cj_function(domain_name=domain)
    cookie_value = {c.name: c.value for c in cj if c.domain.endswith(domain)}
    return cookie_value


def check_invalid_naming(
    naming: str, allowed_patterns: list, allowed_separators: list
) -> list:
    """
    检查命名是否符合命名模板 (Check if the naming conforms to the naming template)

    Args:
        naming (str): 命名字符串 (Naming string)
        allowed_patterns (list): 允许的模式列表 (List of allowed patterns)
        allowed_separators (list): 允许的分隔符列表 (List of allowed separators)
    Returns:
        list: 无效的模式列表 (List of invalid patterns)
    """
    if not naming or not allowed_patterns or not allowed_separators:
        return []

    temp_naming = naming
    invalid_patterns = []

    # 检查提供的模式是否有效
    for pattern in allowed_patterns:
        if pattern in temp_naming:
            temp_naming = temp_naming.replace(pattern, "")

    # 此时，temp_naming应只包含分隔符
    for char in temp_naming:
        if char not in allowed_separators:
            invalid_patterns.append(char)

    # 检查连续的无效模式或分隔符
    for pattern in allowed_patterns:
        # 检查像"{xxx}{xxx}"这样的模式
        if pattern + pattern in naming:
            invalid_patterns.append(pattern + pattern)
        for sep in allowed_patterns:
            # 检查像"{xxx}-{xxx}"这样的模式
            if pattern + sep + pattern in naming:
                invalid_patterns.append(pattern + sep + pattern)

    return invalid_patterns


def merge_config(
    main_conf: dict = ...,
    custom_conf: dict = ...,
    **kwargs,
):
    """
    合并配置参数，使 CLI 参数优先级高于自定义配置，自定义配置优先级高于主配置，最终生成完整配置参数字典。

    Args:
        main_conf (dict): 主配置参数字典
        custom_conf (dict): 自定义配置参数字典
        **kwargs: CLI 参数和其他额外的配置参数

    Returns:
        dict: 合并后的配置参数字典
    """
    # 合并主配置和自定义配置
    merged_conf = {}
    for key, value in main_conf.items():
        merged_conf[key] = value  # 将主配置复制到合并后的配置中
    for key, value in custom_conf.items():
        if value is not None and value != "":  # 只有值不为 None 和 空值，才进行合并
            merged_conf[key] = value  # 自定义配置参数会覆盖主配置中的同名参数

    # 合并 CLI 参数与合并后的配置，确保 CLI 参数的优先级最高
    for key, value in kwargs.items():
        if key not in merged_conf:  # 如果合并后的配置中没有这个键，则直接添加
            merged_conf[key] = value
        elif value is not None and value != "":  # 如果值不为 None 和 空值，则进行合并
            merged_conf[key] = value  # CLI 参数会覆盖自定义配置和主配置中的同名参数

    return merged_conf


def unescape_json(json_text: str) -> dict:
    """
    反转义 JSON 文本

    Args:
        json_text (str): 带有转义字符的 JSON 文本

    Returns:
        json_obj (dict): 反转义后的 JSON 对象
    """

    # 反转义 JSON 文本
    json_text = re.sub(r"\\{2}", r"\\", json_text)
    json_text = re.sub(r"\\\"", r"\"", json_text)
    json_text = re.sub(r"\\", r"", json_text)
    json_text = re.sub(r"\"{", r"{", json_text)
    json_text = re.sub(r"}\"", r"}", json_text)
    json_text = re.sub(r"\&", r"&", json_text)
    json_text = re.sub(r"\\n", r"", json_text)
    json_text = re.sub(r"\\t", r"", json_text)
    json_text = re.sub(r"\\r", r"", json_text)

    try:
        # 尝试解析 JSON 文本
        import json

        json_obj = json.loads(json_text)
    except Exception as e:
        print(f"`unescape_json` error: {e}, raw_json: {json_text}")
        json_obj = {}

    return json_obj


def check_python_version(min_version: tuple = (3, 9)) -> None:
    """
    检查当前 Python 版本是否满足最低要求

    Args:
        min_version (tuple, optional): 最低 Python 版本要求，默认为 (3, 9)

    Raises:
        SystemExit: 当 Python 版本不满足最低要求时，退出程序
    """

    console = Console()
    if sys.version_info < min_version:
        message = _("当前 Python 版本：{0} 不满足最低要求：{1}").format(
            sys.version.split()[0], ".".join(map(str, min_version))
        )
        panel = Panel(
            f"[bold red]{message}[/bold red]",
            title=_("[bold red]Python 版本错误[/bold red]"),
            border_style="red",
        )
        console.print(panel)
        sys.exit(1)


async def check_f2_version():
    """用于检查F2的版本是否最新"""

    latest_version = await get_latest_version("f2")

    if latest_version:
        if f2.__version__ > latest_version:
            message = _(
                "您当前使用的版本 {0} 可能已过时，请考虑及时升级到最新版本 {1}，"
                "使用 pip install -U f2 更新"
            ).format(f2.__version__, latest_version)
            Console().print(
                Panel(
                    message,
                    title=_("F2 低版本警告"),
                    subtitle=_("请及时更新"),
                    style="bold red",
                    border_style="red",
                )
            )
        elif f2.__version__ == latest_version:
            message = _("您当前使用的是最新版本：{0}").format(f2.__version__)
            Console().print(
                Panel(
                    message,
                    title=_("F2 版本检查"),
                    style="bold green",
                    border_style="green",
                )
            )
    else:
        message = _("无法获取最新版本信息")
        Console().print(
            Panel(
                message,
                title=_("F2 版本检查网络超时"),
                style="bold yellow",
                border_style="yellow",
            )
        )


async def get_latest_version(package_name: str) -> str:
    """
    获取 Python 包的最新版本号

    Args:
        package_name (str): Python 包名

    Returns:
        str: Python 包的最新版本号
    """
    async with httpx.AsyncClient(
        timeout=5.0,
        transport=httpx.AsyncHTTPTransport(retries=5),
        verify=False,
    ) as aclient:
        try:
            response = await aclient.get(f"{f2.PYPI_URL}/{package_name}/json")
            response.raise_for_status()
            package_data = response.json()
            latest_version = package_data["info"]["version"]
            return latest_version
        except asyncio.CancelledError:
            logger.warning(_("取消检查更新"))
        except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as e:
            logger.debug(traceback.format_exc())
            return None


class BaseEndpointManager:
    @classmethod
    def model_2_endpoint(cls, base_endpoint: str, params: dict) -> str:
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        separator = "&" if "?" in base_endpoint else "?"
        return f"{base_endpoint}{separator}{param_str}"


async def filter_by_date_interval(
    data: Union[List[Dict], Dict], interval: str
) -> Union[List[Dict], Dict, None]:
    """
    筛选指定日期区间内的作品

    Args:
        data (Union[List[Dict], Dict]): 作品列表或单个作品
        interval (str): 日期区间，格式：2022-01-01|2023-01-01

    Returns:
        filtered_data (Union[List[Dict], Dict, None]): 筛选后的作品列表或单个作品
    """

    def is_within_interval(item: Dict) -> bool:
        date_str = item.get("create_time")
        if not date_str:
            logger.warning(_("作品缺少创建时间：{0}").format(item))
            return False
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H-%M-%S")
        except ValueError:
            logger.warning(_("无法解析作品的创建时间：{0}").format(date_str))
            return False

        if date < start_date or date > end_date:
            return False

        return True

    if not data or not interval:
        logger.error(_("作品或日期区间为空"))
        return None

    try:
        start_str, end_str = interval.split("|")
        start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d") + datetime.timedelta(
            days=1, seconds=-1
        )

        if end_date < start_date:
            logger.error(_("结束日期早于开始日期，请检查日期区间"))
            return None

        # logger.info(_("筛选日期区间：{0} 至 {1}").format(start_date, end_date))
    except ValueError:
        logger.error(_("日期区间参数格式错误，请查阅文档后重试"))
        return None

    if isinstance(data, dict):
        if is_within_interval(data):
            return data
        else:
            logger.warning(
                _("作品创作时间不在筛选日期区间内：{0}").format(data.get("create_time"))
            )
            return None

    elif isinstance(data, list):
        filtered_list = [item for item in data if is_within_interval(item)]
        if filtered_list:
            logger.info(
                _("在 {0} 条作品中有 {1} 条作品符合筛选日期条件：{2}").format(
                    len(data), len(filtered_list), interval
                )
            )
        else:
            logger.warning(_("没有找到符合条件的作品"))
        return filtered_list


def check_proxy_avail(
    http_proxy: str,
    https_proxy: str,
    test_url: str = "https://www.google.com",
    expected_content: str = None,
    timeout: int = 5,
    method: str = "GET",
    **kwargs,
) -> bool:
    """
    检查 HTTP 和 HTTPS 代理是否可用

    Args:
        http_proxy (str): HTTP 代理地址 (例如 "http://proxy_ip:proxy_port")
        https_proxy (str): HTTPS 代理地址 (例如 "http://proxy_ip:proxy_port")
        test_url (str): 测试地址，默认 https://www.google.com
        expected_content (str): 预期的内容关键字，用于验证页面加载正确
        timeout (int): 请求超时时间，默认 5 秒
        method (str): 请求方法，如 "GET", "POST", "PUT", "DELETE", "OPTIONS"
        **kwargs: 其他请求参数，如 data, json, headers 等

    Returns:
        bool: 如果代理可用返回 True，否则返回 False
    """

    if not http_proxy or not https_proxy:
        logger.error(_("代理地址为空"))
        return False

    proxy_mounts = {
        "http://": httpx.HTTPTransport(proxy=http_proxy),
        "https://": httpx.HTTPTransport(proxy=https_proxy),
    }

    try:
        logger.info(_("正在测试代理服务器是否可用🚀"))
        # 创建 HTTP 和 HTTPS 的代理挂载
        with httpx.Client(timeout=timeout, mounts=proxy_mounts) as client:
            # 根据方法选择请求
            response = client.request(
                method.upper(),
                test_url,
                follow_redirects=True,
                **kwargs,
            )
            response.raise_for_status()

            # 验证响应内容是否包含预期关键字
            if expected_content and expected_content not in response.text:
                logger.warning(_("代理请求成功，但内容不符合预期"))
                return False

            logger.info("[green]代理请求成功，测试地址：{0}[/green]".format(test_url))
            return True

    except httpx.ProxyError as e:
        logger.error(_("代理错误：{0}").format(e))
    except httpx.TimeoutException as e:
        logger.error(_("代理请求超时，错误: {0}").format(e))
    except httpx.TooManyRedirects as e:
        logger.error(_("重定向次数过多：{0}").format(e))
    except httpx.HTTPStatusError as e:
        logger.error(
            _("代理请求 {0} 状态码错误：{1}").format(test_url, e.response.status_code)
        )
    except httpx.RequestError as e:
        logger.error(_("代理请求错误：{0}").format(e))
    except Exception as e:
        logger.error(_("代理请求失败：{0}").format(e))

    return False

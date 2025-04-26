# path: f2/utils/utils.py

import datetime
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import browser_cookie3  # type: ignore[import-untyped]
import importlib_resources
from rich.console import Console
from rich.panel import Panel

from f2.exceptions.api_exceptions import APIFilterError
from f2.i18n.translator import _
from f2.log.logger import logger


def get_resource_path(filepath: str) -> Path:
    """
    获取资源文件的路径 (Get the path of the resource file)

    Args:
        filepath: str: 文件路径 (file path)
    """

    return importlib_resources.files("f2") / filepath


def split_filename(text: str, os_limit: Dict[str, int]) -> str:
    """
    根据操作系统的字符限制分割文件名，并用 '......' 代替。
    前半部分是后半部分的两倍。

    Args:
        text (str): 要计算的文本
        os_limit (Dict[str, int]): 操作系统的字符限制

    Returns:
        str: 分割后的文本
    """
    # 获取操作系统名称和文件名长度限制
    os_name = sys.platform
    filename_length_limit = os_limit.get(os_name, 200)

    # 清理转义字符
    text = re.sub(r"\s+", " ", text).strip()

    # 计算文本的字节长度
    text_bytes = text.encode("utf-8")
    text_length = len(text_bytes)

    # 如果长度未超过限制，直接返回
    if text_length <= filename_length_limit:
        return text

    # 计算截断比例（2:1）
    split_index_first = (filename_length_limit - 6) * 2 // 3
    split_index_second = (filename_length_limit - 6) // 3

    # 截取前后部分
    first_part = text_bytes[:split_index_first].decode("utf-8", errors="ignore")
    second_part = text_bytes[-split_index_second:].decode("utf-8", errors="ignore")

    return f"{first_part}......{second_part}"


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
        return {}

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
    if not cj_function:
        logger.error(_("不支持的浏览器：{0}").format(browser_choice))
        return {}
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
    main_conf: dict,
    custom_conf: dict,
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

    Raises:
        ValueError: 当主配置或自定义配置为空时抛出错误。
    """

    if not main_conf:
        raise ValueError("主配置参数不能为空，请检查配置文件是否正确加载")

    if not custom_conf:
        raise ValueError("自定义配置参数不能为空或空字典，请提供有效的自定义配置")

    # 合并主配置和自定义配置
    merged_conf = {}
    for key, value in main_conf.items():
        merged_conf[key] = value  # 将主配置复制到合并后的配置中

    for key, value in custom_conf.items():
        if value not in [None, ""]:  # 只有值不为 None 和 空字符串，才进行合并
            merged_conf[key] = value  # 自定义配置参数会覆盖主配置中的同名参数

    # 合并 CLI 参数与合并后的配置，确保 CLI 参数的优先级最高
    for key, value in kwargs.items():
        if value not in [None, ""]:  # 如果值不为 None 和 空字符串，则进行合并
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


def check_python_version(min_version: tuple = (3, 10)) -> None:
    """
    检查当前 Python 版本是否满足最低要求

    Args:
        min_version (tuple, optional): 最低 Python 版本要求，默认为 (3, 10)

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


class BaseEndpointManager:
    @classmethod
    def model_2_endpoint(cls, base_endpoint: str, params: dict) -> str:
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        separator = "&" if "?" in base_endpoint else "?"
        return f"{base_endpoint}{separator}{param_str}"


async def filter_by_date_interval(
    data: Union[List[Dict], Dict],
    interval: str,
    fied_name: str = "create_time",
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
        date_str = item.get(fied_name)
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


def filter_to_list(
    filter_instance: Any,
    entries_path: str,
    exclude_fields: List[str],
    extra_fields: Optional[List[str]] = None,
) -> list:
    """
    通用的 `_to_list` 方法实现。

    Args:
        filter_instance (Any): Filter 实例
        entries_path (str): entries 的路径
        exclude_fields (List[str]): 排除的字段列表
        extra_fields (Optional[List[str]]): 额外的字段列表

    Returns:
        list: entries 列表
    """

    # 生成属性名称列表，然后过滤掉排除的属性
    keys = [
        prop_name
        for prop_name in dir(filter_instance)
        if not prop_name.startswith("__")
        and not prop_name.startswith("_")
        and prop_name not in exclude_fields
    ]

    entries = filter_instance._get_attr_value(entries_path) or []
    list_dicts = []
    # 使用集合避免重复记录相同的错误
    errors = set()
    extra_fields = extra_fields or []  # 使用空列表而不是空字典作为默认值

    # 遍历每个条目并创建一个字典
    for entry in entries:
        d = {key: getattr(filter_instance, key, None) for key in extra_fields}
        for key in keys:
            try:
                attr_values = getattr(filter_instance, key)
                # 当前entry在属性列表中的索引
                index = entries.index(entry)
                # 如果属性值的长度足够则赋值，否则赋None
                d[key] = attr_values[index] if index < len(attr_values) else None
            except TypeError as e:
                # 如果字段已出错，跳过重复记录
                error_message = _("字段 {0} 出错: {1}").format(key, str(e))
                if error_message not in errors:
                    errors.add(error_message)
                d[key] = None
            except Exception as e:
                # 捕获其他未预料的异常
                error_message = _("字段 {0} 出现未预料的错误: {1}").format(key, str(e))
                if error_message not in errors:
                    errors.add(error_message)
                d[key] = None

        list_dicts.append(d)

    # 如果有错误，统一抛出异常
    if errors:
        raise APIFilterError(_("由于接口更新，部分字段处理失败:\n") + "\n".join(errors))

    return list_dicts

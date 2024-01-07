# path: f2/utils/algorithm.py

import re
import random
import secrets
import datetime
import importlib_resources

from typing import Union, Any
from pathlib import Path

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


def get_timestamp(unit: str = "milli"):
    """
    根据给定的单位获取当前时间 (Get the current time based on the given unit)

    Args:
        unit (str): 时间单位，可以是 "milli"、"sec"、"min" 等
            (The time unit, which can be "milli", "sec", "min", etc.)

    Returns:
        int: 根据给定单位的当前时间 (The current time based on the given unit)
    """

    now = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
    if unit == "milli":
        return int(now.total_seconds() * 1000)
    elif unit == "sec":
        return int(now.total_seconds())
    elif unit == "min":
        return int(now.total_seconds() / 60)
    else:
        raise ValueError("Unsupported time unit")


def timestamp_2_str(
    timestamp: Union[str, int, float], format: str = "%Y-%m-%d %H-%M-%S"
) -> str:
    """
    将 UNIX 时间戳转换为格式化字符串 (Convert a UNIX timestamp to a formatted string)

    Args:
        timestamp (int): 要转换的 UNIX 时间戳 (The UNIX timestamp to be converted)
        format (str, optional): 返回的日期时间字符串的格式。
                                默认为 '%Y-%m-%d %H-%M-%S'。
                                (The format for the returned date-time string
                                Defaults to '%Y-%m-%d %H-%M-%S')

    Returns:
        str: 格式化的日期时间字符串 (The formatted date-time string)
    """
    if timestamp is None or timestamp == "None":
        return ""

    return datetime.datetime.fromtimestamp(float(timestamp)).strftime(format)


def num_to_base36(num: int) -> str:
    """数字转换成base32 (Convert number to base 36)"""

    base_str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    if num == 0:
        return "0"

    base36 = []
    while num:
        num, i = divmod(num, 36)
        base36.append(base_str[i])

    return "".join(reversed(base36))


def split_set_cookie(cookie_str: str) -> str:
    """
    拆分Set-Cookie字符串并拼接 (Split the Set-Cookie string and concatenate)

    Args:
        cookie_str (str): 待拆分的Set-Cookie字符串 (The Set-Cookie string to be split)

    Returns:
        str: 拼接后的Cookie字符串 (Concatenated cookie string)
    """

    # 判断是否为字符串 / Check if it's a string
    if not isinstance(cookie_str, str):
        raise TypeError("`set-cookie` must be str")

    # 拆分Set-Cookie字符串,避免错误地在expires字段的值中分割字符串 (Split the Set-Cookie string, avoiding incorrect splitting on the value of the 'expires' field)
    # 拆分每个Cookie字符串，只获取第一个分段（即key=value部分） / Split each Cookie string, only getting the first segment (i.e., key=value part)
    # 拼接所有的Cookie (Concatenate all cookies)
    return ";".join(
        cookie.split(";")[0] for cookie in re.split(", (?=[a-zA-Z])", cookie_str)
    )


def split_dict_cookie(cookie_dict: dict) -> str:
    return "; ".join(f"{key}={value}" for key, value in cookie_dict.items())


def extract_valid_urls(inputs: Union[str, list[str]]) -> Union[str, list[str], None]:
    from f2.i18n.translator import _

    """从输入中提取有效的URL (Extract valid URLs from input)

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


def _get_first_item_from_list(_list) -> list:
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


def get_resource_path(filepath: str):
    """获取资源文件的路径 (Get the path of the resource file)

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
        return [re.sub(reSub, "_", i) for i in obj]

    if isinstance(obj, str):
        return re.sub(reSub, "_", obj)

    # raise TypeError("输入应为字符串或字符串列表")


def ensure_path(path: Union[str, Path]) -> Path:
    """确保路径是一个Path对象 (Ensure the path is a Path object)"""
    return Path(path) if isinstance(path, str) else path

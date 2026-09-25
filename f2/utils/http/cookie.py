# path: f2/utils/http/cookie.py

import re
from typing import Dict

from f2.i18n.translator import _


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


def parse_cookie_str(cookie_str: str) -> Dict[str, str]:
    """
    把 Cookie 字符串解析为字典 (Parse a Cookie string into a dict)

    按 `;` 分段，每段只在第一个 `=` 处切分，值里的 `=` 会被保留；
    没有 `=` 或名称为空的片段会被忽略，同名 Cookie 以最后一次出现的值为准。

    Args:
        cookie_str (str): 形如 "a=1; b=2" 的 Cookie 字符串 (Cookie string such as "a=1; b=2")

    Returns:
        Dict[str, str]: Cookie 名称到值的映射 (Mapping from cookie name to value)
    """

    if not isinstance(cookie_str, str):
        raise TypeError(_("cookie_str 参数应为字符串"))

    cookies: Dict[str, str] = {}
    for part in cookie_str.split(";"):
        name, sep, value = part.strip().partition("=")
        if sep and name.strip():
            cookies[name.strip()] = value.strip()
    return cookies


def split_dict_cookie(cookie_dict: Dict) -> str:
    """
    拆分Cookie字典并拼接 (Split the Cookie dictionary and concatenate)

    Args:
        cookie_dict (dict): 待拆分的Cookie字典 (The Cookie dictionary to be split)

    Returns:
        str: 拼接后的Cookie字符串 (Concatenated cookie string)
    """
    return "; ".join(f"{key}={value}" for key, value in cookie_dict.items())

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


def split_dict_cookie(cookie_dict: Dict) -> str:
    """
    拆分Cookie字典并拼接 (Split the Cookie dictionary and concatenate)

    Args:
        cookie_dict (dict): 待拆分的Cookie字典 (The Cookie dictionary to be split)

    Returns:
        str: 拼接后的Cookie字符串 (Concatenated cookie string)
    """
    return "; ".join(f"{key}={value}" for key, value in cookie_dict.items())

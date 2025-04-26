# path: f2/utils/string/formatter.py


import re
from typing import Any, List, Optional, Union, overload


@overload
def extract_valid_urls(inputs: str) -> Optional[str]: ...


@overload
def extract_valid_urls(inputs: List[str]) -> List[str]: ...


def extract_valid_urls(inputs: Union[str, List[str]]) -> Union[str, List[str], None]:
    """
    从输入中提取有效的URL (Extract valid URLs from input)

    Args:
        inputs (Union[str, list[str]]): 输入的字符串或字符串列表 (Input string or list of strings)

    Returns:
        - str 或 None: 当输入为单个字符串时，返回找到的第一个URL或None
        - List[str]: 当输入为字符串列表时，返回找到的所有URL的列表（可能为空）
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
            if isinstance(input_str, str):  # 确保列表元素是字符串
                matches = url_pattern.findall(input_str)
                if matches:
                    valid_urls.extend(matches)

        # 返回有效URL列表（可能为空）
        return valid_urls

    # 如果输入既不是字符串也不是列表，返回空列表（处理输入类型错误的情况）
    return [] if isinstance(inputs, list) else None


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

# path: f2/utils/string/formatter.py


import re
import sys
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


# 文件名中不允许出现的字符（以 Windows 为准，同时覆盖 macOS 与 Linux）换成外观相近的
# 全角字符，换行与制表符换成空格；其余字符（包括标点、空格、各国文字与 emoji）原样保留（#248）
_FILENAME_CHAR_MAP = str.maketrans(
    {
        "/": "／",
        "\\": "＼",
        ":": "：",
        "*": "＊",
        "?": "？",
        '"': "＂",
        "<": "＜",
        ">": "＞",
        "|": "｜",
        "\t": " ",
        "\n": " ",
        "\r": " ",
    }
)
# 其余控制字符在文件名中不可见，Windows 也不允许，直接去掉
_CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x1f\x7f]")
# Windows 的保留设备名，带扩展名同样不能作为文件名或目录名（如作者昵称为 con 时无法建立用户目录）
_WINDOWS_RESERVED_NAMES = re.compile(
    r"(?i)(con|prn|aux|nul|com[0-9¹²³]|lpt[0-9¹²³])(\..*)?"
)
_IS_WINDOWS = sys.platform == "win32"


def _replace_filename_chars(text: str) -> str:
    result = _CONTROL_CHARS_PATTERN.sub("", text.translate(_FILENAME_CHAR_MAP))
    # Windows 不允许文件名以空格或点结尾，开头的空格也容易被忽略
    result = result.strip().rstrip(". ")
    # 非空内容被清空时（例如昵称全是点）用下划线兜底，避免目录名为空
    if not result:
        return "_" if text else ""
    # 只在 Windows 上处理：其他系统可以使用这些名称，已下载的文件名保持不变
    reserved = _WINDOWS_RESERVED_NAMES.fullmatch(result) if _IS_WINDOWS else None
    if reserved:
        # Windows 只看第一个点之前的部分（NUL.txt 等同于 NUL），下划线要加在设备名后面
        result = f"{reserved.group(1)}_{reserved.group(2) or ''}"
    return result


def replaceT(obj: Union[str, Any]) -> Union[str, Any]:
    """
    替换文案中文件名不允许的字符 (Replace characters that are not allowed in file names)

    \\ / : * ? " < > | 换成外观相近的全角字符，换行与制表符换成空格，其余控制字符去掉，
    去掉首尾空格与结尾的点；标点、空格、各国文字与 emoji 原样保留。

    Args:
        obj (str): 传入对象 (Input object)

    Returns:
        new: 处理后的内容 (Processed content)
    """

    if isinstance(obj, list):
        return [
            _replace_filename_chars(i) if isinstance(i, str) else i or "" for i in obj
        ]

    if isinstance(obj, str):
        return _replace_filename_chars(obj)

    return obj

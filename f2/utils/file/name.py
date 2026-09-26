# path: f2/utils/file/name.py

import re
import sys
from typing import Dict

# ext4、btrfs 等文件系统（包括多数 NAS）限制单个文件名最多 255 字节；
# NTFS、APFS 按字符计算，不超过 255 字节的文件名同样不会超出
FILENAME_BYTE_LIMIT = 255
FILENAME_ELLIPSIS = "......"


def fit_filename(name: str, suffix: str = "", limit: int = FILENAME_BYTE_LIMIT) -> str:
    """
    截断文件名，使其连同后缀的 UTF-8 编码不超过 limit 字节，后缀保持完整
    (Truncate a file name so that, with its suffix, it fits in limit UTF-8 bytes)

    超出时保留开头约 2/3 与结尾约 1/3，中间用 '......' 连接，与 split_filename 的写法一致。

    Args:
        name (str): 不含后缀的文件名
        suffix (str): 后缀，如 ".mp4"
        limit (int): 字节上限，默认为 255

    Returns:
        str: 不超过字节上限的完整文件名
    """

    budget = limit - len(suffix.encode("utf-8"))
    raw = name.encode("utf-8")
    if len(raw) <= budget:
        return name + suffix

    ellipsis_size = len(FILENAME_ELLIPSIS.encode("utf-8"))
    if budget <= ellipsis_size:
        return raw[: max(budget, 0)].decode("utf-8", errors="ignore") + suffix

    keep = budget - ellipsis_size
    head_size = keep * 2 // 3
    tail_size = keep - head_size
    # 在多字节字符中间截断时丢弃不完整的字节
    head = raw[:head_size].decode("utf-8", errors="ignore")
    tail = raw[len(raw) - tail_size :].decode("utf-8", errors="ignore")
    return f"{head}{FILENAME_ELLIPSIS}{tail}{suffix}"


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

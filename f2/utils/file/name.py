# path: f2/utils/file/name.py

import re
import sys
from typing import Dict


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

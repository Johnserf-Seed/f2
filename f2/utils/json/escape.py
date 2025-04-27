# path: f2/utils/json/escape.py

import json
import re


def unescape_json(json_text: str) -> dict:
    """
    反转义 JSON 文本

    Args:
        json_text (str): 带有转义字符的 JSON 文本

    Returns:
        json_obj (dict): 反转义后的 JSON 对象
    """
    try:
        # 如果是双重编码的 JSON，先解码一次得到 JSON 字符串
        json_str = (
            json.loads(f'"{json_text}"') if not json_text.startswith("{") else json_text
        )
        # 再解析成 JSON 对象
        return json.loads(json_str)
    except Exception as e:
        print(f"unescape_json error: {e}, raw_json: {json_text}")
        return {}

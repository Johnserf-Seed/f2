# f2/utils/json_filter.py

from typing import Any, List, Union
from jsonpath_ng.ext import parse
from jsonpath_ng.exceptions import JsonPathParserError, JsonPathLexerError
import json


class JSONModel:
    def __init__(self, data: Any):
        """
        初始化 JSONModel 对象。

        Args:
            data: JSON 数据。
        """
        self._data = data

    def _parse_expression(self, jsonpath_expr: str):
        """
        解析 JSONPath 表达式，并处理解析错误。

        Args:
            jsonpath_expr: JSONPath 表达式字符串。

        Returns:
            JSONPath 表达式对象。
        """
        try:
            return parse(jsonpath_expr)
        except (JsonPathParserError, JsonPathLexerError):
            raise ValueError(
                f"这是一个无效的 JSONPath 表达式: {jsonpath_expr}，请检查表达式是否正确。"
            )

    def _get_attr_value(self, jsonpath_expr: str) -> Union[Any, List[Any], None]:
        """
        根据 JSONPath 表达式获取属性值。

        Args:
            jsonpath_expr: JSONPath 表达式字符串。

        Returns:
            属性值或属性值列表。
        """
        expr = self._parse_expression(jsonpath_expr)
        matches = expr.find(self._data)
        if not matches:
            return None
        values = [match.value for match in matches]
        return values[0] if len(values) == 1 else values

    def _extract_values(self, matches: List[Any], field_part: str) -> List[Any]:
        """
        从匹配的项中提取字段值，处理缺失的字段。

        Args:
            matches: 匹配的项列表。
            field_part: 字段部分。

        Returns:
            字段值列表。
        """
        values = []
        for match in matches:
            item = match.value
            if field_part.startswith("."):
                field_expr = parse("$" + field_part)
                field_result = field_expr.find(item)
                values.append(field_result[0].value if field_result else None)
            else:
                values.append(item)
        return values

    def _get_list_attr_value(
        self, jsonpath_expr: str, as_json: bool = False
    ) -> Union[List[Any], str]:
        """
        获取列表属性值，处理缺失的字段。

        Args:
            jsonpath_expr: JSONPath 表达式字符串。
            as_json: 是否返回 JSON 字符串。

        Returns:
            属性值列表或 JSON 字符串。
        """
        expr = self._parse_expression(jsonpath_expr)

        if "[*]" in jsonpath_expr:
            parent_expr_str, field_part = jsonpath_expr.split("[*]", 1)
            parent_expr = parse(parent_expr_str + "[*]")
            matches = parent_expr.find(self._data)
            values = self._extract_values(matches, field_part)
        else:
            value = self._get_attr_value(jsonpath_expr)
            values = value if isinstance(value, list) else [value]

        return json.dumps(values, ensure_ascii=False) if as_json else values

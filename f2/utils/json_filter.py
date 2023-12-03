# f2/utils/json_filter.py

from jsonpath_ng import parse

# from jsonpath_ng.ext import parser
# from jsonpath_ng.ext.filter import Filter
import json

# 需要重写find_or_create用于[*]匹配不到键值时的返回
# https://github.com/h2non/jsonpath-ng/issues/82


class JSONModel:
    def __init__(self, data):
        self._data = data

    def _get_attr_value(self, jsonpath_expr):
        expr = parse(jsonpath_expr)
        # expr = parser.parse(jsonpath_expr)
        result = expr.find(self._data)
        if result:
            return (
                [match.value for match in result]
                if len(result) > 1
                else result[0].value
            )
        return None

    def _get_list_attr_value(self, jsonpath_expr, as_json=False):
        values = self._get_attr_value(jsonpath_expr)

        if isinstance(values, (list, tuple)):
            if as_json:
                return json.dumps(values, ensure_ascii=False)
            return values
        if as_json:
            return (
                json.dumps([values], ensure_ascii=False) if values is not None else "[]"
            )

        return [values] if values is not None else []

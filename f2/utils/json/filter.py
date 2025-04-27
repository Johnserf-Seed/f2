# path: f2/utils/json/filter.py

import json
from typing import Any, Dict, List, Optional, Union

from jsonpath_ng import parse  # type: ignore[import-untyped]

from f2.exceptions.api_exceptions import APIFilterError
from f2.i18n.translator import _


class JSONModel:
    """
    JSON 数据模型 (JSON Data Model)

    该类用于处理和解析 JSON 数据。通过提供 JSONPath 表达式。

    支持从 JSON 数据中提取单一属性值或列表属性值，并支持缓存 JSONPath 表达式的解析器以提高性能。

    类属性:
    - _data (Any): 存储的 JSON 数据，可以是字典、列表或其他类型。
    - _cache (dict): 存储已解析的 JSONPath 表达式解析器，用于避免重复解析。

    类方法:
    - __init__: 初始化 JSONModel 实例并加载数据。
    - _parse_expression: 缓存并返回 JSONPath 表达式解析器。
    - _get_attr_value: 根据 JSONPath 表达式获取单一属性值。
    - _get_list_attr_value: 获取列表属性值，支持字段缺失时补全 None。

    异常处理:
    - 该类会在没有匹配到值时返回 `None` 或空列表。

    使用示例:
    ```python
        # 创建 JSONModel 实例并加载 JSON 数据
        json_data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        model = JSONModel(json_data)

        # 获取单一属性值
        name = model._get_attr_value('$.users[0].name')
        print(name)  # 输出: Alice

        # 获取列表属性值
        names = model._get_list_attr_value('$.users[*].name')
        print(names)  # 输出: ['Alice', 'Bob']
    ```
    """

    def __init__(self, data: Any):
        self._data = data
        self._cache: Dict[str, Any] = {}  # 缓存解析后的 JSONPath 表达式

    def _parse_expression(self, jsonpath_expr: str):
        """
        缓存 JSONPath 表达式解析器，避免重复解析。

        Args:
            jsonpath_expr: str: JSONPath 表达式

        Returns:
            jsonpath_ng.jsonpath.JsonPath: JSONPath 表达式解析器
        """
        if jsonpath_expr not in self._cache:
            self._cache[jsonpath_expr] = parse(jsonpath_expr)
        return self._cache[jsonpath_expr]

    def _get_attr_value(self, jsonpath_expr: str) -> Optional[Any]:
        """
        根据 JSONPath 表达式获取单一属性值。

        Args:
            jsonpath_expr: str: JSONPath 表达式

        Returns:
            Union[str, int, float, bool]: 属性值
        """
        expr = self._parse_expression(jsonpath_expr)
        matches = expr.find(self._data)
        if not matches:
            return None
        # 如果只有一个结果，直接返回值；多个结果返回列表
        return (
            matches[0].value
            if len(matches) == 1
            else [match.value for match in matches]
        )

    def _get_list_attr_value(
        self, jsonpath_expr: str, as_json: bool = False
    ) -> Union[List[Any], str, None]:
        """
        获取列表属性值，支持字段缺失时补全 None。

        Args:
            jsonpath_expr: str: JSONPath 表达式
            as_json: bool: 是否返回 JSON 字符串

        Returns:
            List[Union[str, int, float, bool]]: 属性值列表
        """
        # 提取父级路径和子级路径
        if "[*]" in jsonpath_expr:
            idx = jsonpath_expr.find("[*]")
            parent_expr_str = jsonpath_expr[: idx + 3]  # 包含 [*]
            child_expr_str = jsonpath_expr[idx + 3 :]  # [*] 之后的部分
        else:
            # 如果没有 [*]，则整个路径作为父级路径
            parent_expr_str = jsonpath_expr
            child_expr_str = ""

        parent_expr = self._parse_expression(parent_expr_str)
        parent_matches = parent_expr.find(self._data)

        values = []
        if child_expr_str:
            # 存在子级路径，需要在每个父级元素中查找子属性
            child_expr = self._parse_expression(f'$.{child_expr_str.lstrip(".")}')
            for match in parent_matches:
                parent_value = match.value
                # 在当前父级元素中查找子属性
                child_matches = child_expr.find(parent_value)
                if child_matches:
                    # 假设每个父级元素中子属性只匹配一个值
                    values.append(child_matches[0].value)
                else:
                    values.append(None)  # 子级路径缺失时补全 None
        else:
            # 没有子级路径，父级匹配结果即为值
            values = [match.value for match in parent_matches]

        # 返回 JSON 字符串或列表
        return json.dumps(values, ensure_ascii=False) if as_json else values


def filter_to_list(
    filter_instance: Any,
    entries_path: str,
    exclude_fields: List[str],
    extra_fields: Optional[List[str]] = None,
) -> list:
    """
    通用的 `_to_list` 方法实现。

    Args:
        filter_instance (Any): Filter 实例
        entries_path (str): entries 的路径
        exclude_fields (List[str]): 排除的字段列表
        extra_fields (Optional[List[str]]): 额外的字段列表

    Returns:
        list: entries 列表
    """
    # 生成属性名称列表，然后过滤掉排除的属性
    keys = [
        prop_name
        for prop_name in dir(filter_instance)
        if not prop_name.startswith("__")
        and not prop_name.startswith("_")
        and prop_name not in exclude_fields
    ]

    entries = filter_instance._get_attr_value(entries_path) or []
    list_dicts = []
    # 使用集合避免重复记录相同的错误
    errors = set()
    extra_fields = extra_fields or []  # 使用空列表而不是空字典作为默认值

    # 遍历每个条目并创建一个字典
    for entry in entries:
        d = {key: getattr(filter_instance, key, None) for key in extra_fields}
        for key in keys:
            try:
                attr_values = getattr(filter_instance, key)
                # 当前entry在属性列表中的索引
                index = entries.index(entry)
                # 如果属性值的长度足够则赋值，否则赋None
                d[key] = attr_values[index] if index < len(attr_values) else None
            except TypeError as e:
                # 如果字段已出错，跳过重复记录
                error_message = _("字段 {0} 出错: {1}").format(key, str(e))
                if error_message not in errors:
                    errors.add(error_message)
                d[key] = None
            except Exception as e:
                # 捕获其他未预料的异常
                error_message = _("字段 {0} 出现未预料的错误: {1}").format(key, str(e))
                if error_message not in errors:
                    errors.add(error_message)
                d[key] = None

        list_dicts.append(d)

    # 如果有错误，统一抛出异常
    if errors:
        raise APIFilterError(_("由于接口更新，部分字段处理失败:\n") + "\n".join(errors))

    return list_dicts

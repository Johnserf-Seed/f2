# path: tests/test_json_filter.py

from f2.utils.json_filter import JSONModel

# 测试数据
data = {
    "example": [
        {"a": 1, "b": 2},
        {"b": 2, "c": 3},
        {"a": 1, "c": 3},
        {"a": 1, "b": 2, "c": 3},
    ]
}


class TestJSONModel:

    def setup_method(self):
        # 每个测试方法前执行，初始化 JSONModel 实例
        self.model = JSONModel(data)

    def test_get_existing_attribute(self):
        # 测试获取存在的属性
        result = self.model._get_list_attr_value("$.example[*].a")
        assert result == [1, None, 1, 1], "应当正确处理缺失的 'a' 字段"

    def test_get_nonexistent_attribute(self):
        # 测试获取不存在的属性
        result = self.model._get_list_attr_value("$.example[*].d")
        assert result == [None, None, None, None], "应当在字段缺失时返回 None"

    def test_get_nested_attribute(self):
        # 测试获取嵌套属性
        nested_data = {
            "example": [
                {"a": {"x": 10}, "b": 2},
                {"b": 2, "c": 3},
                {"a": {"x": 20}, "c": 3},
                {"a": {"x": 30}, "b": 2, "c": 3},
            ]
        }
        model = JSONModel(nested_data)
        result = model._get_list_attr_value("$.example[*].a.x")
        assert result == [10, None, 20, 30], "应当正确处理嵌套的 'a.x' 字段"

    def test_get_attribute_with_different_types(self):
        # 测试处理不同类型的数据
        mixed_data = {
            "example": [
                {"a": 1},
                {"a": "string"},
                {"a": [1, 2, 3]},
                {"a": {"key": "value"}},
                {},
            ]
        }
        model = JSONModel(mixed_data)
        result = model._get_list_attr_value("$.example[*].a")
        assert result == [
            1,
            "string",
            [1, 2, 3],
            {"key": "value"},
            None,
        ], "应当正确处理不同类型的 'a' 字段"

    def test_get_attribute_with_missing_list(self):
        # 测试当列表字段缺失时的情况
        data_without_list = {
            "not_example": [
                {"a": 1},
                {"a": 2},
            ]
        }
        model = JSONModel(data_without_list)
        result = model._get_list_attr_value("$.example[*].a")
        assert result == [], "当列表字段缺失时，应返回空列表"

    def test_get_single_value(self):
        # 测试获取单个值
        result = self.model._get_attr_value("$.example[0].a")
        assert result == 1, "应当正确返回单个值"

    def test_get_single_value_missing(self):
        # 测试获取缺失的单个值
        result = self.model._get_attr_value("$.example[1].a")
        assert result is None, "当单个值缺失时，应返回 None"

    def test_get_list_attr_value_as_json(self):
        # 测试 as_json 参数
        result = self.model._get_list_attr_value("$.example[*].a", as_json=True)
        assert result == "[1, null, 1, 1]", "应当正确返回 JSON 字符串"

    def test_get_attribute_with_special_characters(self):
        # 测试包含特殊字符的字段名
        special_data = {
            "example": [
                {"a-b": 1},
                {"a-b": 2},
            ]
        }
        model = JSONModel(special_data)
        result = model._get_list_attr_value("$.example[*].a-b")
        assert result == [1, 2], "应当正确处理包含特殊字符的字段名"

    def test_empty_data(self):
        # 测试空数据
        empty_model = JSONModel({})
        result = empty_model._get_list_attr_value("$.example[*].a")
        assert result == [], "在空数据时，应返回空列表"

    def test_none_data(self):
        # 测试数据为 None
        none_model = JSONModel(None)
        result = none_model._get_list_attr_value("$.example[*].a")
        assert result == [], "在数据为 None 时，应返回空列表"

    def test_get_attribute_with_index_out_of_range(self):
        # 测试索引超出范围
        result = self.model._get_attr_value("$.example[10].a")
        assert result is None, "当索引超出范围时，应返回 None"

    def test_get_list_attr_value_with_complex_expression(self):
        # 测试复杂的 JSONPath 表达式
        complex_data = {
            "data": {
                "items": [
                    {"id": 1, "value": {"a": 10}},
                    {"id": 2, "value": {"a": 20}},
                    {"id": 3, "value": {"b": 30}},
                ]
            }
        }
        model = JSONModel(complex_data)
        result = model._get_list_attr_value("$.data.items[*].value.a")
        assert result == [10, 20, None], "应当正确处理复杂的 JSONPath 表达式"

    def test_get_attribute_with_filter_expression(self):
        # 测试包含过滤器的 JSONPath 表达式
        # 需要使用 jsonpath_ng.ext
        from jsonpath_ng.ext import parse

        model = JSONModel(data)
        expr = parse("$.example[?(@.b==2)].a")
        results = expr.find(model._data)
        values = [match.value for match in results]
        assert values == [1, 1], "应当正确处理带过滤器的表达式"

    def test_get_attribute_with_recursive_descent(self):
        # 测试递归下降
        recursive_data = {
            "root": {
                "child": {
                    "name": "child1",
                    "child": {"name": "child2", "child": {"name": "child3"}},
                }
            }
        }
        model = JSONModel(recursive_data)
        result = model._get_attr_value("$..name")
        assert result == ["child1", "child2", "child3"], "应当正确处理递归下降表达式"

    def test_get_attribute_with_wildcard(self):
        # 测试通配符
        wildcard_data = {
            "items": {
                "item1": {"value": 1},
                "item2": {"value": 2},
                "item3": {"value": 3},
            }
        }
        model = JSONModel(wildcard_data)
        result = model._get_list_attr_value("$.items.*.value")
        assert result == [1, 2, 3], "应当正确处理通配符表达式"

    def test_get_attribute_with_mixed_types_in_list(self):
        # 测试列表中包含不同类型的元素
        mixed_list_data = {
            "example": [
                {"a": 1},
                ["b", 2],
                "string",
                123,
                None,
                {"a": 3},
            ]
        }
        model = JSONModel(mixed_list_data)
        result = model._get_list_attr_value("$.example[*].a")
        assert result == [
            1,
            None,
            None,
            None,
            None,
            3,
        ], "应当正确处理列表中不同类型的元素"

    def test_get_attribute_with_multiple_matches(self):
        multi_match_data = {
            "data": {
                "items": [
                    {"id": 1, "values": [{"a": 10}, {"a": 20}]},
                    {"id": 2, "values": [{"a": 30}, {"b": 40}]},
                ]
            }
        }
        model = JSONModel(multi_match_data)
        result = model._get_attr_value("$.data.items[*].values[*].a")
        assert result == [10, 20, 30], "应当正确处理多层次的列表"

    def test_get_attribute_with_special_jsonpath_syntax(self):
        # 测试特殊的 JSONPath 语法，如数组切片
        slice_data = {
            "example": [
                {"a": 1},
                {"a": 2},
                {"a": 3},
                {"a": 4},
                {"a": 5},
            ]
        }
        model = JSONModel(slice_data)
        result = model._get_list_attr_value("$.example[1:4].a")
        assert result == [2, 3, 4], "应当正确处理数组切片"

    def test_get_attribute_with_union(self):
        # 测试联合索引
        union_data = {
            "example": [
                {"a": 1},
                {"a": 2},
                {"a": 3},
                {"a": 4},
                {"a": 5},
            ]
        }
        model = JSONModel(union_data)
        result = model._get_attr_value("$.example[0:5:2].a")
        assert result == [1, 3, 5], "应当正确处理联合索引"

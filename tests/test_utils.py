# path: tests/test_utils.py

import datetime

import pytest

from f2.utils.utils import gen_random_str, get_timestamp, merge_config


def test_gen_random_str():
    # Test lengths
    assert len(gen_random_str(5)) == 5
    assert len(gen_random_str(10)) == 10
    assert len(gen_random_str(0)) == 0

    # Test characters are from the expected set
    sample_str = gen_random_str(100)
    for char in sample_str:
        assert (
            char in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
        )


def test_get_timestamp():
    # Assuming your system's clock is accurate, this is a simple way to verify
    # the value is close to expected since it could vary slightly between function
    # call and the actual assert statement.

    # Test milliseconds
    assert (
        abs(
            get_timestamp("milli")
            - int(
                (
                    datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
                ).total_seconds()
                * 1000
            )
        )
        <= 10
    )

    # Test seconds
    assert (
        abs(
            get_timestamp("sec")
            - int(
                (
                    datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
                ).total_seconds()
            )
        )
        <= 1
    )

    # Test minutes
    assert (
        abs(
            get_timestamp("min")
            - int(
                (
                    datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
                ).total_seconds()
                / 60
            )
        )
        <= 1
    )

    # Test invalid unit
    with pytest.raises(ValueError, match="不支持的时间单位"):
        get_timestamp("invalid_unit")


def test_merge_config():
    # 测试主配置为空
    with pytest.raises(ValueError, match="主配置参数不能为空"):
        merge_config({}, {"key": "value"})

    # 测试自定义配置为空
    with pytest.raises(ValueError, match="自定义配置参数不能为空或空字典"):
        merge_config({"key": "value"}, {})

    # 测试主配置和自定义配置合并
    main_conf = {"key1": "value1", "key2": "value2"}
    custom_conf = {"key2": None, "key3": ""}
    result = merge_config(main_conf, custom_conf)
    expected = {
        "key1": "value1",  # 主配置保留
        "key2": "value2",  # 自定义配置的 None 不覆盖主配置
    }
    assert result == expected

    # 测试 CLI 参数覆盖自定义配置和主配置
    cli_args = {"key2": "cli_value2", "key4": "cli_value4"}
    result = merge_config(main_conf, custom_conf, **cli_args)
    expected = {
        "key1": "value1",  # 主配置保留
        "key2": "cli_value2",  # CLI 参数覆盖
        "key4": "cli_value4",  # CLI 参数新增
    }
    assert result == expected

    # 测试空值和 None 不会覆盖已有值
    custom_conf = {"key2": None, "key3": ""}
    cli_args = {"key3": None, "key4": ""}
    result = merge_config(main_conf, custom_conf, **cli_args)
    expected = {
        "key1": "value1",  # 主配置保留
        "key2": "value2",  # 自定义配置的 None 不覆盖主配置
    }
    assert result["key1"] == "value1"
    assert result["key2"] == "value2"
    assert "key3" not in result  # 空值不应新增键
    assert "key4" not in result  # 空值不应新增键

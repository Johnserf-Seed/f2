# path: tests/test_parse_interval.py

import datetime

import pytest

from f2.exceptions import ConfError
from f2.utils.time.timestamp import parse_interval

# 2024-01-01 00:00:00 与 2024-12-31 23:59:59（北京时间）
START_2024 = 1704038400
END_2024 = 1735660799


@pytest.mark.parametrize("interval", [None, "", "  ", "all", "ALL", " all "])
def test_parse_interval_without_limit(interval):
    assert parse_interval(interval) is None


@pytest.mark.parametrize(
    "interval", ["2024-01-01|2024-12-31", " 2024-01-01 | 2024-12-31 "]
)
def test_parse_interval_includes_both_days(interval):
    assert parse_interval(interval) == (START_2024, END_2024)


def test_parse_interval_single_day():
    start, end = parse_interval("2024-05-01|2024-05-01")
    assert end - start == 24 * 3600 - 1


def test_parse_interval_milliseconds():
    assert parse_interval("2024-01-01|2024-12-31", unit="milli") == (
        START_2024 * 1000,
        END_2024 * 1000,
    )


@pytest.mark.parametrize(
    "interval",
    [
        "2024-01-01",
        "2024/01/01|2024/12/31",
        "2024-13-01|2024-12-31",
        "2024-02-30|2024-03-01",
        "2024-01-01|2024-12-31|2025-01-01",
        "a|b",
        # YAML 会把单独的日期解析成 date 对象
        datetime.date(2024, 1, 1),
    ],
)
def test_parse_interval_rejects_invalid_format(interval):
    with pytest.raises(ConfError) as exc_info:
        parse_interval(interval)
    assert exc_info.value.key == "interval"
    assert exc_info.value.value == interval


def test_parse_interval_rejects_reversed_range():
    with pytest.raises(ConfError) as exc_info:
        parse_interval("2024-12-31|2024-01-01")
    assert exc_info.value.key == "interval"

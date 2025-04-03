# path: f2/utils/time/timestamp.py

import datetime
import traceback
from typing import List, Union

from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger


def get_timestamp(unit: str = "milli") -> int:
    """
    根据给定的单位获取当前时区的时间戳 (Get the current time based on the given unit)

    Args:
        unit (str): 时间单位，可以是 "milli"、"sec"、"min" 等
            (The time unit, which can be "milli", "sec", "min", etc.)

    Returns:
        int: 根据给定单位的当前时间 (The current time based on the given unit)
    """

    now = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime(
        1970, 1, 1, tzinfo=datetime.timezone.utc
    )
    if unit == "milli":
        return int(now.total_seconds() * 1000)
    elif unit == "sec":
        return int(now.total_seconds())
    elif unit == "min":
        return int(now.total_seconds() / 60)
    else:
        raise ValueError(_("不支持的时间单位：{0}").format(unit))


def timestamp_2_str(
    timestamp: Union[str, int, float, List],
    format: str = "%Y-%m-%d %H-%M-%S",
    tz: datetime.timezone = datetime.timezone(datetime.timedelta(hours=8)),
) -> Union[str, int, float, List]:
    """
    将 UNIX 时间戳转换为东八区北京时间格式化字符串使用

    Args:
        timestamp (Union[str, int, float, list]): 要转换的 UNIX 时间戳
        format (str, optional): 返回的日期时间字符串的格式，默认为 '%Y-%m-%d %H-%M-%S'。
        tz (datetime.timezone, optional): 时区，默认为东八区北京时间

    Returns:
        Union[str, int, float, list]: 格式化的日期时间字符串
    """

    # 处理空或无效时间戳
    if timestamp in [None, "None"]:
        return _("Invalid timestamp")

    if timestamp in [0, "0"]:
        return datetime.datetime.now(tz=tz).strftime(format)

    # 递归处理列表中的时间戳
    def convert(ts):
        if isinstance(ts, str):
            # 处理类似 "Wed Jun 01 10:23:01 +0800 2022" 的格式
            if len(ts) == 30:
                return datetime.datetime.strptime(ts, "%a %b %d %H:%M:%S %z %Y")
            else:
                try:
                    timestamp_value = float(ts)
                    if timestamp_value > 1e10:
                        timestamp_value /= 1000
                    return datetime.datetime.fromtimestamp(timestamp_value, tz=tz)
                except ValueError:
                    raise TypeError(_("无效的时间戳字符串: {0}").format(ts))
        elif isinstance(ts, (int, float)):
            timestamp_value = float(ts)
            if timestamp_value > 1e10:
                timestamp_value /= 1000
            return datetime.datetime.fromtimestamp(timestamp_value, tz=tz)
        else:
            raise TypeError(_("不支持的时间戳类型: {0}").format(type(ts)))

    # 如果是列表，则递归处理每个时间戳
    if isinstance(timestamp, list):
        return [
            (
                convert(ts).strftime(format)
                if not isinstance(ts, list)
                else [convert(t).strftime(format) for t in ts]
            )
            for ts in timestamp
        ]

    # 处理单个时间戳
    return convert(timestamp).strftime(format)


def str_2_timestamp(
    date_str: str,
    format: str = "%Y-%m-%d %H-%M-%S",
    unit: str = "milli",
    tz: datetime.timezone = datetime.timezone(datetime.timedelta(hours=8)),
) -> int:
    """
    将日期时间字符串转换为 UNIX 时间戳

    Args:
        date_str (str): 要转换的日期时间字符串 (The date-time string to be converted)
        format (str, optional): 日期时间字符串的格式，默认为 '%Y-%m-%d %H-%M-%S'。
                                (The format for the date-time string, defaults to '%Y-%m-%d %H-%M-%S')
        unit (str, optional): 时间单位，默认为 'milli'。 (The time unit, defaults to 'milli')
        tz (datetime.timezone, optional): 时区，默认为东八区北京时间 (The timezone, defaults to UTC+8)

    Returns:
        int: UNIX 时间戳 (The UNIX timestamp)
    """

    date_obj = datetime.datetime.strptime(date_str, format)
    if unit == "milli":
        return int(date_obj.replace(tzinfo=tz).timestamp() * 1000)
    elif unit == "sec":
        return int(date_obj.replace(tzinfo=tz).timestamp())
    elif unit == "min":
        return int(date_obj.replace(tzinfo=tz).timestamp() / 60)
    else:
        raise ValueError(_("不支持的时间单位：{0}").format(unit))


def interval_2_timestamp(
    interval: str,
    date_type: str = "start",
    format: str = "%Y-%m-%d %H-%M-%S",
    unit: str = "milli",
    tz: datetime.timezone = datetime.timezone(datetime.timedelta(hours=8)),
) -> int:
    """
    将日期区间字符串转换为 UNIX 时间戳区间

    Args:
        interval (str): 日期区间字符串，格式为 '2022-01-01|2023-01-01' (The date range string, formatted as '2022-01-01|2023-01-01')
        date_type (str, optional): 'start' 表示使用开始日期，'end' 表示使用结束日期 (Whether to use the start or end date, defaults to 'start')
        format (str, optional): 日期字符串的格式，默认为 '%Y-%m-%d' (The date string format, defaults to '%Y-%m-%d')
        unit (str, optional): 时间单位，默认为 'milli' (The time unit, defaults to 'milli')
        tz (datetime.timezone, optional): 时区，默认为东八区北京时间 (The timezone, defaults to UTC+8)

    Returns:
        int: UNIX 时间戳 (The UNIX timestamp)
    """

    if not interval:
        logger.warning(_("日期区间为空，无法转换为时间戳"))
        return 0

    try:
        start_date, end_date = interval.split("|")
        if date_type == "start":
            date_str = f"{start_date} 00-00-00"
        elif date_type == "end":
            date_str = f"{end_date} 23-59-59"
        else:
            logger.warning(_("不支持的日期类型：{0}").format(date_type))
            return 0

        return str_2_timestamp(date_str, format, unit, tz)
    except ValueError:
        trace_logger.error(traceback.format_exc())
        logger.error(_("日期区间参数格式错误，请查阅文档后重试"))
    return 0

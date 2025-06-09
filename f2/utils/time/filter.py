# path: f2/utils/time/filter.py

import datetime
from typing import Dict, List, Union

from f2.i18n.translator import _
from f2.log.logger import logger


async def filter_by_date_interval(
    data: Union[List[Dict], Dict],
    interval: str,
    field_name: str = "create_time",
) -> Union[List[Dict], Dict, None]:
    """
    筛选指定日期区间内的作品

    Args:
        data (Union[List[Dict], Dict]): 作品列表或单个作品
        interval (str): 日期区间，格式：2022-01-01|2023-01-01
        field_name (str): 日期字段名称，默认为"create_time"

    Returns:
        filtered_data (Union[List[Dict], Dict, None]): 筛选后的作品列表或单个作品
    """

    def is_within_interval(item: Dict) -> bool:
        date_str = item.get(field_name)
        if not date_str:
            logger.warning(_("作品缺少创建时间：{0}").format(item))
            return False
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H-%M-%S")
        except ValueError:
            logger.warning(_("无法解析作品的创建时间：{0}").format(date_str))
            return False

        if date < start_date or date > end_date:
            return False

        return True

    if not data or not interval:
        logger.error(_("作品或日期区间为空"))
        return None

    try:
        start_str, end_str = interval.split("|")
        start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d") + datetime.timedelta(
            days=1, seconds=-1
        )

        if end_date < start_date:
            logger.error(_("结束日期早于开始日期，请检查日期区间"))
            return None

    except ValueError:
        logger.error(_("日期区间参数格式错误，请查阅文档后重试"))
        return None

    if isinstance(data, dict):
        if is_within_interval(data):
            return data
        else:
            logger.warning(
                _("作品创作时间不在筛选日期区间内：{0}").format(data.get("create_time"))
            )
            return None

    elif isinstance(data, list):
        filtered_list = [item for item in data if is_within_interval(item)]
        if filtered_list:
            logger.info(
                _("在 {0} 条作品中有 {1} 条作品符合筛选日期条件：{2}").format(
                    len(data), len(filtered_list), interval
                )
            )
        else:
            logger.warning(_("没有找到符合条件的作品"))
        return filtered_list

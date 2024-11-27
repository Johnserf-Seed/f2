# path: f2/apps/tiktok/dl.py

import asyncio

from rich.live import Live
from rich.rule import Rule
from datetime import datetime
from typing import Any, Union

from f2.i18n.translator import _
from f2.log.logger import logger
from f2.dl.base_downloader import BaseDownloader
from f2.utils.utils import get_timestamp, timestamp_2_str, filter_by_date_interval
from f2.apps.tiktok.db import AsyncUserDB
from f2.apps.tiktok.utils import format_file_name
from f2.cli.cli_console import RichConsoleManager


class TiktokDownloader(BaseDownloader):
    def __init__(self, kwargs: dict = {}):
        if kwargs["cookie"] is None:
            raise ValueError(
                _(
                    "cookie不能为空。请提供有效的 cookie 参数，或自动从浏览器获取。如 `--auto-cookie edge`"
                )
            )

        super().__init__(kwargs)

    async def save_last_aweme_id(self, secUid: str, aweme_id: str) -> None:
        """
        保存最后一个请求的aweme_id
        (Save the last requested aweme_id)

        Args:
            aweme_id (str): 作品id (aweme_id)
        """

        async with AsyncUserDB("tiktok_users.db") as db:
            await db.update_user_info(secUid=secUid, last_aweme_id=aweme_id)

    async def filter_aweme_datas_by_interval(
        self, aweme_datas: Union[list, dict], interval: str
    ) -> Union[list[dict], dict, None]:
        """
        筛选指定日期区间内的作品

        Args:
            aweme_datas (Union[list, dict]): 作品数据列表
            interval (str): 日期区间，格式：2022-01-01|2023-01-01

        Returns:
            filtered_aweme_datas (Union[list, dict]): 筛选后的作品数据列表
        """

        if not aweme_datas or not interval:
            return None

        start_str, end_str = interval.split("|")

        try:
            start_date = datetime.strptime(start_str + " 00-00-00", "%Y-%m-%d %H-%M-%S")
            end_date = datetime.strptime(end_str + " 23-59-59", "%Y-%m-%d %H-%M-%S")
            logger.info(_("筛选日期区间：{0} 至 {1}").format(start_date, end_date))
        except ValueError:
            logger.error(_("日期区间参数格式错误，请查阅文档后重试"))
            return None

        if isinstance(aweme_datas, dict):
            aweme_date_str = aweme_datas.get("createTime")
            try:
                aweme_date = datetime.strptime(aweme_date_str, "%Y-%m-%d %H-%M-%S")
            except ValueError:
                logger.warning(_("无法解析作品发布时间：{0}").format(aweme_date_str))
                return None

            # 检查作品发布时间是否在指定区间内
            if start_date <= aweme_date <= end_date:
                logger.info(
                    _("作品发布时间在指定区间内：作品id {0} 发布时间 {1}").format(
                        aweme_datas.get("aweme_id"), aweme_date_str
                    )
                )
                return aweme_datas
            else:
                logger.warning(
                    _("作品发布时间不在指定区间内：{0}").format(aweme_date_str)
                )
                return None

        elif isinstance(aweme_datas, list):
            # 遍历列表中的每个字典
            filtered_list = []
            for aweme_data in aweme_datas:
                filtered_data = await self.filter_aweme_datas_by_interval(
                    aweme_data, interval
                )
                if filtered_data:
                    filtered_list.append(filtered_data)
            return filtered_list

    async def create_download_tasks(
        self, kwargs: dict, aweme_datas: Union[list, dict], user_path: Any
    ) -> None:
        """
        创建下载任务

        Args:
            kwargs (dict): 命令行参数
            aweme_datas (list, dict): 作品数据列表或字典
            user_path (str): 用户目录路径
        """

        if (
            not kwargs
            or not aweme_datas
            or not isinstance(aweme_datas, (list, dict))
            or not user_path
        ):
            return

        # 统一处理，将 aweme_datas 转为列表
        aweme_datas_list = (
            [aweme_datas] if isinstance(aweme_datas, dict) else aweme_datas
        )

        # 筛选指定日期区间内的作品
        if kwargs.get("interval") is None:
            logger.warning(_("未提供日期区间参数"))
        elif kwargs.get("interval") != "all":
            aweme_datas_list = await filter_by_date_interval(
                aweme_datas_list, kwargs.get("interval"), "createTime"
            )

        # 检查是否有符合条件的作品
        if not aweme_datas_list:
            logger.warning(_("没有找到符合条件的作品，请检查`interval`参数是否正确"))
            return

        # 使用 Rich 的 Live 管理器
        with Live(
            console=RichConsoleManager().rich_console,
            auto_refresh=False,
            # refresh_per_second=2,
            vertical_overflow="visible",
        ) as live:
            for aweme_data in aweme_datas_list:
                await self.handler_download(kwargs, aweme_data, user_path)
                # 手动刷新防止过快闪屏
                live.refresh()

            # 延时更新，避免过快刷新导致界面错乱
            await asyncio.sleep(0.2)
            # 动态更新规则输出
            live.update(Rule(_("当前任务处理完成")))

            await self.execute_tasks()

    async def handler_download(
        self, kwargs: dict, aweme_data_dict: dict, user_path: Any
    ) -> None:
        """
        处理下载任务

        Args:
            kwargs (dict): 命令行参数
        """

        # 构建文件夹路径
        base_path = (
            user_path
            / format_file_name(kwargs.get("naming", "{create}_{desc}"), aweme_data_dict)
            if kwargs.get("folderize")
            else user_path
        )

        secUid = str(aweme_data_dict.get("secUid"))  # 用户ID
        aweme_privateItem = aweme_data_dict.get(
            "privateItem"
        )  # 作品权限 false公开, true私密
        aweme_secret = aweme_data_dict.get("secret")  # 作品权限 false公开, true私密
        aweme_id = str(aweme_data_dict.get("aweme_id"))  # 视频ID

        logger.debug(f"========{aweme_id}========")
        logger.debug(aweme_data_dict)
        logger.debug("===================================")

        # 检查作品是否被屏蔽
        if aweme_privateItem:
            logger.warning(_("该 {0} 作品已被屏蔽，无法下载").format(aweme_id))
            return

        # 检查作品是否可见
        if not aweme_secret:
            video_name = (
                format_file_name(
                    kwargs.get("naming", "{create}_{desc}"), aweme_data_dict
                )
                + "_video"
            )

            video_url = aweme_data_dict.get("video_playAddr")
            if video_url != None:
                await self.initiate_download(
                    _("视频"), video_url, base_path, video_name, ".mp4"
                )
            else:
                logger.warning(_("{0} 该作品没有视频链接，无法下载").format(aweme_id))

            # 处理音乐下载任务
            if kwargs.get("music"):
                music_name = (
                    format_file_name(
                        kwargs.get("naming", "{create}_{desc}"), aweme_data_dict
                    )
                    + "_music"
                )

                music_url = aweme_data_dict.get("music_playUrl")
                if music_url != None:
                    await self.initiate_download(
                        _("原声"), music_url, base_path, music_name, ".mp3"
                    )
                else:
                    logger.warning(_("{0} 该原声已被屏蔽，无法下载").format(aweme_id))

            # 处理封面下载任务
            if kwargs.get("cover"):
                cover_name = (
                    format_file_name(
                        kwargs.get("naming", "{create}_{desc}"), aweme_data_dict
                    )
                    + "_cover"
                )
                animated_cover_url = aweme_data_dict.get("video_dynamicCover")
                cover_url = aweme_data_dict.get("video_cover")
                if animated_cover_url != None:
                    await self.initiate_download(
                        _("封面"), animated_cover_url, base_path, cover_name, ".webp"
                    )
                elif cover_url != None:
                    logger.debug(_("{0} 该作品没有动态封面").format(aweme_id))
                    await self.initiate_download(
                        _("封面"), cover_url, base_path, cover_name, ".jpeg"
                    )
                else:
                    logger.warning(_("{0} 该作品没有封面").format(aweme_id))

            # 处理文案下载任务
            if kwargs.get("desc"):
                desc_name = (
                    format_file_name(
                        kwargs.get("naming", "{create}_{desc}"), aweme_data_dict
                    )
                    + "_desc"
                )
                desc_content = aweme_data_dict.get("desc")
                await self.initiate_static_download(
                    _("文案"), desc_content, base_path, desc_name, ".txt"
                )

        # 保存最后一个aweme_id
        await self.save_last_aweme_id(secUid, aweme_id)

    async def create_stream_tasks(
        self, kwargs: dict, webcast_datas: Union[list, dict], user_path: Any
    ) -> None:
        """
        创建视频流下载任务

        Args:
            kwargs (dict): 命令行参数
            aweme_datas (list, dict): 作品数据列表或字典
            user_path (str): 用户目录路径
        """

        if (
            not kwargs
            or not webcast_datas
            or not isinstance(webcast_datas, (list, dict))
            or not user_path
        ):
            return

        if isinstance(webcast_datas, dict):
            await self.handler_stream(kwargs, webcast_datas, user_path)
        else:
            for webcast_data in webcast_datas:
                await self.handler_stream(kwargs, webcast_data, user_path)

        # 执行下载任务
        await self.execute_tasks()

    async def handler_stream(
        self, kwargs: dict, webcast_data_dict: dict, user_path: Any
    ) -> None:
        """
        处理视频流下载任务

        Args:
            kwargs (dict): 命令行参数
        """
        # 构建自定义字段
        custom_fields = {
            "create": timestamp_2_str(timestamp=get_timestamp(unit="sec")),
            "nickname": webcast_data_dict.get("nickname", ""),
            "uniqueId": webcast_data_dict.get("uniqueId", ""),
            "aweme_id": webcast_data_dict.get("live_room_id", ""),
            "desc": webcast_data_dict.get("live_title", ""),
            "uid": webcast_data_dict.get("user_id", ""),
        }

        # 格式化文件名
        formated_name = format_file_name(
            kwargs.get("naming", "{create}_{desc}"),
            webcast_data_dict,
            custom_fields=custom_fields,
        )

        # 构建文件夹路径
        base_path = user_path / formated_name if kwargs.get("folderize") else user_path

        webcast_name = f"{formated_name}_live"
        webcast_url = webcast_data_dict.get("live_hls_url", None)

        await self.initiate_m3u8_download(
            _("直播"), webcast_url, base_path, webcast_name, ".flv"
        )

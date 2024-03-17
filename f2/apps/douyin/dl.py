# path: f2/apps/douyin/dl.py

import sys
from datetime import datetime
from typing import Any, Union

from f2.i18n.translator import _
from f2.log.logger import logger
from f2.dl.base_downloader import BaseDownloader
from f2.utils.utils import get_timestamp, timestamp_2_str
from f2.apps.douyin.db import AsyncUserDB
from f2.apps.douyin.utils import format_file_name, json_2_lrc


class DouyinDownloader(BaseDownloader):
    def __init__(self, kwargs: dict = {}):
        if kwargs["cookie"] is None:
            raise ValueError(
                _(
                    "cookie不能为空。请提供有效的 cookie 参数，或自动从浏览器获取。如 `--auto-cookie edge`"
                )
            )

        super().__init__(kwargs)

    async def save_last_aweme_id(self, sec_user_id: str, aweme_id: int) -> None:
        """
        保存最后一个请求的aweme_id
        (Save the last requested aweme_id)

        Args:
            aweme_id (int): 作品id (aweme_id)
        """

        async with AsyncUserDB("douyin_users.db") as db:
            await db.update_user_info(sec_user_id=sec_user_id, last_aweme_id=aweme_id)

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
            aweme_date_str = aweme_datas.get("create_time")
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
        if kwargs.get("interval") != "all":
            aweme_datas_list = await self.filter_aweme_datas_by_interval(
                aweme_datas_list, kwargs.get("interval")
            )

        # 检查是否有符合条件的作品
        if not aweme_datas_list:
            logger.warning(_("没有找到符合条件的作品"))
            await self.close()
            sys.exit(0)

        # 创建下载任务
        for aweme_data in aweme_datas_list:
            await self.handler_download(kwargs, aweme_data, user_path)

        # 执行下载任务
        await self.execute_tasks()

    async def handler_download(
        self, kwargs: dict, aweme_data_dict: dict, user_path: Any
    ) -> None:
        """
        处理下载任务

        Args:
            kwargs (dict): 命令行参数
            aweme_data_dict (dict): 作品数据字典
            user_path (Any): 用户目录路径
        """

        # 构建文件夹路径
        base_path = (
            user_path
            / format_file_name(kwargs.get("naming", "{create}_{desc}"), aweme_data_dict)
            if kwargs.get("folderize")
            else user_path
        )

        sec_user_id = str(aweme_data_dict.get("sec_user_id"))  # 用户ID
        aweme_prohibited = aweme_data_dict.get("is_prohibited")  # 作品状态 0正常, 1屏蔽
        aweme_part_see = aweme_data_dict.get(
            "part_see"
        )  # 部分可见 part_see 1, private_status 1
        aweme_status = aweme_data_dict.get(
            "private_status"
        )  # 视频权限 0公开或不给谁看, 1私密, 2互关朋友
        aweme_type = aweme_data_dict.get(
            "aweme_type"
        )  # 视频类型 0视频, 55动图或关闭下载, 61挑战， 109日常, 68图集
        aweme_id = str(aweme_data_dict.get("aweme_id"))  # 视频ID

        logger.debug(f"========{aweme_id}========")
        logger.debug(aweme_data_dict)
        logger.debug("===================================")

        # 检查作品是否被屏蔽
        if aweme_prohibited:
            logger.warning(_("{0} 该作品已被屏蔽，无法下载").format(aweme_id))
            return

        # 检查作品是否可见
        if aweme_status in [0, 1, 2]:
            # 处理音乐下载任务
            if kwargs.get("music"):
                if aweme_data_dict.get("music_status") == 1:  # 原声状态 1 正常 0 失效
                    music_name = (
                        format_file_name(
                            kwargs.get("naming", "{create}_{desc}"), aweme_data_dict
                        )
                        + "_music"
                    )

                    music_url = aweme_data_dict.get("music_play_url")
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
                animated_cover_url = aweme_data_dict.get("animated_cover")
                cover_url = aweme_data_dict.get("cover")
                if animated_cover_url != None:
                    await self.initiate_download(
                        _("封面"), animated_cover_url, base_path, cover_name, ".webp"
                    )
                elif cover_url != None:
                    logger.warning(_("{0} 该作品没有动态封面").format(aweme_id))
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

            # 处理不同类型的作品下载任务
            if aweme_type in [0, 55, 61, 109]:
                video_name = (
                    format_file_name(
                        kwargs.get("naming", "{create}_{desc}"), aweme_data_dict
                    )
                    + "_video"
                )

                video_url = aweme_data_dict.get("video_play_addr")
                if video_url != None:
                    await self.initiate_download(
                        _("视频"), video_url, base_path, video_name, ".mp4"
                    )
                else:
                    logger.warning(
                        _("{0} 该作品没有视频链接，无法下载").format(aweme_id)
                    )

            elif aweme_type in [68]:
                for i, image_url in enumerate(aweme_data_dict.get("images", None)):
                    image_name = f"{format_file_name(kwargs.get('naming'), aweme_data_dict)}_image_{i + 1}"
                    if image_url != None:
                        await self.initiate_download(
                            _("图集"), image_url, base_path, image_name, ".jpg"
                        )
                    else:
                        logger.warning(
                            _("{0} 该图集没有图片链接，无法下载").format(aweme_id)
                        )

        # 保存最后一个aweme_id
        await self.save_last_aweme_id(sec_user_id, aweme_id)

    async def create_music_download_tasks(
        self, kwargs: dict, music_datas: Union[list, dict], user_path: Any
    ) -> None:
        """
        创建音乐下载任务

        Args:
            kwargs (dict): 命令行参数
            music_datas (list, dict): 音乐数据列表或字典
            user_path (Any): 用户目录路径
        """

        if (
            not kwargs
            or not music_datas
            or not isinstance(music_datas, (list, dict))
            or not user_path
        ):
            return

        if isinstance(music_datas, dict):
            await self.handler_music_download(kwargs, music_datas, user_path)
        else:
            for music_data in music_datas:
                await self.handler_music_download(kwargs, music_data, user_path)

        # 执行下载任务
        await self.execute_tasks()

    async def handler_music_download(
        self, kwargs: dict, music_data_dict: dict, user_path: Any
    ) -> None:
        """
        处理音乐下载任务

        Args:
            kwargs (dict): 命令行参数
            music_data_dict (dict): 音乐数据字典
            user_path (Any): 用户目录路径
        """

        # 构建文件夹路径
        base_path = (
            user_path / music_data_dict.get("title")
            if kwargs.get("folderize")
            else user_path
        )
        music_name = music_data_dict.get("title") + "_music"
        music_url = music_data_dict.get("play_url")
        lyric_name = music_data_dict.get("title") + "_lyric"
        lyric_url = music_data_dict.get("lyric_url")

        if music_url != None:
            await self.initiate_download(
                _("音乐"), music_url, base_path, music_name, ".mp3"
            )

        if kwargs.get("lyric"):
            if lyric_url is None:
                return

            # 下载str格式的json歌词文件
            lyric = await self.get_fetch_data(lyric_url)

            # 如果json歌词文件下载成功，则读取并处理成lrc格式
            if lyric.status_code != 200:
                return

            lrc_content = json_2_lrc(lyric.json())
            await self.initiate_static_download(
                _("歌词"), lrc_content, base_path, lyric_name, ".lrc"
            )

    async def create_stream_tasks(
        self, kwargs: dict, webcast_datas: Union[list, dict], user_path: Any
    ) -> None:
        """
        创建视频流下载任务

        Args:
            kwargs (dict): 命令行参数
            aweme_datas (list, dict): 作品数据列表或字典
            user_path (Any): 用户目录路径
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
            aweme_data_dict (dict): 直播数据字典
            user_path (Any): 用户目录路径
        """
        custom_fields = {
            "create": timestamp_2_str(timestamp=get_timestamp(unit="sec")),
            "nickname": webcast_data_dict.get("nickname", ""),
            "aweme_id": webcast_data_dict.get("room_id", ""),
            "desc": webcast_data_dict.get("live_title", ""),
            "uid": webcast_data_dict.get("user_id", ""),
        }
        # 构建文件夹路径
        base_path = (
            user_path
            / format_file_name(
                kwargs.get("naming", "{create}_{desc}"), custom_fields=custom_fields
            )
            if kwargs.get("folderize")
            else user_path
        )

        webcast_name = f"{format_file_name(kwargs.get('naming'), custom_fields=custom_fields)}_live"
        webcast_url = webcast_data_dict.get("m3u8_pull_url").get("FULL_HD1")

        await self.initiate_m3u8_download(
            _("直播"), webcast_url, base_path, webcast_name, ".mp4"
        )

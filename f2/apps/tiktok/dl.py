# path: f2/apps/tiktok/dl.py

import f2
from typing import Any, Union
from f2.i18n.translator import _
from f2.log.logger import logger
from f2.dl.base_downloader import BaseDownloader
from f2.utils.conf_manager import ConfigManager
from f2.utils.utils import get_timestamp, timestamp_2_str
from f2.apps.tiktok.db import AsyncUserDB
from f2.apps.tiktok.utils import format_file_name


class TiktokDownloader(BaseDownloader):
    def __init__(self):
        app_manager = ConfigManager(f2.APP_CONFIG_FILE_PATH)
        tiktok_conf = app_manager.get_config("tiktok")
        proxies_conf = tiktok_conf.get("proxies", None)
        proxies = {
            "http://": proxies_conf.get("http", None),
            "https://": proxies_conf.get("https", None),
        }
        self.headers = {
            "User-Agent": tiktok_conf["headers"]["User-Agent"],
            "Referer": tiktok_conf["headers"]["Referer"],
            "Cookie": tiktok_conf["cookie"],
        }
        super().__init__(proxies=proxies, headers=self.headers)

    async def save_last_aweme_id(self, secUid: str, aweme_id: str) -> None:
        """
        保存最后一个请求的aweme_id
        (Save the last requested aweme_id)

        Args:
            aweme_id (str): 作品id (aweme_id)
        """

        async with AsyncUserDB("tiktok_users.db") as db:
            await db.update_user_info(secUid=secUid, last_aweme_id=aweme_id)

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

        if isinstance(aweme_datas, dict):
            await self.handler_download(kwargs, aweme_datas, user_path)
        else:
            for aweme_data in aweme_datas:
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
        """

        # 构建文件夹路径
        base_path = (
            user_path
            / format_file_name(kwargs.get("naming", "{create}_{desc}"), aweme_data_dict)
            if kwargs.get("folderize")
            else user_path
        )

        secUid = str(aweme_data_dict.get("secUid"))  # 用户ID
        aweme_privateItem = aweme_data_dict.get("privateItem")  # 作品权限 false公开, true私密
        aweme_secret = aweme_data_dict.get("secret")  # 作品权限 false公开, true私密
        aweme_id = str(aweme_data_dict.get("aweme_id"))  # 视频ID

        logger.debug(f"========{aweme_id}========")
        logger.debug(aweme_data_dict)
        logger.debug("================")

        # 检查作品是否被屏蔽
        if aweme_privateItem:
            logger.warning(_("{0} 该作品已被屏蔽，无法下载").format(aweme_id))
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

        webcast_name = f"{format_file_name(kwargs.get('naming', '{create}_{desc}'), custom_fields=custom_fields)}_live"
        webcast_url = webcast_data_dict.get("m3u8_pull_url", None).get("FULL_HD1")

        await self.initiate_m3u8_download(
            _("直播"), webcast_url, base_path, webcast_name, ".mp4"
        )

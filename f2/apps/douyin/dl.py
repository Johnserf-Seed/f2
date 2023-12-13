# path: f2/apps/douyin/dl.py

import f2
from typing import Any, Union
from f2.i18n.translator import _
from f2.log.logger import logger
from f2.dl.base_downloader import BaseDownloader
from f2.utils.conf_manager import ConfigManager
from f2.utils.utils import get_timestamp, timestamp_2_str
from f2.apps.douyin.db import AsyncUserDB
from f2.apps.douyin.utils import format_file_name


class DouyinDownloader(BaseDownloader):
    def __init__(self):
        app_manager = ConfigManager(f2.APP_CONFIG_FILE_PATH)
        douyin_conf = app_manager.get_config("douyin")
        proxies_conf = douyin_conf.get("proxies", None)
        proxies = {
            "http://": proxies_conf.get("http", None),
            "https://": proxies_conf.get("https", None),
        }
        self.headers = {
            "User-Agent": douyin_conf["headers"]["User-Agent"],
            "Referer": douyin_conf["headers"]["Referer"],
            "Cookie": douyin_conf["cookie"],
        }
        super().__init__(proxies=proxies, headers=self.headers)

    async def save_last_aweme_id(self, sec_user_id: str, aweme_id: int) -> None:
        """
        保存最后一个请求的aweme_id
        (Save the last requested aweme_id)

        Args:
            aweme_id (int): 作品id (aweme_id)
        """

        async with AsyncUserDB("douyin_users.db") as db:
            await db.update_user_info(sec_user_id=sec_user_id, last_aweme_id=aweme_id)

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
        logger.debug("================")

        # 检查作品是否被屏蔽
        if aweme_prohibited:
            logger.warning(
                _("{0} 该作品已被屏蔽，无法下载").format(aweme_id)
            )  # This work has been blocked and cannot be downloaded
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
                    logger.warning(
                        _("{0} 该原声已被屏蔽，无法下载").format(aweme_id)
                    )  # This original sound has been blocked and cannot be downloaded

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
                    logger.warning(
                        _("{0} 该作品没有动态封面").format(aweme_id)
                    )  # This video has no dynamic cover
                    await self.initiate_download(
                        _("封面"), cover_url, base_path, cover_name, ".jpeg"
                    )
                else:
                    logger.warning(
                        _("{0} 该作品没有封面").format(aweme_id)
                    )  # This video has no cover

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
                    )  # This video has no video link and cannot be downloaded

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
                        )  # This atlas has no picture link and cannot be downloaded

        # 保存最后一个aweme_id
        await self.save_last_aweme_id(sec_user_id, aweme_id)

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

        webcast_name = f"{format_file_name(kwargs.get('naming'), custom_fields=custom_fields)}_live"
        webcast_url = webcast_data_dict.get("m3u8_pull_url").get("FULL_HD1")

        await self.initiate_m3u8_download(
            _("直播"), webcast_url, base_path, webcast_name, ".mp4"
        )

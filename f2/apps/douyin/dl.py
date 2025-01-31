# path: f2/apps/douyin/dl.py

import asyncio

from rich.live import Live
from rich.rule import Rule
from typing import Any, Dict, List, Union

from f2.i18n.translator import _
from f2.log.logger import logger
from f2.dl.base_downloader import BaseDownloader
from f2.utils.utils import get_timestamp, timestamp_2_str, filter_by_date_interval
from f2.apps.douyin.db import AsyncUserDB
from f2.apps.douyin.utils import format_file_name, json_2_lrc
from f2.cli.cli_console import RichConsoleManager


class DouyinDownloader(BaseDownloader):
    def __init__(self, kwargs: Dict = {}):
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

    async def create_download_tasks(
        self,
        kwargs: Dict,
        aweme_datas: Union[List, Dict],
        user_path: Any,
    ) -> None:
        """
        创建下载任务

        Args:
            kwargs (Dict): 命令行参数
            aweme_datas (List, Dict): 作品数据列表或字典
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
                aweme_datas_list, kwargs.get("interval"), "create_time"
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
        self, kwargs: Dict, aweme_data_dict: Dict, user_path: Any
    ) -> None:
        """
        处理下载任务

        Args:
            kwargs (Dict): 命令行参数
            aweme_data_dict (Dict): 作品数据字典
            user_path (Any): 用户目录路径
        """
        self.base_path = (
            user_path
            / format_file_name(kwargs.get("naming", "{create}_{desc}"), aweme_data_dict)
            if kwargs.get("folderize")
            else user_path
        )

        self.sec_user_id = str(aweme_data_dict.get("sec_user_id"))
        self.aweme_id = str(aweme_data_dict.get("aweme_id"))
        self.kwargs = kwargs
        self.aweme_data_dict = aweme_data_dict

        aweme_prohibited = aweme_data_dict.get("is_prohibited")
        aweme_status = aweme_data_dict.get("private_status")
        aweme_type = aweme_data_dict.get("aweme_type")

        if aweme_prohibited:
            logger.warning(_("[{0}] 该作品已被屏蔽，无法下载").format(self.aweme_id))
            return

        if aweme_status in [0, 1, 2]:
            download_tasks = [
                ("music", self.download_music),
                ("cover", self.download_cover),
                ("desc", self.download_desc),
            ]

            for task_name, task_func in download_tasks:
                if self.kwargs.get(task_name):
                    await task_func()

            if aweme_type in [0, 55, 61, 109, 201]:
                await self.download_video()
            elif aweme_type == 68:
                await self.download_images()

        # 保存最后一个 aweme_id
        await self.save_last_aweme_id(self.sec_user_id, self.aweme_id)

    async def download_music(self):
        if self.aweme_data_dict.get("music_status") == 1:
            music_name = (
                format_file_name(
                    self.kwargs.get("naming", "{create}_{desc}"), self.aweme_data_dict
                )
                + "_music"
            )
            music_url = self.aweme_data_dict.get("music_play_url")
            if music_url:
                await self.initiate_download(
                    _("原声"), music_url, self.base_path, music_name, ".mp3"
                )
        else:
            logger.warning(_("[{0}] 该原声已被屏蔽，无法下载").format(self.aweme_id))

    async def download_cover(self):
        cover_name = (
            format_file_name(
                self.kwargs.get("naming", "{create}_{desc}"), self.aweme_data_dict
            )
            + "_cover"
        )
        animated_cover_url = self.aweme_data_dict.get("animated_cover")
        cover_url = self.aweme_data_dict.get("cover")
        if animated_cover_url:
            await self.initiate_download(
                _("封面"), animated_cover_url, self.base_path, cover_name, ".webp"
            )
        elif cover_url:
            logger.debug(_("[{0}] 该作品没有动态封面").format(self.aweme_id))
            await self.initiate_download(
                _("封面"), cover_url, self.base_path, cover_name, ".jpeg"
            )
        else:
            logger.warning(_("[{0}] 该作品没有封面").format(self.aweme_id))

    async def download_desc(self):
        desc_name = (
            format_file_name(
                self.kwargs.get("naming", "{create}_{desc}"), self.aweme_data_dict
            )
            + "_desc"
        )
        # 保存原始文案
        desc_content = self.aweme_data_dict.get("desc_raw")
        await self.initiate_static_download(
            _("文案"), desc_content, self.base_path, desc_name, ".txt"
        )

    async def download_video(self):
        video_name = (
            format_file_name(
                self.kwargs.get("naming", "{create}_{desc}"), self.aweme_data_dict
            )
            + "_video"
        )
        video_url = self.aweme_data_dict.get("video_play_addr")
        if video_url:
            await self.initiate_download(
                _("视频"), video_url, self.base_path, video_name, ".mp4"
            )
        else:
            logger.warning(
                _("[{0}] 该作品没有视频链接，无法下载").format(self.aweme_id)
            )

    async def download_images(self):
        # 处理实况视频下载
        images_video_list = self.aweme_data_dict.get("images_video", [])
        if images_video_list:
            for i, images_video_url in enumerate(images_video_list):
                image_video_name = f"{format_file_name(self.kwargs.get('naming'), self.aweme_data_dict)}_live_{i + 1}"
                if images_video_url:
                    await self.initiate_download(
                        _("实况"),
                        images_video_url,
                        self.base_path,
                        image_video_name,
                        ".mp4",
                    )
                else:
                    logger.warning(
                        _("[{0}] 该图集没有实况链接，无法下载").format(self.aweme_id)
                    )
        else:
            logger.info(_("[{0}] 非实况图集，跳过实况下载").format(self.aweme_id))

        # 处理图片下载
        for i, image_url in enumerate(self.aweme_data_dict.get("images", [])):
            image_name = f"{format_file_name(self.kwargs.get('naming'), self.aweme_data_dict)}_image_{i + 1}"
            if image_url:
                await self.initiate_download(
                    _("图集"), image_url, self.base_path, image_name, ".webp"
                )
            else:
                logger.warning(
                    _("[{0}] 该图集没有图片链接，无法下载").format(self.aweme_id)
                )

    async def create_music_download_tasks(
        self, kwargs: Dict, music_datas: Union[List, Dict], user_path: Any
    ) -> None:
        """
        创建音乐下载任务

        Args:
            kwargs (Dict): 命令行参数
            music_datas (List, Dict): 音乐数据列表或字典
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
        self, kwargs: Dict, music_data_dict: Dict, user_path: Any
    ) -> None:
        """
        处理音乐下载任务

        Args:
            kwargs (Dict): 命令行参数
            music_data_dict (Dict): 音乐数据字典
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
        self, kwargs: Dict, webcast_datas: Union[List, Dict], user_path: Any
    ) -> None:
        """
        创建视频流下载任务

        Args:
            kwargs (Dict): 命令行参数
            aweme_datas (List, Dict): 作品数据列表或字典
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
        self, kwargs: Dict, webcast_data_dict: Dict, user_path: Any
    ) -> None:
        """
        处理视频流下载任务

        Args:
            kwargs (Dict): 命令行参数
            aweme_data_dict (Dict): 直播数据字典
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
            _("直播"), webcast_url, base_path, webcast_name, ".flv"
        )

# path: f2/apps/douyin/dl.py

import asyncio
import traceback
from typing import Any, Dict, List, Optional, Union

from rich.live import Live
from rich.rule import Rule

from f2.apps.douyin.db import AsyncUserDB
from f2.apps.douyin.utils import format_file_name, json_2_lrc
from f2.cli.cli_console import RichConsoleManager
from f2.dl.base_downloader import BaseDownloader
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.time.filter import filter_by_date_interval
from f2.utils.time.timestamp import get_timestamp, timestamp_2_str


class DouyinDownloader(BaseDownloader):
    # 图集作品的类型。其他类型只要带有视频链接就按视频下载，
    # 抖音新增的 51、53、66 等类型与视频的数据结构相同（#402）
    IMAGE_AWEME_TYPES = frozenset({68})

    def __init__(self, kwargs: Optional[dict] = None):
        kwargs = kwargs or {}
        if kwargs["cookie"] is None:
            raise ValueError(
                _(
                    "cookie不能为空。请提供有效的 cookie 参数，或自动从浏览器获取。如 `--auto-cookie edge`"
                )
            )

        super().__init__(kwargs)
        self._live_status_callback_user_id = None  # 用于回调函数的user_id

    async def save_last_aweme_id(self, sec_user_id: str, aweme_id: str) -> None:
        """
        保存最后一个请求的aweme_id
        (Save the last requested aweme_id)

        Args:
            aweme_id (str): 作品id (aweme_id)
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
            kwargs (dict): 命令行参数
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
            logger.debug(_("未提供日期区间参数，将处理所有作品"))
        elif kwargs.get("interval") != "all":
            logger.debug(
                _("开始按日期区间筛选作品：{0}").format(kwargs.get("interval"))
            )
            filtered_data = await filter_by_date_interval(
                aweme_datas_list, str(kwargs.get("interval")), "create_time"
            )
            # 处理返回结果确保类型一致
            if filtered_data is None:
                aweme_datas_list = []
            elif isinstance(filtered_data, dict):
                aweme_datas_list = [filtered_data]
            else:
                aweme_datas_list = filtered_data

        # 检查是否有符合条件的作品
        if not aweme_datas_list:
            if kwargs.get("interval") and kwargs.get("interval") != "all":
                logger.warning(
                    _("没有找到更多符合日期区间 '{0}' 的作品，请检查参数设置").format(
                        kwargs.get("interval")
                    )
                )
            else:
                logger.warning(_("没有可处理的作品数据"))
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
            kwargs (dict): 命令行参数
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

            await self.download_media(aweme_type)
        else:
            logger.warning(
                _("[{0}] 作品的可见状态 private_status={1} 不支持下载，已跳过").format(
                    self.aweme_id, aweme_status
                )
            )

        # 保存最后一个 aweme_id
        await self.save_last_aweme_id(self.sec_user_id, self.aweme_id)

    async def download_media(self, aweme_type: Any) -> None:
        """
        按作品数据选择下载内容：图集类型或带有图片时下载图集，否则有视频链接就下载视频

        Args:
            aweme_type (Any): 作品类型
        """
        if aweme_type in self.IMAGE_AWEME_TYPES or self.aweme_data_dict.get("images"):
            await self.download_images()
        elif self.aweme_data_dict.get("video_play_addr"):
            await self.download_video()
        else:
            logger.warning(
                _("[{0}] 作品类型 {1} 没有可下载的视频或图片").format(
                    self.aweme_id, aweme_type
                )
            )

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
        """
        下载作品封面，按优先级尝试：动画封面 -> 动态封面 -> 静态封面

        优先下载质量最好的封面类型，如果首选类型不存在则尝试下一种类型
        """
        cover_name = (
            format_file_name(
                self.kwargs.get("naming", "{create}_{desc}"), self.aweme_data_dict
            )
            + "_cover"
        )
        # 获取所有可能的封面URL
        animated_cover_url = self.aweme_data_dict.get(
            "animated_cover"
        )  # 动画封面（gif格式）
        dynamic_cover_url = self.aweme_data_dict.get(
            "dynamic_cover"
        )  # 动态封面（通常质量更好）
        static_cover_url = self.aweme_data_dict.get("cover")  # 静态封面（webp格式）

        # 尝试按优先级下载不同类型的封面
        if animated_cover_url:
            logger.debug(_("[{0}] 正在下载动画封面").format(self.aweme_id))
            await self.initiate_download(
                _("动画封面"), animated_cover_url, self.base_path, cover_name, ".gif"
            )
        elif dynamic_cover_url:
            logger.debug(
                _("[{0}] 没有动画封面，正在下载动态封面").format(self.aweme_id)
            )
            await self.initiate_download(
                _("动态封面"), dynamic_cover_url, self.base_path, cover_name, ".gif"
            )
        elif static_cover_url:
            logger.debug(
                _("[{0}] 没有动画或动态封面，正在下载静态封面").format(self.aweme_id)
            )
            await self.initiate_download(
                _("静态封面"), static_cover_url, self.base_path, cover_name, ".webp"
            )
        else:
            logger.warning(_("[{0}] 该作品没有任何可用的封面").format(self.aweme_id))

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
        """
        下载图集相关内容，包括实况视频和图片

        处理逻辑：
        1. 优先检查并下载实况视频（如果存在）
        2. 下载图集中的所有图片
        3. 所有下载都使用统一的命名格式
        """
        # 获取基础文件名格式
        base_filename = format_file_name(
            self.kwargs.get("naming", "{create}_{desc}"), self.aweme_data_dict
        )

        # 处理实况视频下载
        await self._download_live_videos(base_filename)

        # 处理图片下载
        await self._download_gallery_images(base_filename)

    async def _download_live_videos(self, base_filename):
        """下载图集中的实况视频"""
        images_video_list = self.aweme_data_dict.get("images_video", [])

        if not images_video_list:
            logger.info(_("[{0}] 非实况图集，跳过实况视频下载").format(self.aweme_id))
            return

        # 首先过滤出有效的视频链接
        valid_videos = [url for url in images_video_list if url]

        if not valid_videos:
            logger.info(_("[{0}] 未找到有效的实况视频链接").format(self.aweme_id))
            return

        logger.info(
            _("[{0}] 检测到有效实况视频，共 {1} 个").format(
                self.aweme_id, len(valid_videos)
            )
        )

        # 使用原始列表的索引以保持序号一致
        for i, images_video_url in enumerate(images_video_list):
            if not images_video_url:
                logger.debug(
                    _("[{0}] 第 {1} 个实况视频链接无效，跳过").format(
                        self.aweme_id, i + 1
                    )
                )
                continue

            image_video_name = f"{base_filename}_live_{i + 1}"

            # 使用有效视频列表长度作为总数
            await self.initiate_download(
                _("实况 {0}/{1}").format(i + 1, len(images_video_list)),
                images_video_url,
                self.base_path,
                image_video_name,
                ".mp4",
            )

    async def _download_gallery_images(self, base_filename):
        """下载图集中的所有图片"""
        images = self.aweme_data_dict.get("images", [])

        if not images:
            logger.warning(
                _("[{0}] 未找到任何图片，请检查作品信息").format(self.aweme_id)
            )
            return

        logger.info(
            _("[{0}] 开始下载图集，共 {1} 张图片").format(self.aweme_id, len(images))
        )

        for i, image_url in enumerate(images):
            if not image_url:
                logger.warning(
                    _("[{0}] 第 {1} 张图片链接无效，跳过").format(self.aweme_id, i + 1)
                )
                continue

            image_name = f"{base_filename}_image_{i + 1}"

            await self.initiate_download(
                _("图集 {0}/{1}").format(i + 1, len(images)),
                image_url,
                self.base_path,
                image_name,
                ".webp",
            )

    async def create_music_download_tasks(
        self, kwargs: Dict, music_datas: Union[List, Dict], user_path: Any
    ) -> None:
        """
        创建音乐下载任务

        Args:
            kwargs (dict): 命令行参数
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
            kwargs (dict): 命令行参数
            music_data_dict (Dict): 音乐数据字典
            user_path (Any): 用户目录路径
        """

        # 构建文件夹路径
        base_path = (
            user_path / music_data_dict.get("title")
            if kwargs.get("folderize")
            else user_path
        )
        music_name = music_data_dict.get("title", "") + "_music"
        music_url = music_data_dict.get("play_url")
        lyric_name = music_data_dict.get("title", "") + "_lyric"
        lyric_url = music_data_dict.get("lyric_url")

        if music_url is not None:
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
            kwargs (dict): 命令行参数
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

    async def _check_live_status_callback(self) -> str:
        """
        直播状态检查回调函数

        Returns:
            str: 直播状态描述
        """
        if not self._live_status_callback_user_id:
            return _("无法验证直播状态（缺少用户ID）")

        # 动态导入避免循环依赖
        from f2.apps.douyin.handler import DouyinHandler

        try:
            handler = DouyinHandler(self.kwargs)
            live_status = await handler.fetch_user_live_status(
                self._live_status_callback_user_id
            )

            # 映射直播状态
            status_map = {
                0: _("未开播"),
                1: _("已关播"),
                2: _("直播中"),
                4: _("已关播"),
            }
            status_text = status_map.get(live_status.live_status, _("未知状态"))

            return _("直播状态：{0}").format(status_text)
        except Exception as e:
            logger.error(_("验证直播状态失败：{0}").format(e))
            trace_logger.error(traceback.format_exc())
            return _("无法验证直播状态（异常：{0}）").format(str(e))

    async def handler_stream(
        self, kwargs: Dict, webcast_data_dict: Dict, user_path: Any
    ) -> None:
        """
        处理视频流下载任务

        Args:
            kwargs (dict): 命令行参数
            aweme_data_dict (Dict): 直播数据字典
            user_path (Any): 用户目录路径
        """
        # 保存 kwargs 供回调函数使用
        self.kwargs = kwargs

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

        webcast_name = (
            format_file_name(
                kwargs.get("naming", "{create}_{desc}"), custom_fields=custom_fields
            )
            + "_live"
        )
        webcast_url = webcast_data_dict.get("m3u8_pull_url", {}).get("FULL_HD1")

        # 设置回调函数需要的user_id
        self._live_status_callback_user_id = webcast_data_dict.get("user_id", "")

        await self.initiate_m3u8_download(
            _("直播"),
            webcast_url,
            base_path,
            webcast_name,
            ".flv",
            stream_status_callback=self._check_live_status_callback,
        )

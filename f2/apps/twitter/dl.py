# path: f2/apps/twitter/dl.py

import asyncio

from rich.live import Live
from rich.rule import Rule
from typing import Any, Union

from f2.i18n.translator import _
from f2.log.logger import logger
from f2.dl.base_downloader import BaseDownloader
from f2.utils.utils import filter_by_date_interval
from f2.apps.twitter.utils import format_file_name
from f2.cli.cli_console import RichConsoleManager


class TwitterDownloader(BaseDownloader):
    def __init__(self, kwargs: dict = {}):
        if kwargs["cookie"] is None:
            raise ValueError(
                _(
                    "cookie不能为空。请提供有效的 cookie 参数，或自动从浏览器获取。如 `--auto-cookie edge`"
                )
            )

        super().__init__(kwargs)

    async def create_download_tasks(
        self,
        kwargs: dict,
        tweet_datas: Union[list, dict],
        user_path: Any,
    ) -> None:
        """
        创建下载任务

        Args:
            kwargs (dict): 命令行参数
            tweet_datas (list, dict): 推文数据列表或字典
            user_path (str): 用户目录路径
        """
        if (
            not kwargs
            or not tweet_datas
            or not isinstance(tweet_datas, (list, dict))
            or not user_path
        ):
            return

        # 统一处理，将 tweet_datas 转为列表
        tweet_datas_list = (
            [tweet_datas] if isinstance(tweet_datas, dict) else tweet_datas
        )

        # 筛选指定日期区间内的推文
        if kwargs.get("interval") is None:
            logger.warning(_("未提供日期区间参数"))
        elif kwargs.get("interval") != "all":
            tweet_datas_list = await filter_by_date_interval(
                tweet_datas_list, kwargs.get("interval"), "tweet_created_at"
            )

        # 检查是否有符合条件的推文
        if not tweet_datas_list:
            logger.warning(_("没有找到符合条件的推文，请检查`interval`参数是否正确"))
            return

        # 使用 Rich 的 Live 管理器
        with Live(
            console=RichConsoleManager().rich_console,
            auto_refresh=False,
            # refresh_per_second=2,
            vertical_overflow="visible",
        ) as live:
            for tweet_data in tweet_datas_list:
                await self.handler_download(kwargs, tweet_data, user_path)
                # 手动刷新防止过快闪屏
                live.refresh()

            # 延时更新，避免过快刷新导致界面错乱
            await asyncio.sleep(0.2)
            # 动态更新规则输出
            live.update(Rule(_("当前任务处理完成")))

            await self.execute_tasks()

    async def handler_download(
        self, kwargs: dict, tweet_data_dict: dict, user_path: Any
    ) -> None:
        """
        处理下载任务

        Args:
            kwargs (dict): 命令行参数
            tweet_data_dict (dict): 作品数据字典
            user_path (Any): 用户目录路径
        """

        # 构建文件夹路径
        self.base_path = (
            user_path
            / format_file_name(kwargs.get("naming", "{create}_{desc}"), tweet_data_dict)
            if kwargs.get("folderize")
            else user_path
        )

        self.user_id = tweet_data_dict.get("user_id")
        if self.user_id is None:
            logger.debug(_("跳过下载用户推荐或广告推文"))
            return

        self.kwargs = kwargs
        self.tweet_data_dict = tweet_data_dict
        self.tweet_id = tweet_data_dict.get("tweet_id")
        self.tweet_media_type = tweet_data_dict.get("tweet_media_type")
        self.tweet_media_url = tweet_data_dict.get("tweet_media_url")
        self.tweet_video_url = tweet_data_dict.get("tweet_video_url")

        # logger.info(f"========{tweet_id}========")
        # logger.info(tweet_data_dict)
        # logger.info("===================================")

        # 动图属于视频类型
        if self.tweet_media_type in ["video", "animated_gif"]:
            await self.download_video()
        elif self.tweet_media_type and "photo" in self.tweet_media_type:
            await self.download_images()

        await self.download_desc()

    async def download_video(self):
        if not self.tweet_video_url:
            logger.warning(_("{0} : 视频链接为空").format(self.tweet_id))
            return

        video_name = (
            format_file_name(
                self.kwargs.get("naming", "{create}_{desc}"), self.tweet_data_dict
            )
            + "_video"
        )

        if isinstance(self.tweet_video_url, list):
            self.tweet_video_url = self.tweet_video_url[-1]  # 如果是列表，取第一个元素

        await self.initiate_download(
            _("视频"), self.tweet_video_url, self.base_path, video_name, ".mp4"
        )

    async def download_images(self):
        if not self.tweet_media_url:
            logger.warning(
                _("{0} : {1} 该推文没有图片链接").format(
                    self.tweet_id, self.tweet_data_dict.get("tweet_desc")
                )
            )
            return

        tweet_media_urls = (
            [self.tweet_media_url]
            if isinstance(self.tweet_media_url, str)
            else self.tweet_media_url
        )

        for i, image_url in enumerate(tweet_media_urls):
            if not image_url:
                continue

            image_name = f"{format_file_name(self.kwargs.get('naming'), self.tweet_data_dict)}_image_{i + 1}"
            await self.initiate_download(
                _("图片"),
                f"{image_url}?format=jpg&name=large",
                self.base_path,
                image_name,
                ".jpg",
            )

    async def download_desc(self):
        desc_name = (
            format_file_name(
                self.kwargs.get("naming", "{create}_{desc}"), self.tweet_data_dict
            )
            + "_desc"
        )
        desc_content = (
            ""
            if self.tweet_data_dict.get("tweet_desc_raw") is None
            else self.tweet_data_dict.get("tweet_desc_raw")
        )

        await self.initiate_static_download(
            _("文案"), desc_content, self.base_path, desc_name, ".txt"
        )

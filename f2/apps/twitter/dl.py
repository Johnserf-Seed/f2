# path: f2/apps/twitter/dl.py

import sys
from datetime import datetime
from typing import Any, Union

from f2.i18n.translator import _
from f2.log.logger import logger
from f2.dl.base_downloader import BaseDownloader
from f2.utils.utils import get_timestamp, timestamp_2_str
from f2.apps.twitter.db import AsyncUserDB
from f2.apps.twitter.utils import format_file_name


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
        self, kwargs: dict, tweet_datas: Union[list, dict], user_path: Any
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
        if kwargs.get("interval") != "all":
            tweet_datas_list = await self.filter_tweet_datas_by_interval(
                tweet_datas_list, kwargs.get("interval")
            )

        # 检查是否有符合条件的推文
        if not tweet_datas_list:
            logger.warning(_("没有找到符合条件的推文"))
            await self.close()
            sys.exit(0)

        # 创建下载任务
        for tweet_data in tweet_datas_list:
            await self.handler_download(kwargs, tweet_data, user_path)

        # 执行下载任务
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

        user_id = tweet_data_dict.get("user_id")

        if user_id is None:
            return

        tweet_id = tweet_data_dict.get("tweet_id")
        tweet_media_type = tweet_data_dict.get("tweet_media_type")
        tweet_media_url = tweet_data_dict.get("tweet_media_url")

        # logger.info(f"========{tweet_id}========")
        # logger.info(tweet_data_dict)
        # logger.info("===================================")

        # 构建文件夹路径
        base_path = (
            user_path
            / format_file_name(kwargs.get("naming", "{create}_{desc}"), tweet_data_dict)
            if kwargs.get("folderize")
            else user_path
        )

        # # 检查微博是否可见
        # if tweet_data_dict.get("is_visible"):
        #     logger.error(_("微博 {0} 无查看权限").format(tweet_id))
        #     return

        # 检查推文是否有图片
        if tweet_media_type == "video":

            # 说明是视频推文
            # logger.info(
            #     _("推文视频时长：{0}s，码率列表：{1}").format(
            #         tweet_data_dict.get("tweet_video_duration") // 1000,
            #         tweet_data_dict.get("tweet_video_bitrate"),
            #     )
            # )
            # logger.info(tweet_data_dict.get("playback_list")[0])

            video_name = (
                format_file_name(
                    kwargs.get("naming", "{create}_{desc}"), tweet_data_dict
                )
                + "_video"
            )

            video_url = tweet_data_dict.get("tweet_video_url")
            if isinstance(video_url, list):
                video_url = video_url[-1]

            await self.initiate_download(
                _("视频"),
                video_url,
                base_path,
                video_name,
                ".mp4",
            )
        elif tweet_media_type == "photo":
            # 处理图片下载任务
            logger.info(
                _("推文图片列表：{0}").format(tweet_data_dict.get("tweet_media_url"))
            )
            if not tweet_data_dict.get("tweet_media_url"):
                logger.warning(
                    _("{0} : {1}该推文没有图片链接").format(
                        tweet_id, tweet_data_dict.get("tweet_desc")
                    )
                )
            else:
                if isinstance(tweet_media_url, str):
                    tweet_media_url = [tweet_data_dict.get("tweet_media_url")]
                for i, image_url in enumerate(tweet_media_url):
                    image_name = f"{format_file_name(kwargs.get('naming'), tweet_data_dict)}_image_{i + 1}"
                    if image_url != None:
                        await self.initiate_download(
                            _("图片"),
                            f"{image_url}?format=jpg&name=large",
                            base_path,
                            image_name,
                            ".jpg",
                        )
                    else:
                        logger.warning(
                            _("{0} 该推文没有图片链接，无法下载").format(tweet_id)
                        )

        # 处理文案下载任务
        if kwargs.get("desc"):
            desc_name = (
                format_file_name(
                    kwargs.get("naming", "{create}_{desc}"), tweet_data_dict
                )
                + "_desc"
            )
            desc_content = tweet_data_dict.get("tweet_desc")
            await self.initiate_static_download(
                _("文案"), desc_content, base_path, desc_name, ".txt"
            )

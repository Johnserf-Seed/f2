# path: f2/apps/weibo/dl.py

import sys
from datetime import datetime
from typing import Any, Union

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.dl.base_downloader import BaseDownloader
from f2.utils.utils import get_timestamp, timestamp_2_str
from f2.apps.weibo.db import AsyncUserDB
from f2.apps.weibo.utils import format_file_name
from f2.apps.weibo.api import WeiboAPIEndpoints


class WeiboDownloader(BaseDownloader):
    def __init__(self, kwargs: dict = ...) -> None:
        if kwargs["cookie"] is None:
            raise ValueError(
                _(
                    "cookie不能为空。请提供有效的 cookie 参数，或自动从浏览器获取 `--auto-cookie edge`"
                )
            )

        super().__init__(kwargs)

    async def create_download_tasks(
        self,
        kwargs: dict = ...,
        weibo_datas: Union[list, dict] = ...,
        user_path: Any = ...,
    ) -> None:
        """
        创建下载任务

        Args:
            kwargs (dict): 命令行参数
            weibo_datas (list, dict): 微博数据列表或字典
            user_path (str): 用户目录路径
        """

        if (
            not kwargs
            or not weibo_datas
            or not isinstance(weibo_datas, (list, dict))
            or not user_path
        ):
            return

        # 统一处理，将 weibo_datas 转为列表
        weibo_datas_list = (
            [weibo_datas] if isinstance(weibo_datas, dict) else weibo_datas
        )

        # 创建下载任务
        for weibo_data in weibo_datas_list:
            await self.handler_download(kwargs, weibo_data, user_path)

        # 执行下载任务
        await self.execute_tasks()

    async def handler_download(
        self, kwargs: dict, weibo_data_dict: dict, user_path: Any
    ) -> None:
        """
        处理下载任务

        Args:
            kwargs (dict): 命令行参数
            weibo_data_dict (dict): 作品数据字典
            user_path (Any): 用户目录路径
        """

        # 构建文件夹路径
        base_path = (
            user_path
            / format_file_name(kwargs.get("naming", "{create}_{desc}"), weibo_data_dict)
            if kwargs.get("folderize")
            else user_path
        )

        user_id = weibo_data_dict.get("user_id")
        weibo_id = weibo_data_dict.get("weibo_id")

        logger.debug(f"========{weibo_id}========")
        logger.debug(weibo_data_dict)
        logger.debug("===================================")

        # 检查微博是否可见
        if weibo_data_dict.get("is_visible"):
            logger.error(_("微博 {0} 无查看权限").format(weibo_id))
            return

        # 检查微博是否有图片
        if weibo_data_dict.get("pic_num") == 0:

            # 说明是视频微博
            # print(weibo_data_dict.get("playback_list"))
            logger.info(
                _("清晰度列表：{0}，码率列表：{1}").format(
                    weibo_data_dict.get("quality_list"),
                    weibo_data_dict.get("bitrate_list"),
                )
            )
            logger.info(weibo_data_dict.get("playback_list")[0])

            video_name = (
                format_file_name(
                    kwargs.get("naming", "{create}_{desc}"), weibo_data_dict
                )
                + "_video"
            )
            video_url = weibo_data_dict.get("playback_list")
            if video_url[0]:
                await self.initiate_download(
                    _("视频"),
                    video_url[0],
                    base_path,
                    video_name,
                    ".mp4",
                )
        else:
            # 处理图片下载任务
            # logger.info(
            #     _("图片ID列表：{0}，图片数量：{1}").format(
            #         weibo_data_dict.get("pic_infos"),
            #         weibo_data_dict.get("pic_num"),
            #     )
            # )
            for i, image_url in enumerate(weibo_data_dict.get("pic_infos")):
                image_name = f"{format_file_name(kwargs.get('naming'), weibo_data_dict)}_image_{i + 1}"
                image_url = WeiboAPIEndpoints.LARGEST + f"/{image_url}"
                if image_url != None:
                    await self.initiate_download(
                        _("图片"), image_url, base_path, image_name, ".jpg"
                    )
                else:
                    logger.warning(
                        _("{0} 该微博没有图片链接，无法下载").format(weibo_id)
                    )

        # 处理文案下载任务
        if kwargs.get("desc"):
            desc_name = (
                format_file_name(
                    kwargs.get("naming", "{create}_{desc}"), weibo_data_dict
                )
                + "_desc"
            )
            desc_content = weibo_data_dict.get("desc")
            await self.initiate_static_download(
                _("文案"), desc_content, base_path, desc_name, ".txt"
            )

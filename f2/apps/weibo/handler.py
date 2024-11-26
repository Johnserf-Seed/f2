# path: f2/apps/weibo/handler.py

import asyncio

from pathlib import Path
from rich.rule import Rule
from typing import AsyncGenerator, Union, Dict, Any, List

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.utils.decorators import mode_handler, mode_function_map
from f2.apps.weibo.db import AsyncUserDB
from f2.apps.weibo.crawler import WeiboCrawler
from f2.apps.weibo.dl import WeiboDownloader
from f2.apps.weibo.model import UserInfo, UserDetail, UserWeibo, WeiboDetail
from f2.apps.weibo.filter import (
    UserInfoFilter,
    UserDetailFilter,
    WeiboDetailFilter,
    UserWeiboFilter,
)
from f2.apps.weibo.utils import (
    WeiboIdFetcher,
    WeiboUidFetcher,
    create_or_rename_user_folder,
)
from f2.exceptions.api_exceptions import APIResponseError
from f2.cli.cli_console import RichConsoleManager

rich_console = RichConsoleManager().rich_console
rich_prompt = RichConsoleManager().rich_prompt


class WeiboHandler:

    # 需要忽略的字段
    user_ignore_fields = ["status"]

    def __init__(self, kwargs) -> None:
        self.kwargs = kwargs
        self.downloader = WeiboDownloader(kwargs)

    async def fetch_user_info(self, uid: str, custom: str = "") -> UserInfoFilter:
        """
        获取用户个人信息
        (Get user personal info)

        Args:
            uid (str): 用户ID (User ID)
            custom (str): 用户自定义id (Custom ID)

        Returns:
            UserInfoFilter: 用户信息过滤器 (User info filter)

        Note:
            uid和custom只需传入一个 (Only need to pass in one of uid and custom)
        """

        if not uid and not custom:
            raise ValueError(_("`uid`和`custom`至少需要传入一个"))

        async with WeiboCrawler(self.kwargs) as crawler:
            params = UserInfo(uid=uid, custom=custom)
            response = await crawler.fetch_user_info(params)
            user = UserInfoFilter(response)
            if user.nickname is None:
                raise APIResponseError(
                    _("`fetch_user_info`请求失败，请更换cookie或稍后再试")
                )

            logger.info(
                _("用户昵称: [yellow]{0}[/yellow]  微博数: {1}").format(
                    user.nickname, user.weibo_count
                )
            )
            return user

    async def fetch_user_detail(self, uid: str) -> UserDetailFilter:
        """
        获取用户详细信息
        (Get user detail info)

        Args:
            uid (str): 用户ID (User ID)

        Returns:
            UserDetailFilter: 用户详细信息 (User detail info)
        """

        if not uid:
            raise ValueError(_("`uid`不能为空"))

        async with WeiboCrawler(self.kwargs) as crawler:
            params = UserDetail(uid=uid)
            response = await crawler.fetch_user_detail(params)
            user = UserDetailFilter(response)
            if user.create_at is None:
                raise APIResponseError(
                    _("`fetch_user_detail`请求失败，请更换cookie或稍后再试")
                )
            return user

    async def get_or_add_user_data(
        self,
        kwargs: dict,
        user_id: str,
        db: AsyncUserDB,
    ) -> Path:
        """
        获取或创建用户数据同时创建用户目录
        (Get or create user data and create user directory)

        Args:
            kwargs (dict): 配置参数 (Conf parameters)
            user_id (str): 用户ID (User ID)
            db (AsyncUserDB): 用户数据库 (User database)

        Returns:
            user_path (Path): 用户目录路径 (User directory path)
        """

        # 尝试从数据库中获取用户数据
        local_user_data = await db.get_user_info(user_id)

        # 从服务器获取当前用户最新数据
        current_user_data = await self.fetch_user_info(user_id)

        # 获取当前用户最新昵称
        current_nickname = current_user_data.nickname

        # 设置用户目录
        user_path = create_or_rename_user_folder(
            kwargs, local_user_data, current_nickname
        )

        # 如果用户不在数据库中，将其添加到数据库
        if not local_user_data:
            await db.add_user_info(
                self.user_ignore_fields, **current_user_data._to_dict()
            )

        return user_path

    @mode_handler("one")
    async def handle_one_weibo(self):
        """
        用于处理单个微博。
        (Used to process a single weibo.)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        weibo_id = await WeiboIdFetcher.get_weibo_id(self.kwargs.get("url"))

        weibo = await self.fetch_one_weibo(weibo_id)

        # 检查是否有查看权限
        if weibo.error_code == 20112:
            logger.error(_("微博 {0} 无查看权限，请配置Cookie").format(weibo_id))
            await self.downloader.close()
            return
        else:
            logger.info(
                f"微博ID: {weibo.weibo_id}, 微博文案: {weibo.weibo_desc}, 发布时间: {weibo.weibo_created_at}"
            )

        async with AsyncUserDB("weibo_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, weibo.user_id, db)

        await self.downloader.create_download_tasks(
            self.kwargs, weibo._to_dict(), user_path
        )

    async def fetch_one_weibo(self, weibo_id: str) -> WeiboDetailFilter:
        """
        用于获取单个微博。

        Args:
            weibo_id: str: 微博ID

        Return:
            weibo_data: dict: 微博数据字典，包含微博ID、微博文案、作者昵称
        """

        if not weibo_id:
            raise ValueError(_("`weibo_id`不能为空"))

        logger.info(_("开始爬取微博: {0}").format(weibo_id))

        async with WeiboCrawler(self.kwargs) as crawler:
            params = WeiboDetail(id=weibo_id)
            response = await crawler.fetch_weibo_detail(params)
            weibo = WeiboDetailFilter(response)
            return weibo

    @mode_handler("post")
    async def handle_user_weibo(self):
        """
        用于处理用户微博。
        (Used to process user weibo.)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        user_id = await WeiboUidFetcher.get_weibo_uid(self.kwargs.get("url"))

        async with AsyncUserDB("weibo_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, user_id, db)

        # 获取用户微博数据
        async for weibo_data in self.fetch_user_weibo(user_id):
            await self.downloader.create_download_tasks(
                self.kwargs, weibo_data._to_list(), user_path
            )

    async def fetch_user_weibo(
        self,
        user_id: str,
        page: int = 1,
        feature: int = 0,
        since_id: str = "",
        max_counts: int = None,
    ) -> AsyncGenerator[UserWeiboFilter, Any]:
        """
        用于获取用户微博数据。

        Args:
            user_id: str: 用户ID

        Return:
            weibo_data: AsyncGenerator[UserWeiboFilter, Any]: 用户微博数据过滤器
        """

        max_counts = max_counts or float("inf")
        weibos_collected = 0

        logger.info(_("处理用户：{0} 发布的微博").format(user_id))

        while weibos_collected < max_counts:
            rich_console.print(Rule(_("处理第 {0} 页").format(page)))

            async with WeiboCrawler(self.kwargs) as crawler:
                params = UserWeibo(
                    uid=user_id,
                    page=page,
                    feature=feature,
                    since_id=since_id,
                )
                response = await crawler.fetch_user_weibo(params)
                weibo_data = UserWeiboFilter(response)
                yield weibo_data

            if weibo_data.since_id == "" or weibos_collected == weibo_data.weibo_total:
                logger.info(
                    _("已爬取完所有微博，共处理 {0} 个微博").format(weibos_collected)
                )
                break
            else:
                since_id = str(weibo_data.since_id)

            # 更新已经处理的微博数量
            weibos_collected += len(weibo_data.weibo_id)
            page += 1

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))


async def main(kwargs):
    mode = kwargs.get("mode")
    if mode in mode_function_map:
        await mode_function_map[mode](WeiboHandler(kwargs))
    else:
        logger.error(_("不存在该模式: {0}").format(mode))

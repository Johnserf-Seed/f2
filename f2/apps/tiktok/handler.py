# path: f2/apps/tiktok/handler.py

import sys

from pathlib import Path
from typing import AsyncGenerator, Union, List, Any

from f2.i18n.translator import _
from f2.log.logger import logger
from f2.utils.mode_handler import mode_handler, mode_function_map
from f2.apps.tiktok.db import AsyncUserDB, AsyncVideoDB
from f2.apps.tiktok.crawler import TiktokCrawler
from f2.apps.tiktok.dl import TiktokDownloader
from f2.apps.tiktok.model import (
    UserProfile,
    UserPost,
    UserLike,
    UserCollect,
    UserMix,
    UserPlayList,
    PostDetail,
)
from f2.apps.tiktok.filter import (
    UserProfileFilter,
    UserPostFilter,
    PostDetailFilter,
    UserMixFilter,
    UserPlayListFilter,
)
from f2.apps.tiktok.utils import (
    SecUserIdFetcher,
    AwemeIdFetcher,
    create_or_rename_user_folder,
)
from f2.cli.cli_console import RichConsoleManager

rich_console = RichConsoleManager().rich_console
rich_prompt = RichConsoleManager().rich_prompt


class TiktokHandler:

    # 需要忽略的字段（需过滤掉有时效性的字段）
    ignore_fields = ["video_play_addr", "images", "video_bit_rate", "cover"]

    def __init__(self, kwargs: dict = ...) -> None:
        self.kwargs = kwargs
        self.downloader = TiktokDownloader(kwargs)

    async def handler_user_profile(
        self,
        secUid: str = "",
        uniqueId: str = "",
    ) -> UserProfileFilter:
        """
        用于获取指定用户的个人信息
        (Used to get personal info of specified users)

        Args:
            secUid: str: 用户ID (User ID)
            uniqueId: str: 用户唯一ID (User unique ID)

        Return:
            user: UserProfileFilter: 用户信息过滤器 (User info filter)
        """

        if not secUid and not uniqueId:
            raise ValueError(_("至少提供 secUid 或 uniqueId 中的一个参数"))

        async with TiktokCrawler(self.kwargs) as crawler:
            params = UserProfile(secUid=secUid, uniqueId=uniqueId)
            response = await crawler.fetch_user_profile(params)
            return UserProfileFilter(response)

    async def get_user_nickname(
        self,
        secUid: str,
        db: AsyncUserDB,
    ) -> str:
        """
        用于获取指定用户的昵称
        (Used to get nickname of specified users)

        Args:
            secUid: str: 用户ID (User ID)
            db: AsyncUserDB: 用户数据库 (User database)

        Return:
            nick_name: str: 用户昵称 (User nickname)
        """

        user_dict = await db.get_user_info(secUid)
        if not user_dict:
            user_dict = await self.handler_user_profile(secUid)
            await db.add_user_info(**user_dict._to_dict())
        return user_dict.get("nickname", "")

    async def get_or_add_user_data(
        self,
        secUid: str,
        db: AsyncUserDB,
    ) -> Path:
        """
        获取或创建用户数据同时创建用户目录
        (Get or create user data and create user directory)

        Args:
            kwargs (dict): 配置参数 (Conf parameters)
            secUid (str): 用户ID (User ID)
            db (AsyncUserDB): 用户数据库 (User database)

        Returns:
            user_path (Path): 用户目录路径 (User directory path)
        """

        # 尝试从数据库中获取用户数据
        local_user_data = await db.get_user_info(secUid)

        # 从服务器获取当前用户最新数据
        current_user_data = await self.handler_user_profile(secUid)

        # 获取当前用户最新昵称
        current_nickname = current_user_data._to_dict().get("nickname")

        # 设置用户目录
        user_path = create_or_rename_user_folder(
            self.kwargs, local_user_data, current_nickname
        )

        # 如果用户不在数据库中，将其添加到数据库
        if not local_user_data:
            await db.add_user_info(**current_user_data._to_dict())

        return user_path

    @classmethod
    async def get_or_add_video_data(
        cls,
        aweme_data: dict,
        db: AsyncVideoDB,
        ignore_fields: list = None,
    ):
        """
        获取或创建作品数据同时创建用户目录
        (Get or create user data and create user directory)

        Args:
            aweme_data (dict): 作品数据 (User data)
            db (AsyncVideoDB): 作品数据库 (User database)
            ignore_fields (list): 剔除的字段
        """

        # 尝试从数据库中获取作品数据
        local_video_data = await db.get_video_info(aweme_data.get("aweme_id", None))

        # 如果作品不在数据库中，将其添加到数据库
        if not local_video_data:
            # 从服务器获取当前作品最新数据
            # current_video_data = await fetch_one_video(aweme_data.get("aweme_id"))
            await db.add_video_info(ignore_fields=ignore_fields, **aweme_data)

    async def fetch_play_list(
        self,
        secUid: str,
        cursor: int,
        page_counts: int,
    ) -> UserPlayListFilter:
        """
        用于获取指定用户的作品合集列表
        (Used to get video mix list of specified user)

        Args:
            secUid: str: 用户ID (User ID)
            cursor: int: 分页游标 (Page cursor)
            page_counts: int: 分页数量 (Page counts)

        Return:
            playlist: UserPlayListFilter: 作品合集列表 (Video mix list)
        """

        logger.debug(_("开始爬取用户：{0} 的作品合集列表").format(secUid))

        async with TiktokCrawler(self.kwargs) as crawler:
            params = UserPlayList(secUid=secUid, cursor=cursor, count=page_counts)
            response = await crawler.fetch_user_play_list(params)
            playlist = UserPlayListFilter(response)

        if not playlist.hasPlayList:
            logger.info(_("用户：{0} 没有作品合集").format(secUid))
            return {}

        logger.debug(_("当前请求的cursor：{0}").format(cursor))
        logger.debug(
            _("作品合集ID：{0} 作品合集标题：{1}").format(
                playlist.mixId, playlist.mixName
            )
        )
        logger.debug("===================================")
        return playlist

    async def select_playlist(
        self, playlists: Union[dict, UserPlayListFilter]
    ) -> Union[str, List[str]]:
        """
        用于选择要下载的作品合辑
        (Used to select the video mix to download)

        Args:
            playlists: Union[dict, UserPlayListFilter]: 作品合辑列表 (Video mix list)

        Return:
            selected_index: Union[str, List[str]]: 选择的作品合辑序号 (Selected video mix index)
        """

        if playlists == {}:
            sys.exit(_("用户没有作品合辑"))

        rich_console.print("[bold]请选择要下载的合辑：[/bold]")
        rich_console.print("0: [bold]全部下载[/bold]")

        for i in range(len(playlists.mixId)):
            rich_console.print(
                _("{0}: {1} (包含 {2} 个作品，收藏夹ID {3})").format(
                    i + 1,
                    playlists.mixName[i],
                    playlists.videoCount[i],
                    playlists.mixId[i],
                )
            )

        # rich_prompt 会有字符刷新问题，暂时使用rich_print
        rich_console.print(_("[bold yellow]请输入希望下载的合辑序号：[/bold yellow]"))
        selected_index = int(
            rich_prompt.ask(
                # _("[bold yellow]请输入希望下载的合辑序号:[/bold yellow]"),
                choices=[str(i) for i in range(len(playlists) + 1)],
            )
        )

        if selected_index == 0:
            return playlists.mixId
        else:
            return playlists.mixId[selected_index - 1]

    @mode_handler("one")
    async def handler_one_video(self):
        """
        用于获取指定作品的信息
        (Used to get video info of specified video)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        aweme_id = await AwemeIdFetcher.get_aweme_id(self.kwargs.get("url"))

        aweme_data = await self.fetch_one_video(aweme_id)

        async with AsyncUserDB("tiktok_users.db") as udb:
            user_path = await self.get_or_add_user_data(aweme_data.secUid, udb)

        async with AsyncVideoDB("tiktok_videos.db") as vdb:
            await self.get_or_add_video_data(
                aweme_data._to_dict(), vdb, self.ignore_fields
            )

        logger.debug(_("单个作品数据：{0}").format(aweme_data._to_dict()))

        # 创建下载任务
        await self.downloader.create_download_tasks(
            self.kwargs, aweme_data._to_dict(), user_path
        )

    async def fetch_one_video(
        self, itemId: str
    ) -> AsyncGenerator[PostDetailFilter, Any]:
        """
        用于获取指定作品的详细信息
        (Used to get detailed information of specified video)

        Args:
            itemId: str: 作品ID (Video ID)

        Return:
            video: AsyncGenerator[PostDetailFilter, Any]: 作品信息过滤器 (Video info filter)
        """

        logger.debug(_("开始爬取作品：{0}").format(itemId))
        async with TiktokCrawler(self.kwargs) as crawler:
            params = PostDetail(itemId=itemId)
            response = await crawler.fetch_post_detail(params)
            video = PostDetailFilter(response)

        logger.debug(
            _("作品ID：{0} 作品文案：{1} 作者：{2}").format(
                video.aweme_id, video.desc, video.nickname
            )
        )

        return video

    @mode_handler("post")
    async def handler_user_post(self):
        """
        用于获取指定用户的作品信息
        (Used to get video info of specified user)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        cursor = self.kwargs.get("cursor", 0)
        page_counts = self.kwargs.get("page_counts", 35)
        max_counts = self.kwargs.get("max_counts")

        secUid = await SecUserIdFetcher.get_secuid(self.kwargs.get("url"))

        async with AsyncUserDB("tiktok_users.db") as udb:
            user_path = await self.get_or_add_user_data(secUid, udb)

        async for aweme_data_list in self.fetch_user_post_videos(
            secUid, cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_user_post_videos(
        self, secUid: str, cursor: int, page_counts: int, max_counts: float
    ) -> AsyncGenerator[UserPostFilter, Any]:
        """
        用于获取指定用户发布的作品列表
        (Used to get video list of specified user)

        Args:
            secUid: str: 用户ID (User ID)
            cursor: int: 分页游标 (Page cursor)
            page_counts: int: 分页数量 (Page counts)
            max_counts: float: 最大数量 (Max counts)

        Return:
            video: AsyncGenerator[UserPostFilter, Any]: 用户发布作品信息过滤器 (Video info filter)
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.debug(_("开始爬取用户：{0} 发布的作品").format(secUid))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(cursor))

            async with TiktokCrawler(self.kwargs) as crawler:
                params = UserPost(secUid=secUid, cursor=cursor, count=page_counts)
                response = await crawler.fetch_user_post(params)
                video = UserPostFilter(response)

            if not video.has_aweme:
                logger.debug(_("{0} 页没有找到作品").format(cursor))
                if not video.hasMore and str(video.api_status_code) == "0":
                    logger.debug(_("用户：{0} 所有作品采集完毕").format(secUid))
                    break
                else:
                    cursor = video.cursor
                    continue

            logger.debug(_("当前请求的cursor：{0}").format(cursor))
            logger.debug(
                _("作品ID：{0} 作品文案：{1} 作者：{2}").format(
                    video.aweme_id, video.desc, video.nickname
                )
            )
            logger.debug("===================================")

            yield video

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(video.aweme_id)
            cursor = video.cursor

        logger.debug(_("爬取结束，共爬取 {0} 个作品").format(videos_collected))

    @mode_handler("like")
    async def handler_user_like(self):
        """
        用于获取指定用户的点赞作品信息
        (Used to get liked video info of specified user)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        cursor = self.kwargs.get("cursor", 0)
        page_counts = self.kwargs.get("page_counts", 30)
        max_counts = self.kwargs.get("max_counts")

        secUid = await SecUserIdFetcher.get_secuid(self.kwargs.get("url"))

        async with AsyncUserDB("tiktok_users.db") as udb:
            user_path = await self.get_or_add_user_data(secUid, udb)

        async for aweme_data_list in self.fetch_user_like_videos(
            secUid, cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_user_like_videos(
        self, secUid: str, cursor: int, page_counts: int, max_counts: float
    ) -> AsyncGenerator[UserPostFilter, Any]:
        """
        用于获取指定用户点赞的作品列表
        (Used to get liked video list of specified user)

        Args:
            secUid: str: 用户ID (User ID)
            cursor: int: 分页游标 (Page cursor)
            page_counts: int: 分页数量 (Page counts)
            max_counts: float: 最大数量 (Max counts)

        Return:
            like: AsyncGenerator[UserPostFilter, Any]: 用户点赞作品信息过滤器 (Video info filter)
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.debug(_("开始爬取用户：{0} 点赞的作品").format(secUid))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(cursor))

            async with TiktokCrawler(self.kwargs) as crawler:
                params = UserLike(secUid=secUid, cursor=cursor, count=page_counts)
                response = await crawler.fetch_user_like(params)
                like = UserPostFilter(response)

            if like.has_aweme:
                logger.debug(_("当前请求的cursor：{0}").format(cursor))
                logger.debug(
                    _("作品ID：{0} 作品文案：{1} 作者：{2}").format(
                        like.aweme_id, like.desc, like.nickname
                    )
                )
                logger.debug("===================================")

                yield like

                # 更新已经处理的作品数量 (Update the number of videos processed)
                videos_collected += len(like.aweme_id)

                if not like.hasMore and str(like.api_status_code) == "0":
                    logger.debug(_("用户：{0} 所有作品采集完毕").format(secUid))
                    break

            else:
                logger.debug(_("{0} 页没有找到作品").format(cursor))

                if not like.hasMore and str(like.api_status_code) == "0":
                    logger.debug(_("用户：{0} 所有作品采集完毕").format(secUid))
                    break

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(like.aweme_id)
            cursor = like.cursor

        logger.debug(_("爬取结束，共爬取 {0} 个作品").format(videos_collected))

    @mode_handler("collect")
    async def handler_user_collect(self):
        """
        用于获取指定用户的收藏作品信息
        (Used to get collected video info of specified user)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        cursor = self.kwargs.get("cursor", 0)
        page_counts = self.kwargs.get("page_counts", 30)
        max_counts = self.kwargs.get("max_counts")

        secUid = await SecUserIdFetcher.get_secuid(self.kwargs.get("url"))

        async with AsyncUserDB("tiktok_users.db") as udb:
            user_path = await self.get_or_add_user_data(secUid, udb)

        async for aweme_data_list in self.fetch_user_collect_videos(
            secUid, cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_user_collect_videos(
        self, secUid: str, cursor: int, page_counts: int, max_counts: float
    ) -> AsyncGenerator[UserPostFilter, Any]:
        """
        用于获取指定用户收藏的作品列表
        (Used to get collected video list of specified user)

        Args:
            secUid: str: 用户ID (User ID)
            cursor: int: 分页游标 (Page cursor)
            page_counts: int: 分页数量 (Page counts)
            max_counts: float: 最大数量 (Max counts)

        Return:
            collect: AsyncGenerator[UserPostFilter, Any]: 收藏作品信息过滤器 (Video info filter)
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.debug(_("开始爬取用户：{0} 收藏的作品").format(secUid))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(cursor))

            async with TiktokCrawler(self.kwargs) as crawler:
                params = UserCollect(secUid=secUid, cursor=cursor, count=page_counts)
                response = await crawler.fetch_user_collect(params)
                collect = UserPostFilter(response)

            if collect.has_aweme:
                logger.debug(_("当前请求的cursor：{0}").format(cursor))
                logger.debug(
                    _("作品ID：{0} 作品文案：{1} 作者：{2}").format(
                        collect.aweme_id, collect.desc, collect.nickname
                    )
                )
                logger.debug("===================================")

                yield collect

                # 更新已经处理的作品数量 (Update the number of videos processed)
                videos_collected += len(collect.aweme_id)

                if not collect.hasMore and str(collect.api_status_code) == "0":
                    logger.debug(_("用户：{0} 所有作品采集完毕").format(secUid))
                    break

            else:
                logger.debug(_("{0} 页没有找到作品").format(cursor))

                if not collect.hasMore and str(collect.api_status_code) == "0":
                    logger.debug(_("用户：{0} 所有作品采集完毕").format(secUid))
                    break

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(collect.aweme_id)
            cursor = collect.cursor

        logger.debug(_("爬取结束，共爬取 {0} 个作品").format(videos_collected))

    @mode_handler("mix")
    async def handler_user_mix(self):
        """
        用于获取指定用户的合集作品信息
        (Used to get mix video info of specified user)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        cursor = self.kwargs.get("cursor", 0)
        page_counts = self.kwargs.get("page_counts", 30)
        max_counts = self.kwargs.get("max_counts")

        secUid = await SecUserIdFetcher.get_secuid(self.kwargs.get("url"))
        playlist = await self.fetch_play_list(secUid, cursor, page_counts)
        mixId = await self.select_playlist(playlist)

        async with AsyncUserDB("tiktok_users.db") as audb:
            user_path = await self.get_or_add_user_data(secUid, audb)

        if isinstance(mixId, str):
            mixId = [mixId]

        for mixId in playlist.get("mixId", []):
            async for aweme_data_list in self.fetch_user_mix_videos(
                mixId, cursor, page_counts, max_counts
            ):
                # 创建下载任务
                await self.downloader.create_download_tasks(
                    self.kwargs, aweme_data_list._to_list(), user_path
                )

    async def fetch_user_mix_videos(
        self, mixId: str, cursor: int, page_counts: int, max_counts: float
    ) -> AsyncGenerator[UserMixFilter, Any]:
        """
        用于获取指定用户合集的作品列表
        (Used to get mix video list of specified user)

        Args:
            mixId: str: 合集ID (Mix ID)
            cursor: int: 分页游标 (Page cursor)
            page_counts: int: 分页数量 (Page counts)
            max_counts: float: 最大数量 (Max counts)

        Return:
            mix: AsyncGenerator[UserMixFilter, Any]: 合集作品信息过滤器 (Video info filter)
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.debug(_("开始爬取用户: {0} 合集的作品").format(mixId))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(cursor))

            async with TiktokCrawler(self.kwargs) as crawler:
                params = UserMix(mixId=mixId, cursor=cursor, count=page_counts)
                response = await crawler.fetch_user_mix(params)
                mix = UserMixFilter(response)

            if mix.has_aweme:
                logger.debug(_("当前请求的cursor: {0}").format(cursor))
                logger.debug(
                    _("作品ID: {0} 作品文案: {1} 作者: {2}").format(
                        mix.aweme_id, mix.desc, mix.nickname
                    )
                )
                logger.debug("===================================")

                yield mix

                # 更新已经处理的作品数量 (Update the number of videos processed)
                videos_collected += len(mix.aweme_id)

                if not mix.hasMore and str(mix.api_status_code) == "0":
                    logger.debug(_("合辑: {0} 所有作品采集完毕").format(mixId))
                    break

            else:
                logger.debug(_("{0} 页没有找到作品").format(cursor))

                if not mix.hasMore and str(mix.api_status_code) == "0":
                    logger.debug(_("合辑: {0} 所有作品采集完毕").format(mixId))
                    break

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(mix.aweme_id)
            cursor = mix.cursor

        logger.debug(_("爬取结束，共爬取 {0} 个作品").format(videos_collected))


async def main(kwargs):
    mode = kwargs.get("mode")
    if mode in mode_function_map:
        await mode_function_map[mode](TiktokHandler(kwargs))
    else:
        logger.error(_("不存在该模式: {0}").format(mode))
        rich_console.print(_("不存在该模式: {0}").format(mode))

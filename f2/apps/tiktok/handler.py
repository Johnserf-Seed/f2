# path: f2/apps/tiktok/handler.py

import asyncio

from rich.rule import Rule
from pathlib import Path
from urllib.parse import quote
from typing import AsyncGenerator, Union, List, Any, Dict

from f2.i18n.translator import _
from f2.log.logger import logger
from f2.utils.decorators import mode_handler, mode_function_map
from f2.apps.bark.handler import BarkHandler
from f2.apps.bark.utils import ClientConfManager as BarkClientConfManager
from f2.apps.tiktok.db import AsyncUserDB, AsyncVideoDB
from f2.apps.tiktok.crawler import TiktokCrawler, TiktokWebSocketCrawler
from f2.apps.tiktok.dl import TiktokDownloader
from f2.apps.tiktok.model import (
    UserProfile,
    UserPost,
    UserLike,
    UserCollect,
    UserMix,
    UserPlayList,
    PostDetail,
    PostSearch,
    UserLive,
    CheckLiveAlive,
    LiveImFetch,
    LiveWebcast,
)
from f2.apps.tiktok.filter import (
    UserProfileFilter,
    UserPostFilter,
    PostDetailFilter,
    UserMixFilter,
    UserPlayListFilter,
    PostSearchFilter,
    UserLiveFilter,
    CheckLiveAliveFilter,
)
from f2.apps.tiktok.utils import (
    SecUserIdFetcher,
    AwemeIdFetcher,
    create_or_rename_user_folder,
)
from f2.cli.cli_console import RichConsoleManager
from f2.exceptions.api_exceptions import APIResponseError
from f2.utils.utils import interval_2_timestamp, timestamp_2_str, get_timestamp

rich_console = RichConsoleManager().rich_console
rich_prompt = RichConsoleManager().rich_prompt


TK_LIVE_STATUS_MAPPING = {
    # 1: _("准备中"),
    2: _("直播中"),
    # 3: _("直播中"),
    4: _("已关播"),
}


class TiktokHandler:

    # 需要忽略的字段（需过滤掉有时效性的字段）
    ignore_fields = [
        "video_play_addr",
        "images",
        "video_bit_rate",
        "cover",
    ]

    def __init__(self, kwargs: dict = ...) -> None:
        self.kwargs = kwargs
        self.downloader = TiktokDownloader(kwargs)
        # 初始化 Bark 通知服务
        self.bark_kwargs = BarkClientConfManager.merge()
        self.enable_bark = BarkClientConfManager.enable_bark()
        self.bark_notification = BarkHandler(self.bark_kwargs)

    async def _send_bark_notification(
        self,
        title: str,
        body: str,
        send_method: str = "post",
        **kwargs,
    ) -> None:
        """
        发送Bark通知的辅助方法。负责自定义通知内容。

        Args:
            title (str): 通知标题
            body (str): 通知内容
            send_method (str): 调用的发送方法（"fetch" 或 "post"）
            kwargs (Dict): 其他通知参数
        Returns:
            None
        """

        if self.enable_bark:
            await self.bark_notification.send_quick_notification(
                title,
                body,
                send_method=send_method,
                **kwargs,
            )

    async def fetch_user_profile(
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
            user = UserProfileFilter(response)
            if user.uniqueId is None:
                raise APIResponseError(
                    _("`fetch_user_profile`请求失败，请更换cookie或稍后再试")
                )
            return UserProfileFilter(response)

    async def get_or_add_user_data(
        self,
        secUid: str,
        uniqueId: str,
        db: AsyncUserDB,
    ) -> Path:
        """
        获取或创建用户数据同时创建用户目录
        (Get or create user data and create user directory)

        Args:
            kwargs (dict): 配置参数 (Conf parameters)
            secUid (str): 用户ID (User ID)
            uniqueId (str): 用户名 (Username)
            db (AsyncUserDB): 用户数据库 (User database)

        Returns:
            user_path (Path): 用户目录路径 (User directory path)
        """

        # 尝试从数据库中获取用户数据
        local_user_data = await db.get_user_info(secUid=secUid, uniqueId=uniqueId)

        # 从服务器获取当前用户最新数据
        current_user_data = await self.fetch_user_profile(
            secUid=secUid, uniqueId=uniqueId
        )

        # 获取当前用户最新昵称
        current_uniqueId = current_user_data.uniqueId

        # 设置用户目录
        user_path = create_or_rename_user_folder(
            self.kwargs, local_user_data, current_uniqueId
        )

        # 如果用户不在数据库中，将其添加到数据库
        if not local_user_data:
            await db.add_user_info(**current_user_data._to_dict())
            logger.debug(_("用户：{0} 已添加到数据库").format(current_uniqueId))

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

    @mode_handler("one")
    async def handle_one_video(self):
        """
        用于获取指定作品的信息
        (Used to get video info of specified video)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        aweme_id = await AwemeIdFetcher.get_aweme_id(self.kwargs.get("url"))

        aweme_data = await self.fetch_one_video(aweme_id)

        async with AsyncUserDB("tiktok_users.db") as udb:
            user_path = await self.get_or_add_user_data(
                secUid="", uniqueId=aweme_data.uniqueId, db=udb
            )

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
        self,
        itemId: str,
    ) -> PostDetailFilter:
        """
        用于获取指定作品的详细信息
        (Used to get detailed information of specified video)

        Args:
            itemId: str: 作品ID (Video ID)

        Return:
            video: PostDetailFilter: 作品信息过滤器 (Video info filter)
        """

        logger.debug(_("处理作品：{0}").format(itemId))
        async with TiktokCrawler(self.kwargs) as crawler:
            params = PostDetail(itemId=itemId)
            response = await crawler.fetch_post_detail(params)
            video = PostDetailFilter(response)

        logger.debug(
            _("作品ID：{0} 作品文案：{1} 作者：{2}").format(
                video.aweme_id, video.desc, video.nickname
            )
        )

        await self._send_bark_notification(
            _("[TikTok] 单个作品下载"),
            _("作品ID：{0}\n" "文案：{1}\n" "作者：{2}\n" "下载时间：{3}").format(
                video.aweme_id,
                (
                    video.desc_raw[:20] + "..."
                    if len(video.desc_raw) > 20
                    else video.desc_raw
                ),
                video.nickname_raw,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="TikTok",
        )

        return video

    @mode_handler("post")
    async def handle_user_post(self):
        """
        用于获取指定用户的作品信息
        (Used to get video info of specified user)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        cursor = self.kwargs.get("cursor", 0)
        min_cursor = 0
        page_counts = self.kwargs.get("page_counts", 35)
        max_counts = self.kwargs.get("max_counts")
        interval = self.kwargs.get("interval")

        secUid = await SecUserIdFetcher.get_secuid(self.kwargs.get("url"))

        # 判断是否提供了interval参数，如果有则获取start_date转时间戳提供给max_cursor
        if interval is not None and interval != "all":
            # 倒序查找
            min_cursor = interval_2_timestamp(interval, date_type="start")
            cursor = interval_2_timestamp(interval, date_type="end")

        async with AsyncUserDB("tiktok_users.db") as udb:
            user_path = await self.get_or_add_user_data(
                secUid=secUid, uniqueId="", db=udb
            )

        async for aweme_data_list in self.fetch_user_post_videos(
            secUid, cursor, min_cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_user_post_videos(
        self,
        secUid: str,
        cursor: int,
        min_cursor: int,
        page_counts: int,
        max_counts: float,
    ) -> AsyncGenerator[UserPostFilter, Any]:
        """
        用于获取指定用户发布的作品列表
        (Used to get video list of specified user)

        Args:
            secUid: str: 用户ID (User ID)
            cursor: int: 分页游标 (Page cursor)
            min_cursor: int: 最小游标 (Min cursor)
            page_counts: int: 分页数量 (Page counts)
            max_counts: float: 最大数量 (Max counts)

        Return:
            video: AsyncGenerator[UserPostFilter, Any]: 用户发布作品信息过滤器 (Video info filter)
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.info(_("处理用户：{0} 发布的作品").format(secUid))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(_("处理第 {0} 页 ({1})").format(cursor, timestamp_2_str(cursor)))
            )

            async with TiktokCrawler(self.kwargs) as crawler:
                params = UserPost(
                    secUid=secUid,
                    cursor=cursor,
                    count=page_counts,
                )
                response = await crawler.fetch_user_post(params)
                video = UserPostFilter(response)

            if not video.has_aweme:
                logger.info(_("第 {0} 页没有找到作品").format(cursor))
                if not video.hasMore and str(video.api_status_code) == "0":
                    logger.info(_("用户：{0} 所有作品采集完毕").format(secUid))
                    break
                else:
                    cursor = video.cursor
                    continue

            # 防止最后一页不包含任何作品导致无法获取nickname_raw
            nickname_raw = video.nickname_raw[0]

            logger.debug(_("当前请求的cursor：{0}").format(cursor))
            logger.debug(
                _("作品ID：{0} 作品文案：{1} 作者：{2}").format(
                    video.aweme_id, video.desc, video.nickname
                )
            )

            yield video

            if cursor < min_cursor:
                logger.info(_("已经处理到指定时间范围内的作品"))
                break

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(video.aweme_id)
            cursor = video.cursor

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理用户发布的作品，共处理 {0} 个作品").format(videos_collected)
        )

        await self._send_bark_notification(
            _("[TikTok] 主页作品下载"),
            _("用户：{0}\n" "作品数量：{1}\n" "下载时间：{2}").format(
                nickname_raw,
                videos_collected,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="TikTok",
        )

    @mode_handler("like")
    async def handle_user_like(self):
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
            user_path = await self.get_or_add_user_data(
                secUid=secUid, uniqueId="", db=udb
            )

        async for aweme_data_list in self.fetch_user_like_videos(
            secUid, cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_user_like_videos(
        self,
        secUid: str,
        cursor: int,
        page_counts: int,
        max_counts: float,
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

        logger.info(_("处理用户：{0} 点赞的作品").format(secUid))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(_("处理第 {0} 页 ({1})").format(cursor, timestamp_2_str(cursor)))
            )

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

                yield like

                # 更新已经处理的作品数量 (Update the number of videos processed)
                videos_collected += len(like.aweme_id)

                if not like.hasMore and str(like.api_status_code) == "0":
                    logger.debug(_("用户：{0} 所有作品采集完毕").format(secUid))
                    break

            else:
                logger.debug(_("第 {0} 页没有找到作品").format(cursor))

                if not like.hasMore and str(like.api_status_code) == "0":
                    logger.debug(_("用户：{0} 所有作品采集完毕").format(secUid))
                    break

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(like.aweme_id)
            cursor = like.cursor

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理用户点赞的作品，共处理 {0} 个作品").format(videos_collected)
        )

        # 点赞接口中没有当前用户的相关信息，因此无法获取nickname_raw
        user = await self.fetch_user_profile(secUid=secUid)
        await self._send_bark_notification(
            _("[TikTok] 点赞作品下载"),
            _("用户：{0}\n" "作品数：{1}\n" "下载时间：{2}").format(
                user.nickname_raw,
                videos_collected,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="TikTok",
        )

    @mode_handler("collect")
    async def handle_user_collect(self):
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
            user_path = await self.get_or_add_user_data(
                secUid=secUid, uniqueId="", db=udb
            )

        async for aweme_data_list in self.fetch_user_collect_videos(
            secUid, cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_user_collect_videos(
        self,
        secUid: str,
        cursor: int,
        page_counts: int,
        max_counts: float,
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

        logger.info(_("处理用户：{0} 收藏的作品").format(secUid))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(_("处理第 {0} 页 ({1})").format(cursor, timestamp_2_str(cursor)))
            )

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
                logger.debug(_("第 {0} 页没有找到作品").format(cursor))

                if not collect.hasMore and str(collect.api_status_code) == "0":
                    logger.debug(_("用户：{0} 所有作品采集完毕").format(secUid))
                    break

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(collect.aweme_id)
            cursor = collect.cursor

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理用户收藏作品，共处理 {0} 个作品").format(videos_collected)
        )

        await self._send_bark_notification(
            _("[TikTok] 收藏作品下载"),
            _("作品数：{0}\n" "下载时间：{1}").format(
                videos_collected,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="TikTok",
        )

    @mode_handler("mix")
    async def handle_user_mix(self):
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
            user_path = await self.get_or_add_user_data(
                secUid=secUid, uniqueId="", db=audb
            )

        if isinstance(mixId, str):
            mixId = [mixId]

        for mixId in playlist.mixId:
            async for aweme_data_list in self.fetch_user_mix_videos(
                mixId, cursor, page_counts, max_counts
            ):
                # 创建下载任务
                await self.downloader.create_download_tasks(
                    self.kwargs, aweme_data_list._to_list(), user_path
                )

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

        logger.debug(_("处理用户：{0} 的作品合集列表").format(secUid))

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
        return playlist

    async def select_playlist(
        self,
        playlists: Union[dict, UserPlayListFilter],
    ) -> Union[str, List[str]]:
        """
        用于选择要下载的作品合集
        (Used to select the video mix to download)

        Args:
            playlists: Union[dict, UserPlayListFilter]: 作品合集列表 (Video mix list)

        Return:
            selected_index: Union[str, List[str]]: 选择的作品合集序号 (Selected video mix index)
        """

        if playlists == {}:
            logger.warning(_("用户没有作品合集"))
            return

        rich_console.print("[bold]请选择要下载的合集：[/bold]")
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
        playlist = [str(i) for i in range(len(playlists.mixId) + 1)]
        rich_console.print(
            _(
                "[bold yellow]请输入希望下载的合集序号：[/bold yellow] [bold purple]{0}[/bold purple]"
            ).format("/".join(playlist))
        )
        selected_index = int(
            rich_prompt.ask(
                # _("[bold yellow]请输入希望下载的合集序号:[/bold yellow]"),
                console=rich_console,
                choices=playlist,
            )
        )

        if selected_index == 0:
            return playlists.mixId
        else:
            return playlists.mixId[selected_index - 1]

    async def fetch_user_mix_videos(
        self,
        mixId: str,
        cursor: int,
        page_counts: int,
        max_counts: float,
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

        logger.info(_("处理合集: {0} 的作品").format(mixId))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(_("处理第 {0} 页 ({1})").format(cursor, timestamp_2_str(cursor)))
            )

            async with TiktokCrawler(self.kwargs) as crawler:
                params = UserMix(mixId=str(mixId), cursor=cursor, count=page_counts)
                response = await crawler.fetch_user_mix(params)
                mix = UserMixFilter(response)

            if mix.has_aweme:
                logger.debug(_("当前请求的cursor: {0}").format(cursor))
                logger.debug(
                    _("作品ID: {0} 作品文案: {1} 作者: {2}").format(
                        mix.aweme_id, mix.desc, mix.nickname
                    )
                )

                yield mix

                # 更新已经处理的作品数量 (Update the number of videos processed)
                videos_collected += len(mix.aweme_id)

                if not mix.hasMore and str(mix.api_status_code) == "0":
                    logger.debug(_("合集: {0} 所有作品采集完毕").format(mixId))
                    break

            else:
                logger.debug(_("第 {0} 页没有找到作品").format(cursor))

                if not mix.hasMore and str(mix.api_status_code) == "0":
                    logger.debug(_("合集: {0} 所有作品采集完毕").format(mixId))
                    break

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(mix.aweme_id)
            cursor = mix.cursor

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理用户合集作品，共处理 {0} 个作品").format(videos_collected)
        )

        await self._send_bark_notification(
            _("[TikTok] 播放列表作品下载"),
            _("合集：{0}\n" "作品数：{1}\n" "下载时间：{2}").format(
                mixId,
                videos_collected,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="TikTok",
        )

    @mode_handler("search")
    async def handle_search(self):
        """
        用于搜索指定关键词的作品信息
        (Used to search video info of specified keyword)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        cursor = self.kwargs.get("cursor", 0)
        page_counts = self.kwargs.get("page_counts", 30)
        max_counts = self.kwargs.get("max_counts")
        keyword = self.kwargs.get("keyword")

        secUid = await SecUserIdFetcher.get_secuid(self.kwargs.get("url"))

        async with AsyncUserDB("tiktok_users.db") as udb:
            user_path = await self.get_or_add_user_data(
                secUid=secUid, uniqueId="", db=udb
            )

        async for aweme_data_list in self.fetch_search_videos(
            keyword, cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_search_videos(
        self,
        keyword: str,
        offset: int,
        page_counts: int,
        max_counts: float,
    ) -> AsyncGenerator[PostSearchFilter, Any]:
        """
        用于搜索指定关键词的作品列表
        (Used to search video list of specified keyword)

        Args:
            keyword: str: 搜索关键词 (Search keyword)
            offset: int: 分页游标 (Page offset)
            page_counts: int: 分页数量 (Page counts)
            max_counts: float: 最大数量 (Max counts)

        Return:
            search: AsyncGenerator[PostSearchFilter, Any]: 搜索作品信息过滤器 (Search video info filter)
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0
        search_id = ""

        logger.info(
            _("搜索关键词：{0} 的作品，最大作品数量 {1} ").format(keyword, max_counts)
        )

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.info(
                _("搜索第 {0} 个作品，每次请求数量：{1}").format(
                    offset + 1, current_request_size
                )
            )

            async with TiktokCrawler(self.kwargs) as crawler:
                params = PostSearch(
                    keyword=quote(keyword, safe=""),
                    offset=offset,
                    count=page_counts,
                    search_id=search_id,
                )
                response = await crawler.fetch_post_search(params)
                search = PostSearchFilter(response)

            if not search.has_aweme:
                logger.info(_("第 {0} 个offset没有找到作品").format(offset))
                if not search.has_more and str(search.api_status_code) == "0":
                    logger.info(_("关键词：{0} 所有作品采集完毕").format(keyword))
                    break
                else:
                    offset = search.cursor
                    continue

            logger.debug(_("当前请求的offset：{0}").format(offset))
            logger.debug(
                _("作品ID：{0} 作品文案：{1} 作者：{2}").format(
                    search.aweme_id, search.desc, search.nickname
                )
            )

            if videos_collected >= max_counts:
                logger.info(
                    _("关键词：{0} 已达到最大下载数量 {1} 个").format(
                        keyword, max_counts
                    )
                )
                break

            yield search

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(search.aweme_id)
            offset = search.cursor
            search_id = search.search_id

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(_("结束搜索，共搜索到 {0} 个作品").format(videos_collected))

        await self._send_bark_notification(
            _("[TikTok] 搜索作品下载"),
            _("关键词：{0}\n" "作品数：{1}\n" "下载时间：{2}").format(
                keyword,
                videos_collected,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="TikTok",
        )

    @mode_handler("live")
    async def handle_user_live(self):
        """
        用于获取指定用户的直播信息
        (Used to get live info of specified user)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        uniqueId = await SecUserIdFetcher.get_uniqueid(self.kwargs.get("url"))

        webcast_data = await self.fetch_user_live_videos(uniqueId)

        # 判断是否有直播间
        if not webcast_data.has_live:
            logger.info(_("用户：{0} 未直播").format(uniqueId))
            return

        # 是否正在直播
        if webcast_data.live_status != 2:
            logger.info(_("直播: {0} 已结束").format(webcast_data.live_title_raw))
            return

        async with AsyncUserDB("tiktok_users.db") as udb:
            user_path = await self.get_or_add_user_data(
                secUid="", uniqueId=uniqueId, db=udb
            )

        # 创建下载任务
        await self.downloader.create_stream_tasks(
            self.kwargs, webcast_data._to_dict(), user_path
        )

    async def fetch_user_live_videos(
        self,
        uniqueId: str,
    ) -> UserLiveFilter:
        """
        用于获取指定用户直播的作品列表
        (Used to get live video list of specified user)

        Args:
            secUid: str: 用户ID (User ID)
            cursor: int: 分页游标 (Page cursor)
            page_counts: int: 分页数量 (Page counts)
            max_counts: float: 最大数量 (Max counts)

        Return:
            live: [UserLiveFilter: 直播作品信息过滤器 (Live video info filter)
        """

        logger.debug(_("处理用户：{0} 的直播").format(uniqueId))

        async with TiktokCrawler(self.kwargs) as crawler:
            params = UserLive(uniqueId=uniqueId)
            response = await crawler.fetch_user_live(params)
            live = UserLiveFilter(response)

        logger.debug(
            _("房间ID：{0}，直播间：{1}，状态：{2}，观看人数：{3}").format(
                live.live_room_id,
                live.live_title_raw,
                live.live_status,
                live.live_user_count or 0,
            )
        )
        logger.debug(_("结束直播信息处理"))

        await self._send_bark_notification(
            _("[TikTok] 直播下载"),
            _(
                "房间ID：{0}\n"
                "直播间：{1}\n"
                "状态：{2}\n"
                "观看人数：{3}\n"
                "下载时间：{4}"
            ).format(
                live.live_room_id,
                (
                    live.live_title_raw[:20] + "..."
                    if len(live.live_title_raw) > 20
                    else live.live_title_raw
                ),
                TK_LIVE_STATUS_MAPPING.get(live.live_status, _("未知状态")),
                live.live_user_count or 0,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="TikTok",
        )

        return live

    async def fetch_check_live_alive(self, room_ids: str) -> CheckLiveAliveFilter:
        """
        用于检查直播间是否在线
        (Used to check if the live room is online)

        Args:
            room_ids: str: 直播间ID (Live room ID)

        Return:
            check: CheckLiveAliveFilter: 检查直播间在线状态过滤器 (Check live status filter)

        Note:
            房间号参数为字符串形式，多个房间号用逗号分隔，如：7381444193462078214,7381457815116466949,
        """

        logger.info(_("检查直播间在线状态"))
        async with TiktokCrawler(self.kwargs) as crawler:
            response = await crawler.fetch_check_live_alive(
                CheckLiveAlive(room_ids=room_ids)
            )
            check = CheckLiveAliveFilter(response)

        logger.info(
            _("直播间：{0}，在线状态：{1}").format(check.room_id, check.is_alive)
        )
        logger.info(_("结束直播间在线状态检查"))
        return check

    async def fetch_live_im(self, room_id: str):
        """
        用于获取直播间信息。

        Args:
            room_id: str: 直播间ID

        Return:
            live_im: LiveImFetchFilter: 直播间信息数据过滤器，包含直播间信息的_to_raw、_to_dict、_to_list方法
        """

        logger.info(_("查询直播间信息"))

        async with TiktokCrawler(self.kwargs) as crawler:
            params = LiveImFetch(room_id=room_id)
            live_im = await crawler.fetch_live_im_fetch(params)

        if live_im:
            logger.debug(
                _("直播间room_id：{0} 弹幕cursor：{1}").format(room_id, live_im)
            )
            logger.info(_("结束直播间信息查询"))
        else:
            logger.warning(_("请提供正确的room_id"))

        return live_im

    async def fetch_live_danmaku(
        self,
        room_id: str,
        internal_ext: str,
        cursor: str,
        wrss: str,
        wss_callbacks: Dict = {},
    ):
        """
        通过WebSocket连接获取直播间弹幕，再通过回调函数处理弹幕数据。

        Args:
            room_id: str: 直播间ID
            user_unique_id: str: 用户ID
            internal_ext: str: 内部扩展参数
            cursor: str: 弹幕cursor

        Return:
            self.websocket: TiktokWebSocketCrawler: WebSocket连接对象
        """

        if not wss_callbacks:
            logger.warning(_("没有设置回调函数，默认使用所有回调函数"))
            wss_callbacks = {
                "WebcastChatMessage": TiktokWebSocketCrawler.WebcastChatMessage,
                "WebcastMemberMessage": TiktokWebSocketCrawler.WebcastMemberMessage,
                "WebcastRoomUserSeqMessage": TiktokWebSocketCrawler.WebcastRoomUserSeqMessage,
                "WebcastGiftMessage": TiktokWebSocketCrawler.WebcastGiftMessage,
                "WebcastSocialMessage": TiktokWebSocketCrawler.WebcastSocialMessage,
                "WebcastLikeMessage": TiktokWebSocketCrawler.WebcastLikeMessage,
                "WebcastLinkMicFanTicketMethod": TiktokWebSocketCrawler.WebcastLinkMicFanTicketMethod,
                "WebcastLinkMicMethod": TiktokWebSocketCrawler.WebcastLinkMicMethod,
                "UserFanTicket": TiktokWebSocketCrawler.UserFanTicket,
                "WebcastLinkMessage": TiktokWebSocketCrawler.WebcastLinkMessage,
                "WebcastLinkMicBattle": TiktokWebSocketCrawler.WebcastLinkMicBattle,
                "WebcastLinkLayerMessage": TiktokWebSocketCrawler.WebcastLinkLayerMessage,
                "WebcastRoomMessage": TiktokWebSocketCrawler.WebcastRoomMessage,
                "WebcastOecLiveShoppingMessage": TiktokWebSocketCrawler.WebcastOecLiveShoppingMessage,
                # TODO: 以下消息类型暂未实现
                # WebcastOecLiveManagerMessage
                # WebcastInRoomBannerMessage
                # WebcastAnchorToolModificationMessage
            }

        async with TiktokWebSocketCrawler(self.kwargs, callbacks=wss_callbacks) as wss:

            params = LiveWebcast(
                room_id=room_id,
                internal_ext=quote(internal_ext, safe=""),
                cursor=cursor,
                wrss=wrss,
            )

            result = await wss.fetch_live_danmaku(params)

            if result == "closed":
                logger.info(_("直播间：{0} 已结束直播").format(room_id))
            elif result == "error":
                logger.error(_("直播间：{0} 弹幕连接异常").format(room_id))

            return


async def main(kwargs):
    mode = kwargs.get("mode")
    if mode in mode_function_map:
        await mode_function_map[mode](TiktokHandler(kwargs))
    else:
        logger.error(_("不存在该模式: {0}").format(mode))

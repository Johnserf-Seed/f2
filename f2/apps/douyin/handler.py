# path: f2/apps/douyin/handler.py

import asyncio

from rich.rule import Rule
from pathlib import Path
from typing import AsyncGenerator, Union, Dict, Any, List

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.utils.decorators import mode_handler, mode_function_map

# from f2.utils.utils import split_set_cookie
from f2.apps.douyin.db import AsyncUserDB, AsyncVideoDB
from f2.apps.douyin.crawler import DouyinCrawler, DouyinWebSocketCrawler
from f2.apps.douyin.dl import DouyinDownloader
from f2.apps.douyin.model import (
    UserPost,
    UserProfile,
    UserLike,
    UserCollection,
    UserCollects,
    UserCollectsVideo,
    UserMusicCollection,
    UserMix,
    PostDetail,
    UserLive,
    UserLive2,
    # LoginGetQr,
    # LoginCheckQr,
    UserFollowing,
    UserFollower,
    PostRelated,
    FriendFeed,
    LiveWebcast,
    LiveImFetch,
    QueryUser,
    FollowingUserLive,
)
from f2.apps.douyin.filter import (
    UserPostFilter,
    UserProfileFilter,
    UserCollectionFilter,
    UserCollectsFilter,
    UserMusicCollectionFilter,
    UserMixFilter,
    PostDetailFilter,
    UserLiveFilter,
    UserLive2Filter,
    # GetQrcodeFilter,
    # CheckQrcodeFilter,
    UserFollowingFilter,
    UserFollowerFilter,
    PostRelatedFilter,
    FriendFeedFilter,
    LiveImFetchFilter,
    QueryUserFilter,
    FollowingUserLiveFilter,
)
from f2.apps.douyin.algorithm.webcast_signature import DouyinWebcastSignature
from f2.apps.douyin.utils import (
    SecUserIdFetcher,
    AwemeIdFetcher,
    MixIdFetcher,
    WebCastIdFetcher,
    ClientConfManager,
    # VerifyFpManager,
    create_or_rename_user_folder,
    # show_qrcode,
)
from f2.cli.cli_console import RichConsoleManager
from f2.exceptions.api_exceptions import APIResponseError
from f2.utils.utils import interval_2_timestamp, timestamp_2_str

rich_console = RichConsoleManager().rich_console
rich_prompt = RichConsoleManager().rich_prompt


class DouyinHandler:

    # 需要忽略的字段（需过滤掉有时效性的字段）
    ignore_fields = [
        "video_play_addr",
        "images",
        "video_bit_rate",
        "cover",
        "images_video",
    ]

    def __init__(self, kwargs: Dict = ...) -> None:
        self.kwargs = kwargs
        self.downloader = DouyinDownloader(kwargs)

    async def fetch_user_profile(
        self,
        sec_user_id: str,
    ) -> UserProfileFilter:
        """
        用于获取指定用户的个人信息
        (Used to get personal info of specified users)

        Args:
            sec_user_id: str: 用户ID (User ID)

        Return:
            user: UserProfileFilter: 用户信息过滤器 (User info filter)
        """
        if not sec_user_id:
            raise ValueError(_("`sec_user_id`不能为空"))

        async with DouyinCrawler(self.kwargs) as crawler:
            params = UserProfile(sec_user_id=sec_user_id)
            response = await crawler.fetch_user_profile(params)
            user = UserProfileFilter(response)
            if user.nickname is None:
                raise APIResponseError(
                    _("`fetch_user_profile`请求失败，请更换cookie或稍后再试")
                )
            return UserProfileFilter(response)

    async def get_or_add_user_data(
        self,
        kwargs: Dict,
        sec_user_id: str,
        db: AsyncUserDB,
    ) -> Path:
        """
        获取或创建用户数据同时创建用户目录
        (Get or create user data and create user directory)

        Args:
            kwargs (Dict): 配置参数 (Conf parameters)
            sec_user_id (str): 用户ID (User ID)
            db (AsyncUserDB): 用户数据库 (User database)

        Returns:
            user_path (Path): 用户目录路径 (User directory path)
        """

        # 尝试从数据库中获取用户数据
        local_user_data = await db.get_user_info(sec_user_id)

        # 从服务器获取当前用户最新数据
        current_user_data = await self.fetch_user_profile(sec_user_id)

        # 获取当前用户最新昵称
        current_nickname = current_user_data.nickname

        # 设置用户目录
        user_path = create_or_rename_user_folder(
            kwargs, local_user_data, current_nickname
        )

        # 如果用户不在数据库中，将其添加到数据库
        if not local_user_data:
            await db.add_user_info(**current_user_data._to_dict())

        return user_path

    @classmethod
    async def get_or_add_video_data(
        cls,
        aweme_data: Dict,
        db: AsyncVideoDB,
        ignore_fields: List = None,
    ):
        """
        获取或创建作品数据库数据
        (Get or create user data and create user directory)

        Args:
            aweme_data (Dict): 作品数据 (User data)
            db (AsyncVideoDB): 作品数据库 (User database)
            ignore_fields (list): 剔除的字段
        """

        # 尝试从数据库中获取作品数据
        local_video_data = await db.get_video_info(aweme_data.get("aweme_id"))

        # 如果作品不在数据库中，将其添加到数据库
        if not local_video_data:
            # 从服务器获取当前作品最新数据
            # current_video_data = await fetch_one_video(aweme_data.get("aweme_id"))
            await db.add_video_info(ignore_fields=ignore_fields, **aweme_data)

    @mode_handler("one")
    async def handle_one_video(self):
        """
        用于处理单个作品。
        (Used to process a single video.)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        aweme_id = await AwemeIdFetcher.get_aweme_id(self.kwargs.get("url"))

        aweme_data = await self.fetch_one_video(aweme_id)

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(
                self.kwargs, aweme_data.sec_user_id, db
            )

        async with AsyncVideoDB("douyin_videos.db") as db:
            await self.get_or_add_video_data(
                aweme_data._to_dict(), db, self.ignore_fields
            )

        logger.debug(_("单个作品数据：{0}").format(aweme_data._to_dict()))

        # 创建下载任务
        await self.downloader.create_download_tasks(
            self.kwargs, aweme_data._to_dict(), user_path
        )

    async def fetch_one_video(
        self,
        aweme_id: str,
    ) -> PostDetailFilter:
        """
        用于获取单个作品。

        Args:
            aweme_id: str: 作品ID

        Return:
            video: PostDetailFilter: 单个作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法
        """

        logger.info(_("处理作品: {0} 数据").format(aweme_id))
        async with DouyinCrawler(self.kwargs) as crawler:
            params = PostDetail(aweme_id=aweme_id)
            response = await crawler.fetch_post_detail(params)
            video = PostDetailFilter(response)

        logger.debug(
            _("作品ID：{0} 作品文案：{1} 作者：{2}").format(
                video.aweme_id, video.desc, video.nickname
            )
        )

        return video

    @mode_handler("post")
    async def handle_user_post(self):
        """
        用于处理用户发布的作品。
        (Used to process videos published by users.)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        min_cursor = 0
        max_cursor = self.kwargs.get("max_cursor", 0)
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")
        interval = self.kwargs.get("interval")

        # 判断是否提供了interval参数，如果有则获取start_date转时间戳提供给max_cursor
        if interval is not None and interval != "all":
            # 倒序查找
            min_cursor = interval_2_timestamp(interval, date_type="start")
            max_cursor = interval_2_timestamp(interval, date_type="end")

        # 获取用户数据并返回创建用户目录
        sec_user_id = await SecUserIdFetcher.get_sec_user_id(self.kwargs.get("url"))
        async with AsyncUserDB("douyin_users.db") as udb:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, udb)

        async for aweme_data_list in self.fetch_user_post_videos(
            sec_user_id, min_cursor, max_cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

            # # 一次性批量插入作品数据到数据库
            # async with AsyncVideoDB("douyin_videos.db") as db:
            #     await db.batch_insert_videos(aweme_data_list._to_list(), ignore_fields)

    async def fetch_user_post_videos(
        self,
        sec_user_id: str,
        min_cursor: int = 0,
        max_cursor: int = 0,
        page_counts: int = 20,
        max_counts: int = None,
    ) -> AsyncGenerator[UserPostFilter, Any]:
        """
        用于获取指定用户发布的作品列表。

        Args:
            sec_user_id: str: 用户ID
            max_cursor: int: 起始页
            page_counts: int: 每页作品数
            max_counts: int: 最大作品数

        Return:
            video: AsyncGenerator[UserPostFilter, Any]: 发布作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.info(_("处理用户：{0} 发布的作品").format(sec_user_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(
                    _("处理第 {0} 页 ({1})").format(
                        max_cursor, timestamp_2_str(max_cursor)
                    )
                )
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserPost(
                    max_cursor=max_cursor,
                    count=current_request_size,
                    sec_user_id=sec_user_id,
                )
                response = await crawler.fetch_user_post(params)
                video = UserPostFilter(response)
                yield video

            if max_cursor < min_cursor:
                logger.info(_("已经处理到指定时间范围内的作品"))
                break

            if not video.has_aweme:
                logger.info(_("第 {0} 页没有找到作品").format(max_cursor))
                if not video.has_more:
                    logger.info(_("用户: {0} 所有作品采集完毕").format(sec_user_id))
                    break

                max_cursor = video.max_cursor
                continue

            logger.debug(_("当前请求的max_cursor：{0}").format(max_cursor))
            logger.debug(
                _("作品ID：{0} 作品文案：{1} 作者：{2}").format(
                    video.aweme_id, video.desc, video.nickname
                )
            )

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(video.aweme_id)
            max_cursor = video.max_cursor

            rich_console.print(Rule())
            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理用户发布的作品，共处理 {0} 个作品").format(videos_collected)
        )

    @mode_handler("like")
    async def handle_user_like(self):
        """
        用于处理用户喜欢的作品 (Used to process videos liked by users)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", 0)
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        # 获取用户数据并返回创建用户目录
        sec_user_id = await SecUserIdFetcher.get_sec_user_id(self.kwargs.get("url"))
        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, db)

        async for aweme_data_list in self.fetch_user_like_videos(
            sec_user_id, max_cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

            # async with AsyncVideoDB("douyin_videos.db") as db:
            #     for aweme_data in aweme_data_list:
            #         await get_or_add_video_data(aweme_data, db, ignore_fields)

            # # 一次性批量插入作品数据到数据库
            # async with AsyncVideoDB("douyin_videos.db") as db:
            #     await db.batch_insert_videos(aweme_data_list, ignore_fields)

    async def fetch_user_like_videos(
        self,
        sec_user_id: str,
        max_cursor: int = 0,
        page_counts: int = 20,
        max_counts: int = None,
    ) -> AsyncGenerator[UserPostFilter, Any]:
        """
        用于获取指定用户点赞的作品列表。

        Args:
            sec_user_id: str: 用户ID
            max_cursor: int: 起始页
            page_counts: int: 每页作品数
            max_counts: int: 最大作品数

        Return:
            video: AsyncGenerator[UserPostFilter, Any]: 点赞作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.info(_("处理用户：{0} 点赞的作品").format(sec_user_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(
                    _("处理第 {0} 页 ({1})").format(
                        max_cursor, timestamp_2_str(max_cursor)
                    )
                )
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserLike(
                    max_cursor=max_cursor,
                    count=current_request_size,
                    sec_user_id=sec_user_id,
                )
                response = await crawler.fetch_user_like(params)
                like = UserPostFilter(response)
                yield like

            if not like.has_aweme:
                logger.info(_("第 {0} 页没有找到作品").format(max_cursor))
                if not like.has_more:
                    logger.info(_("用户：{0} 所有作品采集完毕").format(sec_user_id))
                    break

                max_cursor = like.max_cursor
                continue

            logger.debug(_("当前请求的max_cursor：{0}").format(max_cursor))
            logger.debug(
                _("作品ID：{0} 作品文案：{1} 作者：{2}").format(
                    like.aweme_id, like.desc, like.nickname
                )
            )

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(like.aweme_id)
            max_cursor = like.max_cursor

            rich_console.print(Rule())

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理用户点赞的作品，共处理 {0} 个作品").format(videos_collected)
        )

    @mode_handler("music")
    async def handle_user_music_collection(self):
        """
        用于处理用户收藏的音乐 (Used to process music collected by users)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", 0)
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        # Web端音乐收藏作品的接口只能通过登录的cookie获取，与配置的URL无关。
        # 因此，即使填写了其他人的URL，也只能获取到你自己的音乐收藏作品。
        # 此外，音乐收藏作品的文件夹将根据所配置的URL主页用户名来确定。
        # 为避免将文件下载到其他人的文件夹下，请务必确保填写的URL是你自己的主页URL。
        sec_user_id = await SecUserIdFetcher.get_sec_user_id(self.kwargs.get("url"))

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, db)

        async for aweme_data_list in self.fetch_user_music_collection(
            max_cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_music_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_user_music_collection(
        self,
        max_cursor: int = 0,
        page_counts: int = 20,
        max_counts: int = None,
    ) -> AsyncGenerator[UserMusicCollectionFilter, Any]:
        """
        用于获取指定用户收藏的音乐作品列表。

        Args:
            max_cursor: int: 起始页
            page_counts: int: 每页作品数
            max_counts: int: 最大作品数

        Return:
            music: AsyncGenerator[UserMusicCollectionFilter, Any]: 音乐数据过滤器，包含音乐数据的_to_raw、_to_dict、_to_list方法
        """

        max_counts = max_counts or float("inf")
        music_collected = 0

        logger.info(_("处理用户收藏的音乐作品"))

        while music_collected < max_counts:
            current_request_size = min(page_counts, max_counts - music_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(
                    _("处理第 {0} 页 ({1})").format(
                        max_cursor, timestamp_2_str(max_cursor)
                    )
                )
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserMusicCollection(
                    cursor=max_cursor, count=current_request_size
                )
                response = await crawler.fetch_user_music_collection(params)
                music = UserMusicCollectionFilter(response)
                yield music

            if not music.has_more:
                logger.info(_("用户收藏的音乐作品采集完毕"))
                break

            logger.debug(_("当前请求的max_cursor：{0}").format(max_cursor))
            logger.debug(
                _("音乐ID：{0} 音乐标题：{1} 作者：{2}").format(
                    music.music_id, music.title, music.author
                )
            )

            # 更新已经处理的音乐数量 (Update the number of music processed)
            music_collected += len(music.music_id)
            max_cursor = music.max_cursor

            rich_console.print(Rule())

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理用户收藏音乐作品，共处理 {0} 个作品").format(music_collected)
        )

    @mode_handler("collection")
    async def handle_user_collection(self):
        """
        用于处理用户收藏的作品 (Used to process videos collected by users)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", 0)
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")
        # 由于Web端收藏作品的接口只能通过登录的cookie获取，而与配置的URL无关。
        # 因此，即使填写了其他人的URL，也只能获取到你自己的收藏作品。
        # 此外，收藏作品的文件夹将根据所配置的URL主页用户名来确定。
        # 为避免将文件下载到其他人的文件夹下，请务必确保填写的URL是你自己的主页URL。
        sec_user_id = await SecUserIdFetcher.get_sec_user_id(self.kwargs.get("url"))

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, db)

        async for aweme_data_list in self.fetch_user_collection_videos(
            max_cursor, page_counts, max_counts
        ):
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_user_collection_videos(
        self,
        max_cursor: int = 0,
        page_counts: int = 20,
        max_counts: int = None,
    ) -> AsyncGenerator[UserCollectionFilter, Any]:
        """
        用于获取指定用户收藏的作品列表。
        (Used to get the list of videos collected by the specified user.)

        Args:
            max_cursor: int: 起始页 (Start page)
            page_counts: int: 每页作品数 (Number of videos per page)
            max_counts: int: 最大作品数 (Maximum number of videos)

        Return:
            collection: AsyncGenerator[UserCollectionFilter, Any]: 收藏作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法

        Note:
            该接口需要用POST且只靠cookie来获取数据。
            (This interface needs to use POST and only rely on cookies to obtain data.)
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.info(_("处理用户收藏的作品"))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(
                    _("处理第 {0} 页 ({1})").format(
                        max_cursor, timestamp_2_str(max_cursor)
                    )
                )
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserCollection(cursor=max_cursor, count=current_request_size)
                response = await crawler.fetch_user_collection(params)
                collection = UserCollectionFilter(response)
                yield collection

            if not collection.has_more:
                logger.info(_("用户收藏的作品采集完毕"))
                break

            logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
            logger.debug(
                _("作品ID: {0} 作品文案: {1} 作者: {2}").format(
                    collection.aweme_id, collection.desc, collection.nickname
                )
            )

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(collection.aweme_id)
            max_cursor = collection.max_cursor

            rich_console.print(Rule())

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理用户收藏作品，共处理 {0} 个作品").format(videos_collected)
        )

    @mode_handler("collects")
    async def handle_user_collects(self):
        """
        用于处理用户收藏夹的作品 (Used to process videos in user collections)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", 0)
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")
        # 由于无法在Web端获取收藏夹的URL，因此无法通过URL来获取收藏夹作品。
        # Web端收藏夹作品的接口只能通过登录的cookie获取，与配置的URL无关。
        # 因此，即使填写了其他人的URL，也只能获取到你自己的收藏夹作品。
        # 此外，收藏夹作品的文件夹将根据所配置的URL主页用户名来确定。
        # 为避免将文件下载到其他人的文件夹下，请务必确保填写的URL是你自己的主页URL。
        sec_user_id = await SecUserIdFetcher.get_sec_user_id(self.kwargs.get("url"))

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, db)

        async for collects in self.fetch_user_collects(
            max_cursor, page_counts, max_counts
        ):
            choose_collects_id = await self.select_user_collects(collects)

            if isinstance(choose_collects_id, str):
                choose_collects_id = [choose_collects_id]

            for collects_id in choose_collects_id:
                # 由于收藏夹作品包含在用户名下且存在收藏夹名，因此将额外创建收藏夹名的文件夹
                # 将会根据是否设置了 --folderize 参数来决定是否创建收藏夹名的文件夹
                # 例如: 用户名/收藏夹名/作品名.mp4
                if self.kwargs.get("folderize"):
                    tmp_user_path = user_path
                    tmp_user_path = (
                        tmp_user_path
                        / collects.collects_name[
                            collects.collects_id.index(int(collects_id))
                        ]
                    )
                else:
                    tmp_user_path = user_path

                async for aweme_data_list in self.fetch_user_collects_videos(
                    collects_id, max_cursor, page_counts, max_counts
                ):
                    await self.downloader.create_download_tasks(
                        self.kwargs, aweme_data_list._to_list(), tmp_user_path
                    )

            logger.info(
                _("结束处理用户收藏夹作品，共处理 {0} 个作品").format(
                    len(choose_collects_id)
                )
            )

    async def select_user_collects(
        self, collects: UserCollectsFilter
    ) -> Union[str, List[str]]:
        """
        用于选择收藏夹
        (Used to select the collection)

        Args:
            collects: UserCollectsFilter: 收藏夹列表过滤器  (Collection list Filter)

        Return:
            collects_id: Union[str, List[str]]: 选择的收藏夹ID (Selected collects_id)
        """

        rich_console.print(_("0: [bold]全部下载[/bold]"))
        for i in range(len(collects.collects_id)):
            rich_console.print(
                _(
                    "{0}：{1} (包含 {2} 个作品[以网页实际数量为准]，收藏夹ID {3})"
                ).format(
                    i + 1,
                    collects.collects_name[i],
                    collects.total_number[i],
                    collects.collects_id[i],
                )
            )

        # rich_prompt 会有字符刷新问题，暂时使用rich_print
        rich_console.print(_("[bold yellow]请输入希望下载的收藏夹序号：[/bold yellow]"))
        selected_index = int(
            rich_prompt.ask(
                # _("[bold yellow]请输入希望下载的收藏夹序号:[/bold yellow]"),
                choices=[str(i) for i in range(len(collects.collects_id) + 1)],
            )
        )

        if selected_index == 0:
            return collects.collects_id
        else:
            return str(collects.collects_id[selected_index - 1])

    async def fetch_user_collects(
        self,
        max_cursor: int = 0,
        page_counts: int = 20,
        max_counts: int = None,
    ) -> AsyncGenerator[UserCollectsFilter, Any]:
        """
        用于获取指定用户收藏夹。
        (Used to get the list of videos in the specified user's collection.)

        Args:
            max_cursor: int: 起始页 (Page cursor)
            page_counts: int: 每页收藏夹数  (Page counts)
            max_counts: int: 最大收藏夹数 (Max counts)

        Return:
            collects: AsyncGenerator[UserCollectsFilter, Any]: 收藏夹数据过滤器，包含收藏夹数据的_to_raw、_to_dict方法)
        """

        max_counts = max_counts or float("inf")
        collected = 0

        logger.info(_("处理用户收藏夹"))

        while collected < max_counts:
            logger.debug(
                _("当前请求的max_cursor：{0}， max_counts：{1}").format(
                    max_cursor, max_counts
                )
            )
            rich_console.print(
                Rule(
                    _("处理第 {0} 页 ({1})").format(
                        max_cursor, timestamp_2_str(max_cursor)
                    )
                )
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserCollects(cursor=max_cursor, count=page_counts)
                response = await crawler.fetch_user_collects(params)
                collects = UserCollectsFilter(response)
                yield collects

            # 更新已经处理的收藏夹数量 (Update the number of collections processed)
            collected += len(collects.collects_id)

            if not collects.has_more:
                break

            logger.debug(
                _("收藏夹ID：{0} 收藏夹标题：{1}").format(
                    collects.collects_id, collects.collects_name
                )
            )

            max_cursor = collects.max_cursor

            rich_console.print(Rule())

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(_("结束处理用户收藏夹，共找到 {0} 个收藏夹").format(collected))

    async def fetch_user_collects_videos(
        self,
        collects_id: str,
        max_cursor: int = 0,
        page_counts: int = 20,
        max_counts: int = None,
    ) -> AsyncGenerator[UserCollectionFilter, Any]:
        """
        用于获取指定用户收藏夹的作品列表。
        (Used to get the list of videos in the specified user's collection.)

        Args:
            collects_id: str: 收藏夹ID (Collection ID)
            max_cursor: int: 起始页 (Page cursor)
            page_counts: int: 每页作品数 (Number of videos per page)
            max_counts: int: 最大作品数 (Maximum number of videos)

        Return:
            video: AsyncGenerator[UserCollectionFilter, Any]: 收藏夹作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.info(_("处理收藏夹：{0} 的作品").format(collects_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(
                    _("处理第 {0} 页 ({1})").format(
                        max_cursor, timestamp_2_str(max_cursor)
                    )
                )
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserCollectsVideo(
                    cursor=max_cursor,
                    count=current_request_size,
                    collects_id=collects_id,
                )
                response = await crawler.fetch_user_collects_video(params)
                video = UserCollectionFilter(response)

                # 更新已处理视频数量
                videos_collected += len(video.aweme_id)

                if video.has_aweme:
                    if not video.has_more:
                        yield video
                        break

                    logger.debug(_("当前请求的max_cursor：{0}").format(max_cursor))
                    logger.debug(
                        _("视频ID：{0} 视频文案：{1} 作者：{2}").format(
                            video.aweme_id, video.desc, video.nickname
                        )
                    )

                    yield video
                    max_cursor = video.max_cursor
                else:
                    logger.info(_("{0} 页没有找到作品").format(max_cursor))

                    if not video.has_more:
                        break

            max_cursor = video.max_cursor

            rich_console.print(Rule())

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("收藏夹：{0} 所有作品采集完毕，共处理 {1} 个作品").format(
                collects_id, videos_collected
            )
        )

    @mode_handler("mix")
    async def handle_user_mix(self):
        """
        用于处理用户合集的作品 (Used to process videos of users' mix)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", 0)
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        # 先假定合集链接获取合集ID
        try:
            logger.info(_("正在从合集链接获取合集ID"))
            mix_id = await MixIdFetcher.get_mix_id(self.kwargs.get("url"))
            async for aweme_data in self.fetch_user_mix_videos(mix_id, 0, 20, 1):
                logger.info(_("正在从合集作品里获取sec_user_id"))
                sec_user_id = aweme_data.sec_user_id[0]  # 注意这里是一个列表
        except Exception as e:
            logger.warning(_("获取合集ID失败，尝试从合集作品链接中解析。"))
            # 如果获取失败，则假定作品链接获取作品ID
            logger.info(_("正在从合集作品链接获取合集ID"))
            aweme_id = await AwemeIdFetcher.get_aweme_id(self.kwargs.get("url"))
            aweme_data = await self.fetch_one_video(aweme_id)
            sec_user_id = aweme_data.sec_user_id
            mix_id = aweme_data.mix_id

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, db)

        async for aweme_data_list in self.fetch_user_mix_videos(
            mix_id, max_cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

        # async with AsyncVideoDB("douyin_videos.db") as db:
        #     for aweme_data in aweme_data_list._to_list():
        #         await get_or_add_video_data(aweme_data, db, ignore_fields)

    async def fetch_user_mix_videos(
        self,
        mix_id: str,
        max_cursor: int = 0,
        page_counts: int = 20,
        max_counts: int = None,
    ) -> AsyncGenerator[UserMixFilter, Any]:
        """
        用于获取指定用户合集的作品列表。

        Args:
            mix_id: str: 合集ID
            max_cursor: int: 起始页
            page_counts: int: 每页作品数
            max_counts: int: 最大作品数

        Return:
            mix: AsyncGenerator[UserMixFilter, Any]: 合集作品数据过滤器，包含合集作品数据的_to_raw、_to_dict、_to_list方法
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.info(_("处理合集: {0} 的作品").format(mix_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(
                    _("处理第 {0} 页 ({1})").format(
                        max_cursor, timestamp_2_str(max_cursor)
                    )
                )
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserMix(
                    cursor=max_cursor, count=current_request_size, mix_id=mix_id
                )
                response = await crawler.fetch_user_mix(params)
                mix = UserMixFilter(response)
                yield mix

            if not mix.has_more:
                logger.info(_("合集: {0} 所有作品采集完毕").format(mix_id))
                break

            logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
            logger.debug(
                _("作品ID: {0} 作品文案: {1} 作者: {2}").format(
                    mix.aweme_id, mix.desc, mix.nickname
                )
            )

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(mix.aweme_id)
            max_cursor = mix.max_cursor

            rich_console.print(Rule())

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理用户合集作品，共处理 {0} 个作品").format(videos_collected)
        )

    @mode_handler("live")
    async def handle_user_live(self):
        """
        用于处理用户直播 (Used to process user live)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        # 获取直播相关信息与主播信息
        webcast_id = await WebCastIdFetcher.get_webcast_id(self.kwargs.get("url"))

        # 然后下载直播推流
        webcast_data = await self.fetch_user_live_videos(webcast_id)

        live_status = webcast_data.live_status
        sec_user_id = webcast_data.sec_user_id

        # 是否正在直播
        if live_status != 2:
            logger.info(_("直播：{0} 已结束").format(webcast_id))
            return

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, db)

        await self.downloader.create_stream_tasks(
            self.kwargs, webcast_data._to_dict(), user_path
        )

    async def fetch_user_live_videos(
        self,
        webcast_id: str,
    ) -> UserLiveFilter:
        """
        用于获取指定用户直播列表。
        (Used to get the list of videos collected by the specified user.)

        Args:
            webcast_id: str: 直播ID (Live ID)

        Return:
            webcast_data: Dict: 直播数据字典，包含直播ID、直播标题、直播状态、观看人数、子分区、主播昵称
            (Live data Dict, including live ID, live title, live status, number of viewers,
            sub-partition, anchor nickname)
        """

        logger.debug(_("处理直播: {0} 的数据").format(webcast_id))

        async with DouyinCrawler(self.kwargs) as crawler:
            params = UserLive(web_rid=webcast_id, room_id_str="")
            response = await crawler.fetch_live(params)
            live = UserLiveFilter(response)

        logger.info(
            _("房间ID: {0} 直播标题: {1} 直播状态: {2} 观看人数: {3}").format(
                live.room_id,
                live.live_title,
                live.live_status,
                live.user_count,
            )
        )
        logger.debug(
            _("子分区: {0} 主播昵称: {1}").format(
                live.sub_partition_title, live.nickname
            )
        )

        logger.debug(_("结束直播信息处理"))
        return live

    async def fetch_user_live_videos_by_room_id(
        self,
        room_id: str,
    ) -> UserLive2Filter:
        """
        使用room_id获取指定用户直播列表。
        (Used to get the list of videos collected by the specified user)

        Args:
            room_id: str: 直播ID (Live ID)

        Return:
            webcast_data: Dict: 直播数据字典，包含直播ID、直播标题、直播状态、观看人数、主播昵称
            (Live data Dict, including live ID, live title, live status, number of viewers,
            anchor nickname)
        """

        logger.info(_("处理房间号: {0} 的直播数据").format(room_id))

        async with DouyinCrawler(self.kwargs) as crawler:
            params = UserLive2(room_id=room_id)
            response = await crawler.fetch_live_room_id(params)
            live = UserLive2Filter(response)

        logger.info(
            _("直播ID: {0} 直播标题: {1} 直播状态: {2} 观看人数: {3}").format(
                live.web_rid, live.live_title, live.live_status, live.user_count
            )
        )
        logger.debug(
            _("主播昵称: {0} 开播时间: {1} 直播流清晰度: {2}").format(
                live.nickname,
                live.create_time,
                "、".join(
                    [f"{key}: {value}" for key, value in live.resolution_name.items()]
                ),
            )
        )
        logger.info(_("结束直播数据处理"))

        return live

    @mode_handler("feed")
    async def handle_user_feed(self):
        """
        用于处理用户feed (Used to process user feed)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", 0)
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        sec_user_id = await SecUserIdFetcher.get_sec_user_id(self.kwargs.get("url"))

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, db)

        async for aweme_data_list in self.fetch_user_feed_videos(
            sec_user_id, max_cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_user_feed_videos(
        self,
        sec_user_id: str,
        max_cursor: int = 0,
        page_counts: int = 20,
        max_counts: int = None,
    ) -> AsyncGenerator[UserPostFilter, Any]:
        """
        用于获取指定用户feed的作品列表。

        Args:
            sec_user_id: str: 用户ID
            max_cursor: int: 起始页
            page_counts: int: 每页作品数
            max_counts: int: 最大作品数

        Return:
            video: AsyncGenerator[UserPostFilter, Any]: 作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.info(_("处理用户: {0} feed的作品").format(sec_user_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(
                    _("处理第 {0} 页 ({1})").format(
                        max_cursor, timestamp_2_str(max_cursor)
                    )
                )
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserPost(
                    max_cursor=max_cursor,
                    count=current_request_size,
                    sec_user_id=sec_user_id,
                )
                response = await crawler.fetch_user_post(params)
                feed = UserPostFilter(response)
                yield feed

            if not feed.has_aweme:
                logger.info(_("第 {0} 页没有找到作品").format(max_cursor))
                if not feed.has_more:
                    logger.info(_("用户: {0} 所有作品采集完毕").format(sec_user_id))
                    break

                max_cursor = feed.max_cursor
                continue

            logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
            logger.debug(
                _("作品ID: {0} 作品文案: {1} 作者: {2}").format(
                    feed.aweme_id, feed.desc, feed.nickname
                )
            )

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(feed.aweme_id)
            max_cursor = feed.max_cursor

            rich_console.print(Rule())

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理用户首页推荐作品，共处理 {0} 个作品").format(videos_collected)
        )

    @mode_handler("related")
    async def handle_related(self):
        """
        用于处理相关作品 (Used to process related videos)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        aweme_id = await AwemeIdFetcher.get_aweme_id(self.kwargs.get("url"))
        aweme_data = await self.fetch_one_video(aweme_id)

        async with AsyncUserDB("douyin_users.db") as udb:
            user_path = (
                await self.get_or_add_user_data(
                    self.kwargs, aweme_data.sec_user_id, udb
                )
                / aweme_id
            )

        async for aweme_data_list in self.fetch_related_videos(
            aweme_id, "", page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_related_videos(
        self,
        aweme_id: str,
        filterGids: str = "",
        page_counts: int = 20,
        max_counts: int = None,
    ) -> AsyncGenerator[PostRelatedFilter, Any]:
        """
        用于获取指定作品的相关推荐作品列表。

        Args:
            aweme_id: str: 作品ID
            page_counts: int: 每页作品数
            max_counts: int: 最大作品数

        Return:
            related: AsyncGenerator[PostRelatedFilter, Any]: 相关推荐作品数据过滤器
                        ，包含相关作品数据的_to_raw、_to_dict、_to_list方法
        """
        from urllib.parse import quote

        max_counts = max_counts or float("inf")
        videos_collected = 0
        # aweme_id,awme_id,aweme_id...
        filterGids = filterGids or f"{aweme_id},"

        logger.info(_("处理作品: {0} 的相关推荐").format(aweme_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            rich_console.print(
                Rule(_("处理前 {0} 个相关推荐").format(current_request_size))
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = PostRelated(
                    count=current_request_size,
                    aweme_id=aweme_id,
                    filterGids=quote(filterGids),
                )
                response = await crawler.fetch_post_related(params)
                related = PostRelatedFilter(response)
                yield related

            if not related.has_more:
                logger.info(_("作品: {0} 的所有相关推荐采集完毕").format(aweme_id))
                break

            logger.debug(_("当前请求的相关推荐数量: {0}").format(len(related.aweme_id)))
            logger.debug(
                _("作品ID: {0} 作品文案: {1} 作者: {2}").format(
                    related.aweme_id, related.desc, related.nickname
                )
            )

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(related.aweme_id)

            rich_console.print(Rule())

            # 更新过滤的作品ID (Update the filtered video ID)
            filterGids = ",".join([str(aweme_id) for aweme_id in related.aweme_id])

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(
            _("结束处理作品相似推荐，共处理 {0} 个作品").format(videos_collected)
        )

    @mode_handler("friend")
    async def handle_friend_feed(self):
        """
        用于处理用户好友作品 (Used to process user friend videos)

        Args:
            kwargs: Dict: 参数字典 (Parameter dictionary)
        """

        max_counts = self.kwargs.get("max_counts")
        sec_user_id = await SecUserIdFetcher.get_sec_user_id(self.kwargs.get("url"))

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, db)

        async for aweme_data_list in self.fetch_friend_feed_videos(
            max_counts=max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list._to_list(), user_path
            )

    async def fetch_friend_feed_videos(
        self,
        cursor: int = 0,
        level: int = 1,
        pull_type: int = 0,
        max_counts: int = None,
    ) -> AsyncGenerator[FriendFeedFilter, Any]:
        """
        用于获取指定用户好友作品列表。

        Args:
            cursor: int: 起始页
            level: int: 作品等级
            pull_type: int: 拉取类型
            max_counts: int: 最大作品数

        Return:
            friend: AsyncGenerator[UserFriendFilter, Any]: 好友作品数据过滤器，包含好友作品数据的_to_raw、_to_dict、_to_list方法
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.info(_("处理好友作品"))

        while videos_collected < max_counts:

            logger.debug(_("最大数量：{0} 个").format(max_counts))
            rich_console.print(
                Rule(_("处理第 {0} 页 ({1})").format(cursor, timestamp_2_str(cursor)))
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = FriendFeed(
                    cursor=cursor,
                    level=level,
                    pull_type=pull_type,
                )
                response = await crawler.fetch_friend_feed(params)
                friend = FriendFeedFilter(response)

            if not friend.has_more:
                logger.info(_("所有好友作品采集完毕"))
                break

            if friend.status_code != 0:
                logger.warning(
                    _("请求失败，错误码：{0} 错误信息：{1}").format(
                        friend.status_code, friend.status_msg
                    )
                )
                break
            else:
                # 因为没有好友作品第一页也会返回has_more为False，所以需要访问下一页判断是否有作品
                if not friend.has_aweme:
                    logger.info(_("第 {0} 页没有找到作品").format(cursor))
                    continue

            logger.debug(_("当前请求的cursor: {0}").format(cursor))
            logger.debug(
                _("作品ID: {0} 作品文案: {1} 作者: {2}").format(
                    friend.aweme_id, friend.desc, friend.nickname
                )
            )

            yield friend

            # 更新已经处理的作品数量 (Update the number of videos processed)
            videos_collected += len(friend.aweme_id)
            # 更新下一页的cursor (Update the cursor of the next page)
            cursor = friend.cursor
            # 更新其他参数 (Update other parameters)
            level = friend.level
            pull_type = friend.level

            rich_console.print(Rule())

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(_("结束处理好友作品，共处理 {0} 个作品").format(videos_collected))

    async def fetch_user_following(
        self,
        user_id: str = "",
        sec_user_id: str = "",
        offset: int = 0,
        count: int = 20,
        source_type: int = 4,
        min_time: int = 0,
        max_time: int = 0,
        max_counts: float = float("inf"),
    ) -> AsyncGenerator[UserFollowingFilter, Any]:
        """
        用于获取指定用户关注的用户的作品列表。

        Args:
            user_id: str: 用户ID
            sec_user_id: str: 用户ID
            offset: int: 起始页
            count: int: 每页关注用户数
            source_type: int: 排序类型
            min_time: int: 最小时间戳
            max_time: int: 最大时间戳
        Return:
            following: AsyncGenerator[UserFollowingFilter, Any]: 关注用户数据过滤器，包含关注用户数据的_to_raw、_to_dict、_to_list方法
        """

        if not user_id and not sec_user_id:
            raise ValueError(_("至少提供 user_id 或 sec_user_id 中的一个参数"))

        max_counts = max_counts or float("inf")
        users_collected = 0

        logger.info(_("处理用户：{0} 的关注用户").format(sec_user_id))

        while users_collected < max_counts:
            current_request_size = min(count, max_counts - users_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(count, current_request_size)
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserFollowing(
                    offset=offset,
                    count=current_request_size,
                    user_id=user_id,
                    sec_user_id=sec_user_id,
                    source_type=source_type,
                    min_time=min_time,
                    max_time=max_time,
                )
                response = await crawler.fetch_user_following(params)
                following = UserFollowingFilter(response)
                yield following

            if not following.has_more:
                logger.info(_("用户：{0} 所有关注用户采集完毕").format(sec_user_id))
                break

            logger.info(_("当前请求的offset：{0}").format(offset))
            logger.info(_("处理了 {0} 个关注用户").format(offset + 1))
            logger.debug(
                _("用户ID：{0} 用户昵称：{1} 用户作品数：{2} 额外内容：{3}").format(
                    following.sec_uid,
                    following.nickname,
                    following.aweme_count,
                    following.secondary_text,
                )
            )

            # 更新已经处理的用户数量 (Update the number of users processed)
            users_collected += len(following.sec_uid)
            offset = following.offset

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(_("结束处理关注用户，共处理 {0} 个用户").format(users_collected))

    async def fetch_user_follower(
        self,
        user_id: str = "",
        sec_user_id: str = "",
        offset: int = 0,
        count: int = 20,
        source_type: int = 1,
        min_time: int = 0,
        max_time: int = 0,
        max_counts: float = float("inf"),
    ) -> AsyncGenerator[UserFollowerFilter, Any]:
        """
        用于获取指定用户的粉丝列表。

        Args:
            user_id: str: 用户ID
            sec_user_id: str: 用户ID
            offset: int: 起始页
            count: int: 每页粉丝数
            source_type: int: 排序类型
            min_time: int: 最小时间戳
            max_time: int: 最大时间戳
        Return:
            follower: AsyncGenerator[UserFollowerFilter, Any]: 粉丝数据过滤器，包含用户ID列表、用户昵称、用户头像、起始页
        """

        if not user_id and not sec_user_id:
            raise ValueError(_("至少提供 user_id 或 sec_user_id 中的一个参数"))

        max_counts = max_counts or float("inf")
        users_collected = 0

        logger.info(_("处理用户：{0} 的粉丝用户").format(sec_user_id))

        while users_collected < max_counts:
            current_request_size = min(count, max_counts - users_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(count, current_request_size)
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserFollower(
                    offset=offset,
                    count=current_request_size,
                    user_id=user_id,
                    sec_user_id=sec_user_id,
                    source_type=source_type,
                    min_time=min_time,
                    max_time=max_time,
                )
                response = await crawler.fetch_user_follower(params)
                follower = UserFollowerFilter(response)
                yield follower

            if not follower.has_more:
                logger.info(_("用户：{0} 所有粉丝采集完毕").format(sec_user_id))
                break

            logger.info(
                _("当前请求的offset：{0} max_time：{1}").format(offset, max_time)
            )
            logger.info(_("处理了 {0} 个粉丝用户").format(users_collected + 1))
            logger.debug(
                _("用户ID：{0} 用户昵称：{1} 用户作品数：{2}").format(
                    follower.sec_uid, follower.nickname, follower.aweme_count
                )
            )

            # 更新已经处理的用户数量 (Update the number of users processed)
            users_collected += len(follower.sec_uid)
            offset = follower.offset

            # 更新最大(最早)时间戳，避免重复返回相同的用户
            max_time = follower.min_time

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(_("结束处理粉丝用户，共处理 {0} 个用户").format(users_collected))

    async def fetch_query_user(self) -> QueryUserFilter:
        """
        用于查询用户信息，仅返回用户的基本信息，若需要获取更多信息请使用`fetch_user_profile`。

        Return:
            user: QueryUserFilter: 查询用户数据过滤器，包含用户数据的_to_raw、_to_dict方法
        """

        logger.debug(_("查询用户基本信息"))
        async with DouyinCrawler(self.kwargs) as crawler:
            params = QueryUser()
            response = await crawler.fetch_query_user(params)
            user = QueryUserFilter(response)

        if user.status_code is None:
            logger.info(
                _("用户UniqueID：{0} 用户ID：{1} 用户创建时间：{2}").format(
                    user.user_unique_id, user.user_uid, user.create_time
                )
            )
            logger.debug(_("结束查询用户基本信息"))
        else:
            logger.warning(_("请提供正确的ttwid")),

        return user

    async def fetch_live_im(self, room_id: str, unique_id: str) -> LiveImFetchFilter:
        """
        用于获取直播间信息。

        Args:
            room_id: str: 直播间ID
            unique_id: str: 用户ID

        Return:
            live_im: LiveImFetchFilter: 直播间信息数据过滤器，包含直播间信息的_to_raw、_to_dict、_to_list方法
        """

        logger.debug(_("查询直播间信息"))

        # user = await self.fetch_query_user()

        async with DouyinCrawler(self.kwargs) as crawler:
            params = LiveImFetch(room_id=room_id, user_unique_id=unique_id)
            response = await crawler.fetch_live_im_fetch(params)
            live_im = LiveImFetchFilter(response)

        if live_im.status_code == 0:
            logger.debug(
                _("直播间Room_ID：{0} 弹幕cursor：{1}").format(
                    live_im.room_id, live_im.cursor
                )
            )
            logger.debug(_("结束查询直播间信息"))
            rich_console.print(Rule())
        else:
            logger.warning(_("请提供正确的Room_ID"))

        return live_im

    async def fetch_live_danmaku(
        self,
        room_id: str,
        user_unique_id: str,
        internal_ext: str,
        cursor: str,
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
            self.websocket: DouyinWebSocketCrawler: WebSocket连接对象
        """

        if not wss_callbacks:
            logger.warning(_("没有设置回调函数，默认使用所有回调函数"))
            wss_callbacks = {
                "WebcastRoomMessage": DouyinWebSocketCrawler.WebcastRoomMessage,
                "WebcastLikeMessage": DouyinWebSocketCrawler.WebcastLikeMessage,
                "WebcastMemberMessage": DouyinWebSocketCrawler.WebcastMemberMessage,
                "WebcastChatMessage": DouyinWebSocketCrawler.WebcastChatMessage,
                "WebcastGiftMessage": DouyinWebSocketCrawler.WebcastGiftMessage,
                "WebcastSocialMessage": DouyinWebSocketCrawler.WebcastSocialMessage,
                "WebcastRoomUserSeqMessage": DouyinWebSocketCrawler.WebcastRoomUserSeqMessage,
                "WebcastUpdateFanTicketMessage": DouyinWebSocketCrawler.WebcastUpdateFanTicketMessage,
                "WebcastCommonTextMessage": DouyinWebSocketCrawler.WebcastCommonTextMessage,
                "WebcastMatchAgainstScoreMessage": DouyinWebSocketCrawler.WebcastMatchAgainstScoreMessage,
                "WebcastEcomFansClubMessage": DouyinWebSocketCrawler.WebcastEcomFansClubMessage,
                "WebcastRanklistHourEntranceMessage": DouyinWebSocketCrawler.WebcastRanklistHourEntranceMessage,
                "WebcastRoomStatsMessage": DouyinWebSocketCrawler.WebcastRoomStatsMessage,
                "WebcastLiveShoppingMessage": DouyinWebSocketCrawler.WebcastLiveShoppingMessage,
                "WebcastLiveEcomGeneralMessage": DouyinWebSocketCrawler.WebcastLiveEcomGeneralMessage,
                "WebcastProductChangeMessage": DouyinWebSocketCrawler.WebcastProductChangeMessage,
                "WebcastRoomStreamAdaptationMessage": DouyinWebSocketCrawler.WebcastRoomStreamAdaptationMessage,
                "WebcastNotifyEffectMessage": DouyinWebSocketCrawler.WebcastNotifyEffectMessage,
                "WebcastLightGiftMessage": DouyinWebSocketCrawler.WebcastLightGiftMessage,
                "WebcastProfitInteractionScoreMessage": DouyinWebSocketCrawler.WebcastProfitInteractionScoreMessage,
                "WebcastRoomRankMessage": DouyinWebSocketCrawler.WebcastRoomRankMessage,
                "WebcastFansclubMessage": DouyinWebSocketCrawler.WebcastFansclubMessage,
                "WebcastHotRoomMessage": DouyinWebSocketCrawler.WebcastHotRoomMessage,
                "WebcastLinkMicMethod": DouyinWebSocketCrawler.WebcastLinkMicMethod,
                "LinkMicMethod": DouyinWebSocketCrawler.WebcastLinkMicMethod,
                "WebcastLinkerContributeMessage": DouyinWebSocketCrawler.WebcastLinkerContributeMessage,
                "WebcastEmojiChatMessage": DouyinWebSocketCrawler.WebcastEmojiChatMessage,
                "WebcastScreenChatMessage": DouyinWebSocketCrawler.WebcastScreenChatMessage,
                "WebcastRoomDataSyncMessage": DouyinWebSocketCrawler.WebcastRoomDataSyncMessage,
                "WebcastInRoomBannerMessage": DouyinWebSocketCrawler.WebcastInRoomBannerMessage,
                "WebcastLinkMessage": DouyinWebSocketCrawler.WebcastLinkMessage,
                "WebcastBattleTeamTaskMessage": DouyinWebSocketCrawler.WebcastBattleTeamTaskMessage,
                "WebcastHotChatMessage": DouyinWebSocketCrawler.WebcastHotChatMessage,
                # TODO: 以下消息类型暂未实现
                # WebcastLinkMicArmiesMethod
                # WebcastLinkmicPlayModeUpdateScoreMessage
                # WebcastSandwichBorderMessage
                # WebcastLuckyBoxTempStatusMessage
                # WebcastLotteryEventMessage
                # WebcastLotteryEventNewMessage
                # WebcastDecorationUpdateMessage
                # WebcastDecorationModifyMethod
                # WebcastLinkSettingNotifyMessage
                # WebcastLinkMicBattleMethod
            }

        async with DouyinWebSocketCrawler(self.kwargs, callbacks=wss_callbacks) as wss:
            signature = DouyinWebcastSignature(
                ClientConfManager.user_agent()
            ).get_signature(room_id, user_unique_id)

            params = LiveWebcast(
                room_id=room_id,
                user_unique_id=user_unique_id,
                internal_ext=internal_ext,
                cursor=cursor,
                signature=signature,
            )

            result = await wss.fetch_live_danmaku(params)

            if result == "closed":
                logger.info(_("直播间：{0} 已结束直播或断开了本地连接").format(room_id))
                rich_console.print(Rule())
            elif result == "error":
                logger.error(_("直播间：{0} 弹幕连接异常").format(room_id))

            return

    async def fetch_user_following_lives(self) -> FollowingUserLiveFilter:
        """
        用于获取关注用户的直播间信息。

        Return:
            follow_live: FollowingUserLiveFilter: 关注用户直播间信息数据过滤器，包含关注用户直播间信息的_to_raw、_to_dict、_to_list方法
        """

        logger.info(_("查询关注用户直播间信息"))

        async with DouyinCrawler(self.kwargs) as crawler:
            params = FollowingUserLive()
            response = await crawler.fetch_following_live(params)
            follow_live = FollowingUserLiveFilter(response)

        if follow_live.status_code == 0:
            logger.debug(
                _("直播间Room_ID：{0} 直播间标题：{1} 直播间人数：{2}").format(
                    follow_live.room_id,
                    follow_live.live_title_raw,
                    follow_live.user_count,
                )
            )
            logger.info(_("结束查询关注用户直播间信息"))
        else:
            logger.warning(
                _("获取关注用户直播间信息失败：{0}").format(follow_live.status_msg)
            )

        return follow_live


# async def handle_sso_login():
#     """
#     用于处理用户登录 (Used to process user login)
#     """

#     kwargs = {
#         "proxies": {"http://": None, "https://": None},
#         "cookie": "",
#         "headers": {
#             "Referer": "https://www.douyin.com/",
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/104.0.0.0 Safari/537.36",
#         },
#     }

#     async def get_qrcode() -> str:
#         params = LoginGetQr(verifyFp=verify_fp, fp=verify_fp)
#         async with DouyinCrawler(kwargs) as crawler:
#             response = await crawler.fetch_login_qrcode(params)
#             sso = GetQrcodeFilter(response)
#             show_qrcode(sso.qrcode_index_url)
#             return await check_qrcode(sso.token, crawler)

#     async def check_qrcode(token: str, crawler) -> bool:
#         """
#         检查二维码状态

#         Args:
#             token (str): 二维码token

#         Returns:
#             bool: 是否成功登录
#         """
#         logger.debug(f"check_qrcode token:{token}")

#         status_mapping = {
#             "1": {"message": _("[  登录  ]:等待二维码扫描！"), "log": logger.info},
#             "2": {"message": _("[  登录  ]:扫描二维码成功！"), "log": logger.info},
#             "3": {"message": _("[  登录  ]:确认二维码登录！"), "log": logger.info},
#             "4": {
#                 "message": _("[  登录  ]:访问频繁，请检查参数！"),
#                 "log": logger.warning,
#             },
#             "5": {
#                 "message": _("[  登录  ]:二维码过期，重新获取！"),
#                 "log": logger.warning,
#             },
#             "2046": {
#                 "messages": _("[  登录  ]:扫码环境异常，请前往app验证！"),
#                 "log": logger.warning,
#             },
#         }

#         while True:
#             params = LoginCheckQr(token=token, verifyFp=verify_fp, fp=verify_fp)
#             check_response = await crawler.fetch_check_qrcode(params)
#             check = CheckQrcodeFilter(check_response.json())
#             check_status = check.status
#             check_status = "2046" if check_status is None else check_status

#             status_info = status_mapping.get(check_status, {})
#             message = status_info.get("message", "")
#             log_func = status_info.get("log", logger.info)
#             logger.info(message)
#             log_func(message)

#             if check_status == "3":
#                 login_cookies = split_set_cookie(
#                     check_response.headers.get("set-cookie", "")
#                 )
#                 is_login, login_cookie = await login_redirect(
#                     check.redirect_url, login_cookies, crawler
#                 )
#                 return is_login, login_cookie
#             elif check_status == "5":
#                 get_qrcode()
#                 break
#             elif check_status is None:
#                 break

#             await asyncio.sleep(5)

#     async def login_redirect(redirect_url: str, login_cookies: str, crawler):
#         """
#         登录重定向，获取登录后Cookie

#         Args:
#             redirect_url (str): 重定向url
#             login_cookies (str): 登录cookie

#         Returns:
#             is_login (bool): 是否成功登录
#             login_cookie (str): 登录cookie
#         """
#         crawler.headers["Cookie"] = login_cookies
#         redirect_response = await crawler.get_fetch_data(redirect_url)

#         if redirect_response.history and len(redirect_response.history) > 1:
#             logger.debug(f"login_redirect headers:{redirect_response.headers}")
#             logger.debug(f"login_redirect history:{redirect_response.history}")
#             logger.debug(
#                 f"login_redirect history[0] headers:{redirect_response.history[0].headers}"
#             )
#             logger.debug(
#                 f"login_redirect history[1] headers:{redirect_response.history[1].headers}"
#             )
#             # 获取重最后一个重定向里的Cookie
#             login_cookie = split_set_cookie(
#                 redirect_response.history[1].headers.get("set-cookie", "")
#             )
#             logger.debug(f"login_cookie:{login_cookie}")
#             return True, login_cookie
#         else:
#             logger.warning("[  登录  ]:自动重定向登录失败")
#             if redirect_response:
#                 error_message = f"网络异常: 自动重定向登录失败。 状态码: {redirect_response.status_code}, 响应体: {redirect_response.text}"
#             else:
#                 error_message = f"网络异常: 自动重定向登录失败。 无法连接到服务器。"
#             logger.warning(error_message)
#             return False, ""

#     verify_fp = VerifyFpManager.gen_verify_fp()
#     return await get_qrcode()


async def main(kwargs):
    mode = kwargs.get("mode")
    if mode in mode_function_map:
        await mode_function_map[mode](DouyinHandler(kwargs))
    else:
        logger.error(_("不存在该模式: {0}").format(mode))

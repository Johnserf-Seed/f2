# path: f2/apps/douyin/handler.py

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Union, Dict, Any, List

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.utils.mode_handler import mode_handler, mode_function_map
from f2.utils.utils import split_set_cookie
from f2.apps.douyin.db import AsyncUserDB, AsyncVideoDB
from f2.apps.douyin.crawler import DouyinCrawler
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
    LoginGetQr,
    LoginCheckQr,
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
    GetQrcodeFilter,
    CheckQrcodeFilter,
)
from f2.apps.douyin.utils import (
    SecUserIdFetcher,
    AwemeIdFetcher,
    WebCastIdFetcher,
    VerifyFpManager,
    create_or_rename_user_folder,
    show_qrcode,
)
from f2.cli.cli_console import RichConsoleManager

rich_console = RichConsoleManager().rich_console
rich_prompt = RichConsoleManager().rich_prompt


class DouyinHandler:

    # 需要忽略的字段（需过滤掉有时效性的字段）
    ignore_fields = ["video_play_addr", "images", "video_bit_rate", "cover"]

    def __init__(self, kwargs) -> None:
        self.kwargs = kwargs
        self.downloader = DouyinDownloader(kwargs)

    async def handler_user_profile(self, sec_user_id: str) -> UserProfileFilter:
        """
        用于获取指定用户的个人信息
        (Used to get personal info of specified users)

        Args:
            sec_user_id: str: 用户ID (User ID)

        Return:
            user: UserProfileFilter: 用户信息过滤器 (User info filter)
        """

        async with DouyinCrawler(self.kwargs) as crawler:
            params = UserProfile(sec_user_id=sec_user_id)
            response = await crawler.fetch_user_profile(params)
            return UserProfileFilter(response)

    async def get_user_nickname(self, sec_user_id: str, db: AsyncUserDB) -> str:
        """
        获取指定用户的昵称，如果不存在，则从服务器获取并存储到数据库中
        (Used to get personal info of specified users)

        Args:
            sec_user_id (str): 用户ID (User ID)
            db (AsyncUserDB): 用户数据库 (User database)

        Returns:
            user_nickname: (str): 用户昵称 (User nickname)
        """

        user_dict = await db.get_user_info(sec_user_id)
        if not user_dict:
            user_dict = await self.handler_user_profile(sec_user_id)
            await db.add_user_info(**user_dict._to_dict())
        return user_dict.get("nickname")

    async def get_or_add_user_data(
        self, kwargs: dict, sec_user_id: str, db: AsyncUserDB
    ) -> Path:
        """
        获取或创建用户数据同时创建用户目录
        (Get or create user data and create user directory)

        Args:
            kwargs (dict): 配置参数 (Conf parameters)
            sec_user_id (str): 用户ID (User ID)
            db (AsyncUserDB): 用户数据库 (User database)

        Returns:
            user_path (Path): 用户目录路径 (User directory path)
        """

        # 尝试从数据库中获取用户数据
        local_user_data = await db.get_user_info(sec_user_id)

        # 从服务器获取当前用户最新数据
        current_user_data = await self.handler_user_profile(sec_user_id)

        # 获取当前用户最新昵称
        current_nickname = current_user_data._to_dict().get("nickname")

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
        cls, aweme_data: dict, db: AsyncVideoDB, ignore_fields: list = None
    ):
        """
        获取或创建作品数据库数据
        (Get or create user data and create user directory)

        Args:
            aweme_data (dict): 作品数据 (User data)
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
        用于处理单个视频。
        (Used to process a single video.)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        aweme_id = await AwemeIdFetcher.get_aweme_id(self.kwargs.get("url"))

        aweme_data = await self.fetch_one_video(aweme_id)

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(
                self.kwargs, aweme_data.get("sec_user_id"), db
            )

        async with AsyncVideoDB("douyin_videos.db") as db:
            await self.get_or_add_video_data(aweme_data, db, self.ignore_fields)

        logger.debug(_("单个视频数据: {0}".format(aweme_data)))
        await self.downloader.create_download_tasks(self.kwargs, aweme_data, user_path)

    async def fetch_one_video(self, aweme_id: str) -> dict:
        """
        用于获取单个视频。

        Args:
            aweme_id: str: 视频ID

        Return:
            video_data: dict: 视频数据字典，包含视频ID、视频文案、作者昵称
        """

        logger.debug(_("开始爬取视频: {0}").format(aweme_id))
        async with DouyinCrawler(self.kwargs) as crawler:
            params = PostDetail(aweme_id=aweme_id)
            response = await crawler.fetch_post_detail(params)
            video = PostDetailFilter(response)

        logger.debug(
            _("视频ID: {0} 视频文案: {1} 作者: {2}").format(
                video.aweme_id, video.desc, video.nickname
            )
        )

        return video._to_dict()

    @mode_handler("post")
    async def handle_user_post(self):
        """
        用于处理用户发布的视频。
        (Used to process videos published by users.)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", 0)
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        # 获取用户数据并返回创建用户目录
        sec_user_id = await SecUserIdFetcher.get_sec_user_id(self.kwargs.get("url"))
        async with AsyncUserDB("douyin_users.db") as udb:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, udb)

        async for aweme_data_list in self.fetch_user_post_videos(
            sec_user_id, max_cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list, user_path
            )

            # # 一次性批量插入视频数据到数据库
            # async with AsyncVideoDB("douyin_videos.db") as db:
            #     await db.batch_insert_videos(aweme_data_list, ignore_fields)

    async def fetch_user_post_videos(
        self,
        sec_user_id: str,
        max_cursor: int,
        page_counts: int,
        max_counts: int,
    ):
        """
        用于获取指定用户发布的视频列表。

        Args:
            sec_user_id: str: 用户ID
            max_cursor: int: 起始页
            page_counts: int: 每页视频数
            max_counts: int: 最大视频数

        Return:
            aweme_data: dict: 视频数据字典，包含视频ID列表、视频文案、作者昵称、起始页
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.debug(_("开始爬取用户: {0} 发布的视频").format(sec_user_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserPost(
                    max_cursor=max_cursor,
                    count=current_request_size,
                    sec_user_id=sec_user_id,
                )
                response = await crawler.fetch_user_post(params)
                video = UserPostFilter(response)

            if not video.has_aweme:
                logger.debug(_("{0} 页没有找到作品".format(max_cursor)))
                if not video.has_more:
                    logger.debug(_("用户: {0} 所有作品采集完毕".format(sec_user_id)))
                    break

                max_cursor = video.max_cursor
                continue

            logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
            logger.debug(
                _("视频ID: {0} 视频文案: {1} 作者: {2}").format(
                    video.aweme_id, video.desc, video.nickname
                )
            )
            logger.debug("===================================")

            aweme_data_list = video._to_list()
            yield aweme_data_list

            # 更新已经处理的视频数量 (Update the number of videos processed)
            videos_collected += len(video.aweme_id)
            max_cursor = video.max_cursor

        logger.debug(_("爬取结束，共爬取 {0} 个视频").format(videos_collected))

    @mode_handler("like")
    async def handle_user_like(self):
        """
        用于处理用户喜欢的视频 (Used to process videos liked by users)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
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
                self.kwargs, aweme_data_list, user_path
            )

            # async with AsyncVideoDB("douyin_videos.db") as db:
            #     for aweme_data in aweme_data_list:
            #         await get_or_add_video_data(aweme_data, db, ignore_fields)

            # # 一次性批量插入视频数据到数据库
            # async with AsyncVideoDB("douyin_videos.db") as db:
            #     await db.batch_insert_videos(aweme_data_list, ignore_fields)

    async def fetch_user_like_videos(
        self,
        sec_user_id: str,
        max_cursor: int,
        page_counts: int,
        max_counts: int,
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """
        用于获取指定用户喜欢的视频列表。

        Args:
            sec_user_id: str: 用户ID
            max_cursor: int: 起始页
            page_counts: int: 每页视频数
            max_counts: int: 最大视频数

        Return:
            aweme_data: dict: 视频数据字典，包含视频ID列表、视频文案、作者昵称、起始页
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.debug(_("开始爬取用户: {0} 喜欢的视频").format(sec_user_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserLike(
                    max_cursor=max_cursor,
                    count=current_request_size,
                    sec_user_id=sec_user_id,
                )
                response = await crawler.fetch_user_like(params)
                video = UserPostFilter(response)

            if not video.has_aweme:
                logger.debug(_("{0} 页没有找到作品".format(max_cursor)))
                if not video.has_more:
                    logger.debug(_("用户: {0} 所有作品采集完毕".format(sec_user_id)))
                    break

                max_cursor = video.max_cursor
                continue

            logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
            logger.debug(
                _("视频ID: {0} 视频文案: {1} 作者: {2}").format(
                    video.aweme_id, video.desc, video.nickname
                )
            )
            logger.debug("===================================")

            aweme_data_list = video._to_list()
            yield aweme_data_list

            # 更新已经处理的视频数量 (Update the number of videos processed)
            videos_collected += len(aweme_data_list)
            max_cursor = video.max_cursor

        logger.debug(_("爬取结束，共爬取 {0} 个视频").format(videos_collected))

    @mode_handler("music")
    async def handle_user_music_collection(self):
        """
        用于处理用户收藏的音乐 (Used to process music collected by users)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
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
                self.kwargs, aweme_data_list, user_path
            )

    async def fetch_user_music_collection(
        self, max_cursor: int, page_counts: int, max_counts: int
    ) -> AsyncGenerator[List[Dict[str, Any]], Any]:
        """
        用于获取指定用户收藏的音乐作品列表。

        Args:
            max_cursor: int: 起始页
            page_counts: int: 每页视频数
            max_counts: int: 最大视频数

        Return:
            aweme_data: AsyncGenerator[List[Dict[str, Any]], None]: 音乐作品数据
        """

        max_counts = max_counts or float("inf")
        music_collected = 0

        logger.debug(_("开始爬取用户收藏的音乐作品"))

        while music_collected < max_counts:
            current_request_size = min(page_counts, max_counts - music_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserMusicCollection(
                    cursor=max_cursor, count=current_request_size
                )
                response = await crawler.fetch_user_music_collection(params)
                music = UserMusicCollectionFilter(response)

                logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
                logger.debug(
                    _("音乐ID: {0} 音乐标题: {1} 作者: {2}").format(
                        music.music_id, music.title, music.author
                    )
                )
            logger.debug("===================================")

            yield music._to_list()

            if not music.has_more:
                logger.debug(_("用户收藏的音乐作品采集完毕"))
                break

            # 更新已经处理的音乐数量 (Update the number of music processed)
            music_collected += len(music.music_id)
            max_cursor = music.max_cursor

    @mode_handler("collection")
    async def handle_user_collection(self):
        """
        用于处理用户收藏的视频 (Used to process videos collected by users)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
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
                self.kwargs, aweme_data_list, user_path
            )

    async def fetch_user_collection_videos(
        self, max_cursor: int = 0, page_counts: int = 20, max_counts: int = None
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """
        用于获取指定用户收藏的视频列表。
        (Used to get the list of videos collected by the specified user.)

        Args:
            max_cursor: int: 起始页 (Start page)
            page_counts: int: 每页视频数 (Number of videos per page)
            max_counts: int: 最大视频数 (Maximum number of videos)

        Return:
            aweme_data: dict: 视频数据字典, 包含视频ID列表、视频文案、作者昵称、起始页
            (Video data dictionary, including video ID list, video description,
            author nickname, start page)

        Note:
            该接口需要用POST且只靠cookie来获取数据。
            (This interface needs to use POST and only rely on cookies to obtain data.)
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.debug(_("开始爬取用户收藏的视频"))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserCollection(cursor=max_cursor, count=current_request_size)
                response = await crawler.fetch_user_collection(params)
                video = UserCollectionFilter(response)

            logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
            logger.debug(
                _("视频ID: {0} 视频文案: {1} 作者: {2}").format(
                    video.aweme_id, video.desc, video.nickname
                )
            )
            logger.debug("===================================")

            aweme_data_list = video._to_list()
            yield aweme_data_list

            if not video.has_more:
                logger.debug(_("用户收藏的视频采集完毕"))
                break

            # 更新已经处理的视频数量 (Update the number of videos processed)
            videos_collected += len(aweme_data_list)
            max_cursor = video.max_cursor

    @mode_handler("collects")
    async def handle_user_collects(self):
        """
        用于处理用户收藏夹的视频 (Used to process videos in user collections)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
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
                        self.kwargs, aweme_data_list, tmp_user_path
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
                    "{0}: {1} (包含 {2} 个作品，收藏夹ID {3})".format(
                        i + 1,
                        collects.collects_name[i],
                        collects.total_number[i],
                        collects.collects_id[i],
                    )
                )
            )

        # rich_prompt 会有字符刷新问题，暂时使用rich_print
        rich_console.print(_("[bold yellow]请输入希望下载的收藏夹序号:[/bold yellow]"))
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
        self, max_cursor: int, page_counts: int, max_counts: int
    ) -> AsyncGenerator[UserCollectsFilter, None]:
        """
        用于获取指定用户收藏夹。
        (Used to get the list of videos in the specified user's collection.)

        Args:
            max_cursor: int: 起始页 (Page cursor)
            page_counts: int: 每页收藏夹数  (Page counts)
            max_counts: int: 最大收藏夹数 (Max counts)

        Return:
            collects: AsyncGenerator[UserCollectsFilter, None]: 收藏夹列表过滤器 (Collection list Filter)
        """

        max_counts = max_counts or float("inf")
        collected = 0

        while collected < max_counts:
            logger.debug(_("开始爬取用户收藏夹"))
            logger.debug("===================================")
            logger.debug(
                _("当前请求的max_cursor: {0}， max_counts: {1}").format(
                    max_cursor, max_counts
                )
            )

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserCollects(cursor=max_cursor, count=page_counts)
                response = await crawler.fetch_user_collects(params)
                collects = UserCollectsFilter(response)

            logger.debug(
                _("收藏夹ID: {0} 收藏夹标题: {1}").format(
                    collects.collects_id, collects.collects_name
                )
            )
            logger.debug("===================================")

            yield collects

            if not collects.has_more:
                logger.info(_("所有收藏夹ID采集完毕"))
                break

            # 更新已经处理的收藏夹数量 (Update the number of collections processed)
            collected += len(collects.collects_id)
            max_cursor = collects.max_cursor

        logger.debug(_("用户收藏夹爬取结束"))

    async def fetch_user_collects_videos(
        self,
        collects_id: str,
        max_cursor: int,
        page_counts: int,
        max_counts: int,
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """
        用于获取指定用户收藏夹的视频列表。
        (Used to get the list of videos in the specified user's collection.)

        Args:
            collects_id: str: 收藏夹ID (Collection ID)
            max_cursor: int: 起始页 (Page cursor)
            page_counts: int: 每页视频数 (Number of videos per page)
            max_counts: int: 最大视频数 (Maximum number of videos)

        Return:
            aweme_data: dict: 视频数据字典, 包含视频ID列表、视频文案、作者昵称、起始页
            (Video data dictionary, including video ID list, video description,
            author nickname, start page)
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.debug(_("开始爬取收藏夹: {0} 的视频").format(collects_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserCollectsVideo(
                    cursor=max_cursor,
                    count=current_request_size,
                    collects_id=collects_id,
                )
                response = await crawler.fetch_user_collects_video(params)
                video = UserCollectionFilter(response)

            logger.debug(
                "是否有作品: {0} 是否有更多: {1}".format(
                    video.has_aweme, video.has_more
                )
            )
            if video.has_aweme:
                if not video.has_more:
                    logger.debug(_("收藏夹: {0} 所有作品采集完毕").format(collects_id))
                    yield video._to_list()
                    break
                else:
                    logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
                    logger.debug(
                        _("视频ID: {0} 视频文案: {1} 作者: {2}").format(
                            video.aweme_id, video.desc, video.nickname
                        )
                    )
                    logger.debug("===================================")

                    aweme_data_list = video._to_list()
                    yield aweme_data_list

                    # 更新已经处理的视频数量 (Update the number of videos processed)
                    videos_collected += len(aweme_data_list)
                    max_cursor = video.max_cursor
            else:
                logger.debug(_("{0} 页没有找到作品".format(max_cursor)))
                if not video.has_more:
                    logger.debug(_("收藏夹: {0} 所有作品采集完毕").format(collects_id))
                    break
                max_cursor = video.max_cursor

        logger.debug(_("爬取结束，共爬取 {0} 个视频").format(videos_collected))

    @mode_handler("mix")
    async def handle_user_mix(self):
        """
        用于处理用户合集的视频 (Used to process videos of users' collections)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", 0)
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        aweme_id = await AwemeIdFetcher.get_aweme_id(self.kwargs.get("url"))
        mix_data = await self.fetch_one_video(aweme_id)
        sec_user_id = mix_data.get("sec_user_id")
        mix_id = mix_data.get("mix_id")

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, db)

        async for aweme_data_list in self.fetch_user_mix_videos(
            mix_id, max_cursor, page_counts, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, aweme_data_list, user_path
            )

        # async with AsyncVideoDB("douyin_videos.db") as db:
        #     for aweme_data in aweme_data_list:
        #         await get_or_add_video_data(aweme_data, db, ignore_fields)

    async def fetch_user_mix_videos(
        self,
        mix_id: str,
        max_cursor: int = 0,
        page_counts: int = 20,
        max_counts: int = None,
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """
        用于获取指定用户合集的视频列表。

        Args:
            mix_id: str: 合集ID
            max_cursor: int: 起始页
            page_counts: int: 每页视频数
            max_counts: int: 最大视频数

        Return:
            aweme_data: dict: 视频数据字典，包含视频ID列表、视频文案、作者昵称、起始页
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.debug(_("开始爬取合集: {0} 的视频").format(mix_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserMix(
                    cursor=max_cursor, count=current_request_size, mix_id=mix_id
                )
                response = await crawler.fetch_user_mix(params)
                video = UserMixFilter(response)

            logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
            logger.debug(
                _("视频ID: {0} 视频文案: {1} 作者: {2}").format(
                    video.aweme_id, video.desc, video.nickname
                )
            )
            logger.debug("===================================")

            aweme_data_list = video._to_list()
            yield aweme_data_list

            # 更新已经处理的视频数量 (Update the number of videos processed)
            videos_collected += len(aweme_data_list)
            max_cursor = video.max_cursor

            if not video.has_more:
                logger.debug(_("合集: {0} 所有作品采集完毕").format(mix_id))
                break

        logger.debug(_("爬取结束，共爬取 {0} 个视频").format(videos_collected))

    @mode_handler("live")
    async def handle_user_live(self):
        """
        用于处理用户直播 (Used to process user live)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        # 获取直播相关信息与主播信息
        webcast_id = await WebCastIdFetcher.get_webcast_id(self.kwargs.get("url"))

        # 然后下载直播推流
        webcast_data = await self.fetch_user_live_videos(webcast_id)
        live_status = webcast_data.get("live_status")
        # 是否正在直播
        if live_status != 2:
            logger.debug(_("直播已结束"))
            return
        sec_user_id = webcast_data.get("sec_user_id")

        async with AsyncUserDB("douyin_users.db") as db:
            user_path = await self.get_or_add_user_data(self.kwargs, sec_user_id, db)
        await self.downloader.create_stream_tasks(self.kwargs, webcast_data, user_path)

    async def fetch_user_live_videos(self, webcast_id: str):
        """
        用于获取指定用户直播列表。
        (Used to get the list of videos collected by the specified user.)

        Args:
            webcast_id: str: 直播ID (Live ID)

        Return:
            webcast_data: dict: 直播数据字典，包含直播ID、直播标题、直播状态、观看人数、子分区、主播昵称
            (Live data dict, including live ID, live title, live status, number of viewers,
            sub-partition, anchor nickname)
        """

        logger.debug(_("开始爬取直播: {0} 的数据").format(webcast_id))
        logger.debug("===================================")

        async with DouyinCrawler(self.kwargs) as crawler:
            params = UserLive(web_rid=webcast_id, room_id_str="")
            response = await crawler.fetch_live(params)
            live = UserLiveFilter(response)

        logger.debug(
            _("直播ID: {0} 直播标题: {1} 直播状态: {2} 观看人数: {3}").format(
                live.room_id, live.live_title, live.live_status, live.user_count
            )
        )
        logger.debug(
            _("子分区: {0} 主播昵称: {1}").format(
                live.sub_partition_title, live.nickname
            )
        )
        logger.debug("===================================")
        logger.debug(_("直播信息爬取结束"))

        webcast_data = live._to_dict()
        return webcast_data

    async def fetch_user_live_videos_by_room_id(self, room_id: str):
        """
        使用room_id获取指定用户直播列表。
        (Used to get the list of videos collected by the specified user)

        Args:
            room_id: str: 直播ID (Live ID)

        Return:
            webcast_data: dict: 直播数据字典，包含直播ID、直播标题、直播状态、观看人数、主播昵称
            (Live data dict, including live ID, live title, live status, number of viewers,
            anchor nickname)
        """

        logger.debug(_("开始爬取房间号: {0} 的数据").format(room_id))
        logger.debug("===================================")

        async with DouyinCrawler(self.kwargs) as crawler:
            params = UserLive2(room_id=room_id)
            response = await crawler.fetch_live_room_id(params)
            live = UserLive2Filter(response)

        logger.debug(
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
        logger.debug("===================================")
        logger.debug(_("直播信息爬取结束"))

        webcast_data = live._to_dict()
        return webcast_data

    @mode_handler("feed")
    async def handle_user_feed(self):
        """
        用于处理用户feed (Used to process user feed)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
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
                self.kwargs, aweme_data_list, user_path
            )

    async def fetch_user_feed_videos(
        self,
        sec_user_id: str,
        max_cursor: int,
        page_counts: int,
        max_counts: int,
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """
        用于获取指定用户feed的视频列表。

        Args:
            sec_user_id: str: 用户ID
            max_cursor: int: 起始页
            page_counts: int: 每页视频数
            max_counts: int: 最大视频数

        Return:
            aweme_data: dict: 视频数据字典，包含视频ID列表、视频文案、作者昵称、起始页
        """

        max_counts = max_counts or float("inf")
        videos_collected = 0

        logger.debug(_("开始爬取用户: {0} feed的视频").format(sec_user_id))

        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(
                    max_counts, current_request_size
                )
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

            async with DouyinCrawler(self.kwargs) as crawler:
                params = UserPost(
                    max_cursor=max_cursor,
                    count=current_request_size,
                    sec_user_id=sec_user_id,
                )
                response = await crawler.fetch_user_post(params)
                video = UserPostFilter(response)

            if not video.has_aweme:
                logger.debug(_("{0} 页没有找到作品".format(max_cursor)))
                if not video.has_more:
                    logger.debug(_("用户: {0} 所有作品采集完毕".format(sec_user_id)))
                    break

                max_cursor = video.max_cursor
                continue

            logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
            logger.debug(
                _("视频ID: {0} 视频文案: {1} 作者: {2}").format(
                    video.aweme_id, video.desc, video.nickname
                )
            )
            logger.debug("===================================")

            aweme_data_list = video._to_list()
            yield aweme_data_list

            # 更新已经处理的视频数量 (Update the number of videos processed)
            videos_collected += len(video.aweme_id)
            max_cursor = video.max_cursor

        logger.debug(_("爬取结束，共爬取 {0} 个视频").format(videos_collected))


async def handle_sso_login():
    """
    用于处理用户登录 (Used to process user login)
    """

    kwargs = {
        "proxies": {"http": None, "https": None},
        "cookie": "",
        "headers": {
            "Referer": "https://www.douyin.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/104.0.0.0 Safari/537.36",
        },
    }

    async def get_qrcode() -> str:
        params = LoginGetQr(verifyFp=verify_fp, fp=verify_fp)
        async with DouyinCrawler(kwargs) as crawler:
            response = await crawler.fetch_login_qrcode(params)
            sso = GetQrcodeFilter(response)
            show_qrcode(sso.qrcode_index_url)
            return await check_qrcode(sso.token, crawler)

    async def check_qrcode(token: str, crawler) -> bool:
        """
        检查二维码状态

        Args:
            token (str): 二维码token

        Returns:
            bool: 是否成功登录
        """
        logger.debug(f"check_qrcode token:{token}")

        status_mapping = {
            "1": {"message": _("[  登录  ]:等待二维码扫描！"), "log": logger.info},
            "2": {"message": _("[  登录  ]:扫描二维码成功！"), "log": logger.info},
            "3": {"message": _("[  登录  ]:确认二维码登录！"), "log": logger.info},
            "4": {
                "message": _("[  登录  ]:访问频繁，请检查参数！"),
                "log": logger.warning,
            },
            "5": {
                "message": _("[  登录  ]:二维码过期，重新获取！"),
                "log": logger.warning,
            },
            "2046": {
                "messages": _("[  登录  ]:扫码环境异常，请前往app验证！"),
                "log": logger.warning,
            },
        }

        while True:
            params = LoginCheckQr(token=token, verifyFp=verify_fp, fp=verify_fp)
            check_response = await crawler.fetch_check_qrcode(params)
            check = CheckQrcodeFilter(check_response.json())
            check_status = check.status
            check_status = "2046" if check_status is None else check_status

            status_info = status_mapping.get(check_status, {})
            message = status_info.get("message", "")
            log_func = status_info.get("log", logger.info)
            logger.info(message)
            log_func(message)

            if check_status == "3":
                login_cookies = split_set_cookie(
                    check_response.headers.get("set-cookie", "")
                )
                is_login, login_cookie = await login_redirect(
                    check.redirect_url, login_cookies, crawler
                )
                return is_login, login_cookie
            elif check_status == "5":
                get_qrcode()
                break
            elif check_status is None:
                break

            await asyncio.sleep(5)

    async def login_redirect(redirect_url: str, login_cookies: str, crawler):
        """
        登录重定向，获取登录后Cookie

        Args:
            redirect_url (str): 重定向url
            login_cookies (str): 登录cookie

        Returns:
            is_login (bool): 是否成功登录
            login_cookie (str): 登录cookie
        """
        crawler.headers["Cookie"] = login_cookies
        redirect_response = await crawler.get_fetch_data(redirect_url)

        if redirect_response.history and len(redirect_response.history) > 1:
            logger.debug(f"login_redirect headers:{redirect_response.headers}")
            logger.debug(f"login_redirect history:{redirect_response.history}")
            logger.debug(
                f"login_redirect history[0] headers:{redirect_response.history[0].headers}"
            )
            logger.debug(
                f"login_redirect history[1] headers:{redirect_response.history[1].headers}"
            )
            # 获取重最后一个重定向里的Cookie
            login_cookie = split_set_cookie(
                redirect_response.history[1].headers.get("set-cookie", "")
            )
            logger.debug(f"login_cookie:{login_cookie}")
            return True, login_cookie
        else:
            logger.warning("[  登录  ]:自动重定向登录失败")
            if redirect_response:
                error_message = f"网络异常: 自动重定向登录失败。 状态码: {redirect_response.status_code}, 响应体: {redirect_response.text}"
            else:
                error_message = f"网络异常: 自动重定向登录失败。 无法连接到服务器。"
            logger.warning(error_message)
            return False, ""

    verify_fp = VerifyFpManager.gen_verify_fp()
    return await get_qrcode()


async def main(kwargs):
    mode = kwargs.get("mode")
    if mode in mode_function_map:
        await mode_function_map[mode](DouyinHandler(kwargs))
    else:
        logger.error(_("不存在该模式: {0}").format(mode))

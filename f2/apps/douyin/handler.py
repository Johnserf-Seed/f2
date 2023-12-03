# path: f2/apps/douyin/handler.py

# import time

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.utils.mode_handler import mode_handler, mode_function_map
from f2.apps.douyin.db import AsyncUserDB, AsyncVideoDB
from f2.apps.douyin.crawler import DouyinCrawler
from f2.apps.douyin.dl import DouyinDownloader
from f2.apps.douyin.model import (
    UserPost,
    UserProfile,
    UserLike,
    UserCollect,
    UserMix,
    PostDetail,
    UserLive,
)
from f2.apps.douyin.filter import (
    UserPostFilter,
    UserProfileFilter,
    UserCollectFilter,
    UserMixFilter,
    PostDetailFilter,
    UserLiveFilter,
)
from f2.apps.douyin.utils import SecUserIdFetcher, AwemeIdFetcher, WebCastIdFetcher
from f2.apps.douyin.utils import create_or_rename_user_folder
from f2.cli.cli_console import RichConsoleManager

downloader = DouyinDownloader()
rich_console = RichConsoleManager().rich_console
rich_prompt = RichConsoleManager().rich_prompt

# 需要忽略的字段（需过滤掉有时效性的字段）
ignore_fields = ["video_play_addr", "images", "video_bit_rate", "cover"]


async def handler_user_profile(sec_user_id: str) -> UserProfileFilter:
    """
    用于获取指定用户的个人信息
    (Used to get personal info of specified users)

    Args:
        sec_user_id: str: 用户ID (User ID)

    Return:
        user: UserProfileFilter: 用户信息过滤器 (User info filter)
    """
    async with DouyinCrawler() as crawler:
        params = UserProfile(sec_user_id=sec_user_id)
        response = await crawler.fetch_user_profile(params)
        user = UserProfileFilter(response)
        return user._to_dict()


async def get_user_nickname(sec_user_id: str, db: AsyncUserDB) -> str:
    """
    获取指定用户的昵称，如果不存在，则从服务器获取并存储到数据库中
    (Used to get personal info of specified users)

    Args:
        sec_user_id (str): 用户ID (User ID)
        db (AsyncUserDB): 用户数据库 (User database)

    Returns:
        user_nickname: (str): 用户昵称 (User nickname)
    """
    user_data = await db.get_user_info(sec_user_id)
    if not user_data:
        user_data = await handler_user_profile(sec_user_id)
        await db.add_user_info(**user_data)
    return user_data.get("nickname")


async def get_or_add_user_data(
    kwargs: dict, sec_user_id: str, db: AsyncUserDB
) -> tuple:
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
    current_user_data = await handler_user_profile(sec_user_id)

    # 获取当前用户最新昵称
    current_nickname = current_user_data.get("nickname")

    # 设置用户目录
    user_path = create_or_rename_user_folder(kwargs, local_user_data, current_nickname)

    # 如果用户不在数据库中，将其添加到数据库
    if not local_user_data:
        await db.add_user_info(**current_user_data)

    return user_path


async def get_or_add_video_data(
    aweme_data: dict, db: AsyncVideoDB, ignore_fields: list = None
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
    local_video_data = await db.get_video_info(aweme_data.get("aweme_id"))

    # 如果作品不在数据库中，将其添加到数据库
    if not local_video_data:
        # 从服务器获取当前作品最新数据
        # current_video_data = await fetch_one_video(aweme_data.get("aweme_id"))
        await db.add_video_info(ignore_fields=ignore_fields, **aweme_data)


@mode_handler("one")
async def handle_one_video(kwargs):
    """
    用于处理单个视频。
    (Used to process a single video.)

    Args:
        kwargs: dict: 参数字典 (Parameter dictionary)
    """
    aweme_id = await AwemeIdFetcher.get_aweme_id(kwargs.get("url"))

    aweme_data = await fetch_one_video(aweme_id)

    async with AsyncUserDB("douyin_users.db") as db:
        user_path = await get_or_add_user_data(
            kwargs, aweme_data.get("sec_user_id"), db
        )

    async with AsyncVideoDB("douyin_videos.db") as db:
        await get_or_add_video_data(aweme_data, db, ignore_fields)

    logger.debug(_("单个视频数据: {0}".format(aweme_data)))
    await downloader.create_download_tasks(kwargs, aweme_data, user_path)


async def fetch_one_video(aweme_id: str) -> dict:
    """
    用于获取单个视频。

    Args:
        aweme_id: str: 视频ID

    Return:
        video_data: dict: 视频数据字典，包含视频ID、视频文案、作者昵称
    """
    logger.debug(_("开始爬取视频: {0}").format(aweme_id))

    async with DouyinCrawler() as crawler:
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
async def handle_user_post(kwargs):
    """
    用于处理用户发布的视频。
    (Used to process videos published by users.)

    Args:
        kwargs: dict: 参数字典 (Parameter dictionary)
    """

    max_cursor = kwargs.get("max_cursor", 0)
    page_counts = kwargs.get("page_counts", 20)
    max_counts = kwargs.get("max_counts")

    # 获取用户数据并返回创建用户目录
    sec_user_id = await SecUserIdFetcher.get_sec_user_id(kwargs.get("url"))
    async with AsyncUserDB("douyin_users.db") as udb:
        user_path = await get_or_add_user_data(kwargs, sec_user_id, udb)

    # start_time = time.time()

    async for aweme_data_list in fetch_user_post_videos(
        sec_user_id, max_cursor, page_counts, max_counts
    ):
        # 创建下载任务
        await downloader.create_download_tasks(kwargs, aweme_data_list, user_path)

        # # 一次性批量插入视频数据到数据库
        # async with AsyncVideoDB("douyin_videos.db") as db:
        #     await db.batch_insert_videos(aweme_data_list, ignore_fields)

    # end_time = time.time()
    # print(f"总共执行时间: {end_time - start_time} 秒")


async def fetch_user_post_videos(
    sec_user_id: str, max_cursor: int = 0, page_counts: int = 20, max_counts: int = None
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

    async with DouyinCrawler() as crawler:
        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("=====================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(max_counts, current_request_size)
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

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
            logger.debug("=====================================")

            # 主页接口和作品详情的选择
            # await fetch_one_video(video.aweme_id)
            logger.debug(video)
            aweme_data_list = video._to_list()
            yield aweme_data_list

            # 更新已经处理的视频数量 (Update the number of videos processed)
            videos_collected += len(video.aweme_id)
            max_cursor = video.max_cursor

    logger.debug(_("爬取结束，共爬取{0}个视频").format(videos_collected))


@mode_handler("like")
async def handle_user_like(kwargs):
    """
    用于处理用户喜欢的视频 (Used to process videos liked by users)

    Args:
        kwargs: dict: 参数字典 (Parameter dictionary)
    """

    max_cursor = kwargs.get("max_cursor", 0)
    page_counts = kwargs.get("page_counts", 20)
    max_counts = kwargs.get("max_counts")

    # 获取用户数据并返回创建用户目录
    sec_user_id = await SecUserIdFetcher.get_sec_user_id(kwargs.get("url"))
    async with AsyncUserDB("douyin_users.db") as db:
        user_path = await get_or_add_user_data(kwargs, sec_user_id, db)

    async for aweme_data_list in fetch_user_like_videos(
        sec_user_id, max_cursor, page_counts, max_counts
    ):
        # 创建下载任务
        await downloader.create_download_tasks(kwargs, aweme_data_list, user_path)

        # async with AsyncVideoDB("douyin_videos.db") as db:
        #     for aweme_data in aweme_data_list:
        #         await get_or_add_video_data(aweme_data, db, ignore_fields)

        # # 一次性批量插入视频数据到数据库
        # async with AsyncVideoDB("douyin_videos.db") as db:
        #     await db.batch_insert_videos(aweme_data_list, ignore_fields)


async def fetch_user_like_videos(
    sec_user_id: str, max_cursor: int = 0, page_counts: int = 20, max_counts: int = None
) -> list:
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

    async with DouyinCrawler() as crawler:
        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("=====================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(max_counts, current_request_size)
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

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
            logger.debug("=====================================")

            aweme_data_list = video._to_list()
            yield aweme_data_list

            # 更新已经处理的视频数量 (Update the number of videos processed)
            videos_collected += len(aweme_data_list)
            max_cursor = video.max_cursor

    logger.debug(_("爬取结束，共爬取{0}个视频").format(videos_collected))


@mode_handler("collect")
async def handle_user_collect(kwargs):
    """
    用于处理用户收藏的视频 (Used to process videos collected by users)

    Args:
        kwargs: dict: 参数字典 (Parameter dictionary)
    """

    max_cursor = kwargs.get("max_cursor", 0)
    page_counts = kwargs.get("page_counts", 20)
    max_counts = kwargs.get("max_counts")

    sec_user_id = await SecUserIdFetcher.get_sec_user_id(kwargs.get("url"))

    async with AsyncUserDB("douyin_users.db") as db:
        user_path, user_data = await get_or_add_user_data(kwargs, sec_user_id, db)

    async for aweme_data_list in fetch_user_collect_videos(
        max_cursor, page_counts, max_counts
    ):
        await downloader.create_download_tasks(kwargs, aweme_data_list, user_path)


async def fetch_user_collect_videos(
    max_cursor: int = 0, page_counts: int = 20, max_counts: int = None
) -> list:
    """
    用于获取指定用户收藏的视频列表。
    (Used to get the list of videos collected by the specified user.)
    该接口需要用POST且只靠cookie来获取数据。
    (This interface needs to be POST and only relies on cookies to get data.)

    Args:
        max_cursor: int: 起始页 (Start page)
        page_counts: int: 每页视频数 (Number of videos per page)
        max_counts: int: 最大视频数 (Maximum number of videos)

    Return:
        aweme_data: dict: 视频数据字典, 包含视频ID列表、视频文案、作者昵称、起始页
        (Video data dictionary, including video ID list, video description,
        author nickname, start page)
    """

    max_counts = max_counts or float("inf")
    videos_collected = 0

    logger.debug(_("开始爬取用户收藏的视频"))

    async with DouyinCrawler() as crawler:
        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("=====================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(max_counts, current_request_size)
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

            params = UserCollect(cursor=max_cursor, count=current_request_size)
            response = await crawler.fetch_user_collect(params)
            video = UserCollectFilter(response)

            logger.debug(_("当前请求的max_cursor: {0}").format(max_cursor))
            logger.debug(
                _("视频ID: {0} 视频文案: {1} 作者: {2}").format(
                    video.aweme_id, video.desc, video.nickname
                )
            )
            logger.debug("=====================================")

            aweme_data_list = video._to_list()
            yield aweme_data_list

            if not video.has_more:
                logger.debug(_("用户收藏的视频采集完毕"))
                break

            # 更新已经处理的视频数量 (Update the number of videos processed)
            videos_collected += len(aweme_data_list)
            max_cursor = video.max_cursor


@mode_handler("mix")
async def handle_user_mix(kwargs):
    """
    用于处理用户合集的视频 (Used to process videos of users' collections)

    Args:
        kwargs: dict: 参数字典 (Parameter dictionary)
    """

    max_cursor = kwargs.get("max_cursor", 0)
    page_counts = kwargs.get("page_counts", 20)
    max_counts = kwargs.get("max_counts")

    aweme_id = await AwemeIdFetcher.get_aweme_id(kwargs.get("url"))
    mix_data = await fetch_one_video(aweme_id)
    sec_user_id = mix_data.get("sec_user_id")
    mix_id = mix_data.get("mix_id")

    async with AsyncUserDB("douyin_users.db") as db:
        user_path = await get_or_add_user_data(kwargs, sec_user_id, db)

    async for aweme_data_list in fetch_user_mix_videos(
        mix_id, max_cursor, page_counts, max_counts
    ):
        # 创建下载任务
        await downloader.create_download_tasks(kwargs, aweme_data_list, user_path)

    # async with AsyncVideoDB("douyin_videos.db") as db:
    #     for aweme_data in aweme_data_list:
    #         await get_or_add_video_data(aweme_data, db, ignore_fields)


async def fetch_user_mix_videos(
    mix_id: str, max_cursor: int = 0, page_counts: int = 20, max_counts: int = None
) -> list:
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

    async with DouyinCrawler() as crawler:
        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("=====================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(max_counts, current_request_size)
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

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
            logger.debug("=====================================")

            aweme_data_list = video._to_list()
            yield aweme_data_list

            # 更新已经处理的视频数量 (Update the number of videos processed)
            videos_collected += len(aweme_data_list)
            max_cursor = video.max_cursor

            if not video.has_more:
                logger.debug(_("合集: {0} 所有作品采集完毕").format(mix_id))
                break

    logger.debug(_("爬取结束，共爬取{0}个视频").format(videos_collected))


@mode_handler("live")
async def handle_user_live(kwargs):
    """
    用于处理用户直播 (Used to process user live)

    Args:
        kwargs: dict: 参数字典 (Parameter dictionary)
    """

    # 获取直播相关信息与主播信息
    webcast_id = await WebCastIdFetcher.get_webcast_id(kwargs.get("url"))

    # 然后下载直播推流
    webcast_data = await fetch_user_live_videos(webcast_id)
    sec_user_id = webcast_data.get("sec_user_id")

    async with AsyncUserDB("douyin_users.db") as db:
        user_path = await get_or_add_user_data(kwargs, sec_user_id, db)
    await downloader.create_stream_tasks(kwargs, webcast_data, user_path)


async def fetch_user_live_videos(webcast_id: str):
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

    async with DouyinCrawler() as crawler:
        logger.debug("=====================================")

        params = UserLive(web_rid=webcast_id, room_id_str="")
        response = await crawler.fetch_live(params)
        live = UserLiveFilter(response)

        logger.debug(
            _("直播ID: {0} 直播标题: {1} 直播状态: {2} 观看人数: {3}").format(
                live.room_id, live.live_title, live.live_status, live.user_count
            )
        )
        logger.debug(
            _("子分区: {0} 主播昵称: {1}").format(live.sub_partition_title, live.nickname)
        )
        logger.debug("=====================================")
        logger.debug(_("直播信息爬取结束"))

        webcast_data = live._to_dict()
        return webcast_data


@mode_handler("feed")
async def handle_user_feed(kwargs):
    """
    用于处理用户feed (Used to process user feed)

    Args:
        kwargs: dict: 参数字典 (Parameter dictionary)
    """

    max_cursor = kwargs.get("max_cursor", 0)
    page_counts = kwargs.get("page_counts", 20)
    max_counts = kwargs.get("max_counts")

    sec_user_id = await SecUserIdFetcher.get_sec_user_id(kwargs.get("url"))

    async with AsyncUserDB("douyin_users.db") as db:
        user_path = await get_or_add_user_data(kwargs, sec_user_id, db)

    async for aweme_data_list in fetch_user_feed_videos(
        sec_user_id, max_cursor, page_counts, max_counts
    ):
        # 创建下载任务
        await downloader.create_download_tasks(kwargs, aweme_data_list, user_path)


async def fetch_user_feed_videos(
    sec_user_id: str, max_cursor: int = 0, page_counts: int = 20, max_counts: int = None
) -> list:
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

    async with DouyinCrawler() as crawler:
        while videos_collected < max_counts:
            current_request_size = min(page_counts, max_counts - videos_collected)

            logger.debug("=====================================")
            logger.debug(
                _("最大数量: {0} 每次请求数量: {1}").format(max_counts, current_request_size)
            )
            logger.debug(_("开始爬取第 {0} 页").format(max_cursor))

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
            logger.debug("=====================================")

            aweme_data_list = video._to_list()
            yield aweme_data_list

            # 更新已经处理的视频数量 (Update the number of videos processed)
            videos_collected += len(video.aweme_id)
            max_cursor = video.max_cursor

    logger.debug(_("爬取结束，共爬取{0}个视频").format(videos_collected))


async def main(kwargs):
    mode = kwargs.get("mode")
    if mode in mode_function_map:
        await mode_function_map[mode](kwargs)
    else:
        logger.error(_("不存在该模式: {0}").format(mode))
        print(_("不存在该模式: {0}").format(mode))  # (The mode does not exist)

# path: f2/apps/twitter/handler.py

import asyncio

from pathlib import Path
from typing import AsyncGenerator, Union, Dict, Any, List

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.utils.decorators import mode_handler, mode_function_map
from f2.apps.bark.handler import BarkHandler
from f2.apps.bark.utils import ClientConfManager as BarkClientConfManager
from f2.apps.twitter.db import AsyncUserDB
from f2.apps.twitter.crawler import TwitterCrawler
from f2.apps.twitter.dl import TwitterDownloader
from f2.apps.twitter.model import (
    TweetDetailEncode,
    UserProfileEncode,
    PostTweetEncode,
    LikeTweetEncode,
    BookmarkTweetEncode,
)
from f2.apps.twitter.filter import (
    TweetDetailFilter,
    UserProfileFilter,
    PostTweetFilter,
    LikeTweetFilter,
    BookmarkTweetFilter,
)
from f2.apps.twitter.utils import (
    UniqueIdFetcher,
    TweetIdFetcher,
    create_or_rename_user_folder,
)
from f2.cli.cli_console import RichConsoleManager
from f2.exceptions.api_exceptions import APIResponseError
from f2.utils.utils import timestamp_2_str, get_timestamp

rich_console = RichConsoleManager().rich_console
rich_prompt = RichConsoleManager().rich_prompt


class TwitterHandler:

    def __init__(self, kwargs: dict = ...) -> None:
        self.kwargs = kwargs
        self.downloader = TwitterDownloader(kwargs)
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
        uniqueId: str,
    ) -> UserProfileFilter:
        """
        用于获取指定用户的个人信息
        (Used to get personal info of specified users)

        Args:
            uniqueId: str: 用户ID (User ID)

        Return:
            user: UserProfileFilter: 用户信息过滤器 (User info filter)
        """

        async with TwitterCrawler(self.kwargs) as crawler:
            params = UserProfileEncode(screen_name=uniqueId)
            response = await crawler.fetch_user_profile(params)
            user = UserProfileFilter(response)
            if user.nickname is None:
                raise APIResponseError(
                    _("`fetch_user_profile`请求失败，请更换cookie或稍后再试")
                )
            return UserProfileFilter(response)

    async def get_or_add_user_data(
        self,
        kwargs: dict,
        uniqueId: str,
        db: AsyncUserDB,
    ) -> Path:
        """
        获取或创建用户数据同时创建用户目录
        (Get or create user data and create user directory)

        Args:
            kwargs (dict): 配置参数 (Conf parameters)
            uniqueId (str): 用户ID (User ID)
            db (AsyncUserDB): 用户数据库 (User database)

        Returns:
            user_path (Path): 用户目录路径 (User directory path)
        """

        # 尝试从数据库中获取用户数据
        local_user_data = await db.get_user_info(uniqueId)

        # 从服务器获取当前用户最新数据
        current_user_data = await self.fetch_user_profile(uniqueId)

        # 获取当前用户最新昵称
        current_nickname = current_user_data.nickname

        # 设置用户目录
        user_path = create_or_rename_user_folder(
            kwargs, local_user_data, current_nickname
        )

        # 如果用户不在数据库中，将其添加到数据库
        if not local_user_data:
            await db.add_user_info(**current_user_data._to_dict())
            logger.debug(_("用户：{0} 已添加到数据库").format(current_nickname))

        return user_path

    @mode_handler("one")
    async def handle_one_tweet(self):
        """
        用于处理单个推文。
        (Used to process a single tweet.)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        tweet_id = await TweetIdFetcher.get_tweet_id(self.kwargs.get("url"))
        tweet_data = await self.fetch_one_tweet(tweet_id)

        async with AsyncUserDB("twitter_users.db") as db:
            user_path = await self.get_or_add_user_data(
                self.kwargs, tweet_data.user_unique_id, db
            )

        # async with AsynctweetDB("twitter_tweets.db") as db:
        #     await self.get_or_add_tweet_data(
        #         tweet_data._to_dict(), db, self.ignore_fields
        #     )

        # 创建下载任务
        await self.downloader.create_download_tasks(
            self.kwargs, tweet_data._to_dict(), user_path
        )

    async def fetch_one_tweet(
        self,
        tweet_id: str,
    ) -> TweetDetailFilter:
        """
        用于获取单个推文。

        Args:
            tweet_id: str: 推文ID

        Return:
            tweet: TweetDetailFilter: 单个推文数据过滤器
        """

        logger.info(_("开始爬取推文：{0}").format(tweet_id))
        async with TwitterCrawler(self.kwargs) as crawler:
            params = TweetDetailEncode(focalTweetId=tweet_id)
            response = await crawler.fetch_tweet_detail(params)
            tweet = TweetDetailFilter(response)

        logger.info(
            _("推文ID：{0} 文案：{1} 作者：{2} 阅读量：{3}").format(
                tweet.tweet_id,
                tweet.tweet_desc,
                tweet.nickname,
                tweet.tweet_views_count,
            )
        )

        await self._send_bark_notification(
            _("[Twitter] 单个推文下载"),
            _(
                "推文ID：{0}\n"
                "文案：{1}\n"
                "作者：{2}\n"
                "阅读量：{3}\n"
                "下载时间：{4}"
            ).format(
                tweet.tweet_id,
                (
                    tweet.tweet_desc_raw[:20] + "..."
                    if len(tweet.tweet_desc) > 20
                    else tweet.tweet_desc_raw
                ),
                tweet.nickname,
                tweet.tweet_views_count,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="Twitter",
        )

        return tweet

    @mode_handler("post")
    async def handle_post_tweet(self):
        """
        用于处理主页推文。
        (Used to process a post tweet.)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", "")
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        uniqueID = await UniqueIdFetcher.get_unique_id(self.kwargs.get("url"))
        user = await self.fetch_user_profile(uniqueID)

        async with AsyncUserDB("twitter_users.db") as udb:
            user_path = await self.get_or_add_user_data(self.kwargs, uniqueID, udb)

        async for tweet_list in self.fetch_post_tweet(
            user.user_rest_id, page_counts, max_cursor, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, tweet_list._to_list(), user_path
            )

    async def fetch_post_tweet(
        self,
        userId: str,
        page_counts: int = 20,
        max_cursor: str = "",
        max_counts: int = None,
    ) -> AsyncGenerator[PostTweetFilter, Any]:
        """
        用于获取用户发布的推文。

        Args:
            userId: str: 用户ID
            page_counts: int: 每次请求的推文数量
            max_cursor: str: 游标
            max_counts: int: 最大请求次数

        Return:
            tweet: PostTweetFilter: 用户发布的推文数据过滤器
        """

        max_counts = max_counts or float("inf")
        tweets_collected = 0

        logger.info(_("开始爬取用户：{0} 发布的推文").format(userId))

        while tweets_collected < max_counts:
            current_request_size = min(page_counts, max_counts - tweets_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            logger.info(
                _("开始爬取第 {0} 页").format("1" if max_cursor == "" else max_cursor)
            )

            async with TwitterCrawler(self.kwargs) as crawler:
                params = PostTweetEncode(
                    userId=userId, count=current_request_size, cursor=max_cursor
                )
                response = await crawler.fetch_post_tweet(params)
                tweet = PostTweetFilter(response)

            logger.debug(
                _("推文ID：{0} 文案：{1} 作者：{2}").format(
                    tweet.tweet_id, tweet.tweet_desc, tweet.nickname
                )
            )

            # 当cursorType值为Bottom且entryId长度为2时，表示已经爬取完所有的推文
            if tweet.cursorType == "Bottom" and len(tweet.entryId) == 2:
                logger.info(_("已处理完所有发布的推文"))
                break

            yield tweet

            # 防止最后一页不包含任何作品导致无法获取nickname_raw
            nickname_raw = tweet.nickname_raw[0]

            # 更新已经处理的推文数量 (Update the number of videos processed)
            tweets_collected += len(list(filter(None, tweet.tweet_id)))
            max_cursor = tweet.max_cursor

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(_("爬取结束，共爬取 {0} 个推文").format(tweets_collected))

        await self._send_bark_notification(
            _("[Twitter] 主页推文下载"),
            _("用户：{0}\n" "推文数：{1}\n" "下载时间：{2}").format(
                nickname_raw,
                tweets_collected,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="Twitter",
        )

    @mode_handler("like")
    async def handle_like_tweet(self):
        """
        用于处理喜欢推文。
        (Used to process like tweets.)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", "")
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        uniqueID = await UniqueIdFetcher.get_unique_id(self.kwargs.get("url"))
        user = await self.fetch_user_profile(uniqueID)

        async with AsyncUserDB("twitter_users.db") as udb:
            user_path = await self.get_or_add_user_data(self.kwargs, uniqueID, udb)

        async for tweet_list in self.fetch_like_tweet(
            user.user_rest_id, page_counts, max_cursor, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, tweet_list._to_list(), user_path
            )

    async def fetch_like_tweet(
        self,
        userId: str,
        page_counts: int = 20,
        max_cursor: str = "",
        max_counts: int = None,
    ) -> AsyncGenerator[LikeTweetFilter, Any]:
        """
        用于获取用户喜欢的推文。

        Args:
            userId: str: 用户ID
            page_counts: int: 每次请求的推文数量
            max_cursor: str: 游标
            max_counts: int: 最大请求次数

        Return:
            like: LikeTweetFilter: 用户喜欢的推文数据过滤器
        """

        max_counts = max_counts or float("inf")
        tweets_collected = 0

        logger.info(_("开始爬取用户：{0} 喜欢的推文").format(userId))

        while tweets_collected < max_counts:
            current_request_size = min(page_counts, max_counts - tweets_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            logger.info(
                _("开始爬取第 {0} 页").format("1" if max_cursor == "" else max_cursor)
            )

            async with TwitterCrawler(self.kwargs) as crawler:
                params = LikeTweetEncode(
                    userId=userId, count=current_request_size, cursor=max_cursor
                )
                response = await crawler.fetch_like_tweet(params)
                like = LikeTweetFilter(response)

            logger.debug(
                _("推文ID：{0} 推文文案：{1} 作者：{2}").format(
                    like.tweet_id, like.tweet_desc, like.nickname
                )
            )
            if like.max_cursor is None:
                logger.error(_("该用户没有公开喜欢的推文"))
                break

            # 当cursorType值为Bottom且entryId长度为2时，表示已经爬取完所有的推文
            if like.cursorType == "Bottom" and len(like.entryId) == 2:
                logger.info(_("已处理完所有喜欢的推文"))
                break

            yield like

            # 更新已经处理的推文数量 (Update the number of videos processed)
            tweets_collected += len(list(filter(None, like.tweet_id)))
            max_cursor = like.max_cursor

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(_("爬取结束，共爬取 {0} 个推文").format(tweets_collected))

        await self._send_bark_notification(
            _("[Twitter] 喜欢推文下载"),
            _("用户ID：{0}\n" "推文数：{1}\n" "下载时间：{2}").format(
                userId,
                tweets_collected,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="Twitter",
        )

    @mode_handler("bookmark")
    async def handle_bookmark_tweet(self):
        """
        用于处理收藏推文。
        (Used to process bookmark tweets.)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", "")
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        uniqueID = await UniqueIdFetcher.get_unique_id(self.kwargs.get("url"))

        async with AsyncUserDB("twitter_users.db") as udb:
            user_path = await self.get_or_add_user_data(self.kwargs, uniqueID, udb)

        async for tweet_list in self.fetch_bookmark_tweet(
            page_counts, max_cursor, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, tweet_list._to_list(), user_path
            )

    async def fetch_bookmark_tweet(
        self,
        page_counts: int = 20,
        max_cursor: str = "",
        max_counts: int = None,
    ) -> AsyncGenerator[LikeTweetFilter, Any]:
        """
        用于获取用户收藏的推文。

        Args:
            page_counts: int: 每次请求的推文数量
            max_cursor: str: 游标
            max_counts: int: 最大请求次数

        Return:
            like: LikeTweetFilter: 用户收藏的推文数据过滤器

        Note:
            不需要传入用户ID，提供Cookie即可
        """

        max_counts = max_counts or float("inf")
        tweets_collected = 0

        logger.info(_("开始爬取收藏的推文"))

        while tweets_collected < max_counts:
            current_request_size = min(page_counts, max_counts - tweets_collected)

            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            logger.info(
                _("开始爬取第 {0} 页").format("1" if max_cursor == "" else max_cursor)
            )

            async with TwitterCrawler(self.kwargs) as crawler:
                params = BookmarkTweetEncode(
                    count=current_request_size, cursor=max_cursor
                )
                response = await crawler.fetch_bookmark_tweet(params)
                bookmark = BookmarkTweetFilter(response)

            logger.debug(
                _("推文ID：{0} 推文文案：{1} 作者：{2}").format(
                    bookmark.tweet_id, bookmark.tweet_desc, bookmark.nickname
                )
            )

            if bookmark.max_cursor is None:
                logger.error(_("该用户没有收藏的推文"))
                break

            # 当cursorType值为Bottom且entryId长度为2时，表示已经爬取完所有的推文
            if bookmark.cursorType == "Bottom" and len(bookmark.entryId) == 2:
                logger.info(_("已处理完所有收藏的推文"))
                break

            yield bookmark

            # 更新已经处理的推文数量 (Update the number of videos processed)
            tweets_collected += len(list(filter(None, bookmark.tweet_id)))
            max_cursor = bookmark.max_cursor

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(_("爬取结束，共爬取 {0} 个推文").format(tweets_collected))

        await self._send_bark_notification(
            _("[Twitter] 收藏推文下载"),
            _("推文数：{0}\n" "下载时间：{1}").format(
                tweets_collected,
                timestamp_2_str(get_timestamp("sec")),
            ),
            group="Twitter",
        )


async def main(kwargs):
    mode = kwargs.get("mode")
    if mode in mode_function_map:
        await mode_function_map[mode](TwitterHandler(kwargs))
    else:
        logger.error(_("不存在该模式: {0}").format(mode))

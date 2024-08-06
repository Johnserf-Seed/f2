# path: f2/apps/twitter/handler.py

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Union, Dict, Any, List

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.utils.decorators import mode_handler, mode_function_map
from f2.utils.utils import split_set_cookie
from f2.apps.twitter.db import AsyncUserDB
from f2.apps.twitter.crawler import TwitterCrawler
from f2.apps.twitter.dl import TwitterDownloader
from f2.apps.twitter.model import (
    TweetDetailEncode,
    UserProfileEncode,
    PostTweetEncode,
)
from f2.apps.twitter.filter import (
    TweetDetailFilter,
    UserProfileFilter,
    PostTweetFilter,
    PostRetweetFilter,
)
from f2.apps.twitter.utils import (
    UserIdFetcher,
    TweetIdFetcher,
    create_or_rename_user_folder,
)
from f2.cli.cli_console import RichConsoleManager
from f2.exceptions.api_exceptions import APIResponseError

rich_console = RichConsoleManager().rich_console
rich_prompt = RichConsoleManager().rich_prompt


class TwitterHandler:

    def __init__(self, kwargs: dict = ...) -> None:
        self.kwargs = kwargs
        self.downloader = TwitterDownloader(kwargs)

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

        # logger.info(_("单个推文数据：{0}").format(tweet_data._to_dict()))

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
            _("推文ID：{0} 推文文案：{1} 作者：{2}").format(
                tweet.tweet_id, tweet.tweet_desc, tweet.nickname
            )
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

        uniqueID = await UserIdFetcher.get_user_id(self.kwargs.get("url"))
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

            logger.debug("===================================")
            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            logger.info(_("开始爬取第 {0} 页").format(max_cursor))

            async with TwitterCrawler(self.kwargs) as crawler:
                params = PostTweetEncode(
                    userId=userId, count=current_request_size, cursor=max_cursor
                )
                response = await crawler.fetch_post_tweet(params)
                tweet = PostTweetFilter(response)

            logger.debug(_("当前请求的max_cursor：{0}").format(max_cursor))
            logger.info(
                _("推文ID：{0} 推文文案：{1} 作者：{2}").format(
                    tweet.tweet_id, tweet.tweet_desc, tweet.nickname
                )
            )
            logger.info(tweet._to_dict())
            if len(tweet.tweet_id) == 0:
                # 只有tweet.tweet_id 和 tweet.tweet_desc都为None时，才认为已经爬取完毕
                # 且只有min_cursor与max_cursor 2个值时没有其他值时才认为到达底部
                if tweet.tweet_id is None and tweet.tweet_desc is None:
                    logger.info(
                        _("用户：{0} 所有发布的推文采集完毕").format(tweet.nickname)
                    )
                    break

                logger.info(_("max_cursor：{0} 未找到发布的推文").format(max_cursor))
                max_cursor = tweet.max_cursor
                await asyncio.sleep(self.kwargs.get("timeout", 5))
                continue

            yield tweet

            # 更新已经处理的作品数量 (Update the number of videos processed)
            tweets_collected += len(tweet.tweet_id)

            max_cursor = tweet.max_cursor
            logger.info(f"下一页{tweet.max_cursor}")

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(_("爬取结束，共爬取 {0} 个作品").format(tweets_collected))

    @mode_handler("retweet")
    async def handle_retweet(self):
        """
        用于处理转发推文。
        (Used to process retweet tweets.)

        Args:
            kwargs: dict: 参数字典 (Parameter dictionary)
        """

        max_cursor = self.kwargs.get("max_cursor", "")
        page_counts = self.kwargs.get("page_counts", 20)
        max_counts = self.kwargs.get("max_counts")

        uniqueID = await UserIdFetcher.get_user_id(self.kwargs.get("url"))
        user = await self.fetch_user_profile(uniqueID)

        async with AsyncUserDB("twitter_users.db") as udb:
            user_path = await self.get_or_add_user_data(self.kwargs, uniqueID, udb)

        async for tweet_list in self.fetch_retweet(
            user.user_rest_id, page_counts, max_cursor, max_counts
        ):
            # 创建下载任务
            await self.downloader.create_download_tasks(
                self.kwargs, tweet_list._to_list(), user_path
            )

    async def fetch_retweet(
        self,
        userId: str,
        page_counts: int = 20,
        max_cursor: str = "",
        max_counts: int = None,
    ) -> AsyncGenerator[PostTweetFilter, Any]:
        """
        用于获取用户转发的推文。

        Args:
            userId: str: 用户ID
            page_counts: int: 每次请求的推文数量
            max_cursor: str: 游标
            max_counts: int: 最大请求次数

        Return:
            tweet: PostTweetFilter: 用户转发的推文数据过滤器
        """

        max_counts = max_counts or float("inf")
        tweets_collected = 0

        logger.info(_("开始爬取用户：{0} 转发的推文").format(userId))

        while tweets_collected < max_counts:
            current_request_size = min(page_counts, max_counts - tweets_collected)

            logger.debug("===================================")
            logger.debug(
                _("最大数量：{0} 每次请求数量：{1}").format(
                    max_counts, current_request_size
                )
            )
            logger.info(_("开始爬取第 {0} 页").format(max_cursor))

            async with TwitterCrawler(self.kwargs) as crawler:
                params = PostTweetEncode(
                    userId=userId, count=current_request_size, cursor=max_cursor
                )
                response = await crawler.fetch_post_tweet(params)
                retweet = PostRetweetFilter(response)

            logger.debug(_("当前请求的max_cursor：{0}").format(max_cursor))
            # logger.info(
            #     _("推文ID：{0} 推文文案：{1} 作者：{2}").format(
            #         retweet.tweet_id, retweet.tweet_desc, retweet.nickname
            #     )
            # )
            logger.info(
                _("推文文案：{0} 推文图片：{1} 推文视频：{2}").format(
                    retweet.tweet_desc, retweet.tweet_media_url, retweet.tweet_video_url
                )
            )
            # logger.info(retweet._to_dict())
            if len(retweet.tweet_id) == 0:
                # 只有tweet.tweet_id 和 tweet.tweet_desc都为None时，才认为已经爬取完毕
                # 且只有min_cursor与max_cursor 2个值时没有其他值时才认为到达底部
                if retweet.tweet_id is None and retweet.tweet_desc is None:
                    logger.info(
                        _("用户：{0} 所有转发的推文采集完毕").format(retweet.nickname)
                    )
                    break

                logger.info(_("max_cursor：{0} 未找到转发的推文").format(max_cursor))
                max_cursor = retweet.max_cursor
                await asyncio.sleep(self.kwargs.get("timeout", 5))
                continue

            yield retweet

            # 更新已经处理的作品数量 (Update the number of videos processed)
            tweets_collected += len(retweet.tweet_id)

            max_cursor = retweet.max_cursor
            logger.info(f"下一页{retweet.max_cursor}")

            # 避免请求过于频繁
            logger.info(_("等待 {0} 秒后继续").format(self.kwargs.get("timeout", 5)))
            await asyncio.sleep(self.kwargs.get("timeout", 5))

        logger.info(_("爬取结束，共爬取 {0} 个作品").format(tweets_collected))


async def main(kwargs):
    mode = kwargs.get("mode")
    if mode in mode_function_map:
        await mode_function_map[mode](TwitterHandler(kwargs))
    else:
        logger.error(_("不存在该模式: {0}").format(mode))

# path: f2/apps/twitter/crawler.py

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.crawlers.base_crawler import BaseCrawler
from f2.apps.twitter.api import TwitterAPIEndpoints as xendpoints
from f2.apps.twitter.model import encode_model
from f2.apps.twitter.model import (
    TweetDetail,
    TweetDetailEncode,
    UserProfile,
    UserProfileEncode,
    PostTweet,
    PostTweetEncode,
    LikeTweet,
    LikeTweetEncode,
    BookmarkTweet,
    BookmarkTweetEncode,
)
from f2.apps.twitter.utils import ModelManager, ClientConfManager


class TwitterCrawler(BaseCrawler):
    def __init__(
        self,
        kwargs: dict = ...,
    ):
        # 需要与cli同步
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        self.authorization = (
            kwargs.get("Authorization") or ClientConfManager.authorization()
        )
        self.x_csrf_token = (
            kwargs.get("X-Csrf-Token") or ClientConfManager.x_csrf_token()
        )
        self.headers = kwargs.get("headers", {}) | {
            "Cookie": kwargs.get("cookie"),
            "Authorization": self.authorization,
            "X-Csrf-Token": self.x_csrf_token,
        }

        super().__init__(kwargs, proxies=proxies, crawler_headers=self.headers)

    async def fetch_tweet_detail(self, params: TweetDetailEncode):
        endpoint = ModelManager.model_2_endpoint(
            xendpoints.POST_DETAIL,
            TweetDetail(variables=encode_model(params)).model_dump(),
        )
        logger.debug(_("推文详情接口地址: {0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_profile(self, params: UserProfileEncode):
        endpoint = ModelManager.model_2_endpoint(
            xendpoints.USER_PROFILE,
            UserProfile(variables=encode_model(params)).model_dump(),
        )
        logger.debug(_("用户信息接口地址: {0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_tweet(self, params: PostTweetEncode):
        endpoint = ModelManager.model_2_endpoint(
            xendpoints.USER_POST,
            PostTweet(variables=encode_model(params)).model_dump(),
        )
        logger.debug(_("主页推文接口地址: {0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_like_tweet(self, params: LikeTweetEncode):
        endpoint = ModelManager.model_2_endpoint(
            xendpoints.USER_LIKE,
            LikeTweet(variables=encode_model(params)).model_dump(),
        )
        logger.debug(_("喜欢推文接口地址: {0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_bookmark_tweet(self, params: BookmarkTweetEncode):
        endpoint = ModelManager.model_2_endpoint(
            xendpoints.USER_BOOKMARK,
            BookmarkTweet(variables=encode_model(params)).model_dump(),
        )
        logger.debug(_("书签(收藏)推文接口地址: {0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

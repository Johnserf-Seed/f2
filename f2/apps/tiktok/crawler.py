# path: f2/apps/tiktok/crawler.py

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.crawlers.base_crawler import BaseCrawler
from f2.apps.tiktok.api import TiktokAPIEndpoints as tkendpoint
from f2.apps.tiktok.model import (
    UserProfile,
    UserPost,
    UserLike,
    UserMix,
    UserCollect,
    PostDetail,
    UserPlayList,
    PostComment,
    PostSearch,
    UserLive,
    CheckLiveAlive,
)
from f2.apps.tiktok.utils import XBogusManager


class TiktokCrawler(BaseCrawler):
    def __init__(
        self,
        kwargs: dict = ...,
    ):
        # 需要与cli同步
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        self.headers = kwargs.get("headers") | {"Cookie": kwargs["cookie"]}
        super().__init__(proxies=proxies, crawler_headers=self.headers)

    async def fetch_user_profile(self, params: UserProfile):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_DETAIL,
            params.model_dump(),
        )
        logger.debug(_("用户信息接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_post(self, params: UserPost):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_POST,
            params.model_dump(),
        )
        logger.debug(_("主页作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_like(self, params: UserLike):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_LIKE,
            params.model_dump(),
        )
        logger.debug(_("喜欢作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collect(self, params: UserCollect):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_COLLECT,
            params.model_dump(),
        )
        logger.debug(_("收藏作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_play_list(self, params: UserPlayList):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_PLAY_LIST,
            params.model_dump(),
        )
        logger.debug(_("合集列表接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_mix(self, params: UserMix):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_MIX,
            params.model_dump(),
        )
        logger.debug(_("合集作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_detail(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.AWEME_DETAIL,
            params.model_dump(),
        )
        logger.debug(_("作品详情接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_comment(self, params: PostComment):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.POST_COMMENT,
            params.model_dump(),
        )
        logger.debug(_("作品评论接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_recommend(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.HOME_RECOMMEND,
            params.model_dump(),
        )
        logger.debug(_("首页推荐接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_search(self, params: PostSearch):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.POST_SEARCH,
            params.model_dump(),
        )
        logger.debug(_("搜索作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_live(self, params: UserLive):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_LIVE,
            params.model_dump(),
        )
        logger.debug(_("用户直播接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_check_live_alive(self, params: CheckLiveAlive):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.CHECK_LIVE_ALIVE,
            params.model_dump(),
        )
        logger.debug(_("检查开播状态接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

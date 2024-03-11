# path: f2/apps/tiktok/crawler.py

import f2

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.utils.conf_manager import ConfigManager
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
)
from f2.apps.tiktok.utils import XBogusManager


class TiktokCrawler(BaseCrawler):
    def __init__(
        self,
        kwargs: dict = ...,
    ):
        f2_manager = ConfigManager(f2.F2_CONFIG_FILE_PATH)
        f2_conf = f2_manager.get_config("f2").get("tiktok")
        proxies_conf = kwargs.get("proxies", {"http": None, "https": None})
        proxies = {
            "http://": proxies_conf.get("http", None),
            "https://": proxies_conf.get("https", None),
        }

        self.headers = {
            "User-Agent": f2_conf["headers"]["User-Agent"],
            "Referer": f2_conf["headers"]["Referer"],
            "Cookie": kwargs["cookie"],
        }

        super().__init__(proxies=proxies, crawler_headers=self.headers)

    async def fetch_user_profile(self, params: UserProfile):
        endpoint = XBogusManager.model_2_endpoint(
            tkendpoint.USER_DETAIL, params.dict()
        )  # fmt: off
        logger.debug(_("用户信息接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_post(self, params: UserPost):
        endpoint = XBogusManager.model_2_endpoint(
            tkendpoint.USER_POST, params.dict()
        )  # fmt: off
        logger.debug(_("主页作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_like(self, params: UserLike):
        endpoint = XBogusManager.model_2_endpoint(
            tkendpoint.USER_LIKE, params.dict()
        )  # fmt: off
        logger.debug(_("喜欢作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collect(self, params: UserCollect):
        endpoint = XBogusManager.model_2_endpoint(
            tkendpoint.USER_COLLECT, params.dict()
        )
        logger.debug(_("收藏作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_play_list(self, params: UserPlayList):
        endpoint = XBogusManager.model_2_endpoint(
            tkendpoint.USER_PLAY_LIST, params.dict()
        )
        logger.debug(_("合辑列表接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_mix(self, params: UserMix):
        endpoint = XBogusManager.model_2_endpoint(
            tkendpoint.USER_MIX, params.dict()
        )  # fmt: off
        logger.debug(_("合辑作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_detail(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            tkendpoint.AWEME_DETAIL, params.dict()
        )
        logger.debug(_("作品详情接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_comment(self, params: PostComment):
        endpoint = XBogusManager.model_2_endpoint(
            tkendpoint.POST_COMMENT, params.dict()
        )
        logger.debug(_("作品评论接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_recommend(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            tkendpoint.HOME_RECOMMEND, params.dict()
        )
        logger.debug(_("首页推荐接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

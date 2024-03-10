# path: f2/apps/douyin/crawler.py

import f2

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.utils.conf_manager import ConfigManager
from f2.crawlers.base_crawler import BaseCrawler
from f2.apps.douyin.api import DouyinAPIEndpoints as dyendpoint
from f2.apps.douyin.model import (
    UserProfile,
    UserPost,
    UserLike,
    UserCollection,
    UserCollects,
    UserCollectsVideo,
    UserMusicCollection,
    PostDetail,
    UserMix,
    UserLive,
    UserLive2,
    FollowUserLive,
    LoginGetQr,
    LoginCheckQr,
)
from f2.apps.douyin.utils import XBogusManager


class DouyinCrawler(BaseCrawler):
    def __init__(self, kwargs: dict = {}):
        f2_manager = ConfigManager(f2.F2_CONFIG_FILE_PATH)
        f2_conf = f2_manager.get_config("f2").get("douyin")
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
            dyendpoint.USER_DETAIL, params.dict()
        )  # fmt: off
        logger.debug(_("用户信息接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_post(self, params: UserPost):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.USER_POST, params.dict()
        )  # fmt: off
        logger.debug(_("主页作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_like(self, params: UserLike):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.USER_FAVORITE_A, params.dict()
        )
        logger.debug(_("主页喜欢作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collection(self, params: UserCollection):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.USER_COLLECTION, params.dict()
        )
        logger.debug(_("主页收藏作品接口地址:" + endpoint))
        return await self._fetch_post_json(endpoint, params.dict())

    async def fetch_user_collects(self, params: UserCollects):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.USER_COLLECTS, params.dict()
        )
        logger.debug(_("收藏夹接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collects_video(self, params: UserCollectsVideo):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.USER_COLLECTS_VIDEO, params.dict()
        )
        logger.debug(_("收藏夹作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_music_collection(self, params: UserMusicCollection):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.USER_MUSIC_COLLECTION, params.dict()
        )
        logger.debug(_("音乐收藏接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_mix(self, params: UserMix):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.MIX_AWEME, params.dict()
        )  # fmt: off
        logger.debug(_("合集作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_detail(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.POST_DETAIL, params.dict()
        )  # fmt: off
        logger.debug(_("作品详情接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_comment(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.POST_COMMENT, params.dict()
        )
        logger.debug(_("作品评论接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_feed(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.TAB_FEED, params.dict()
        )  # fmt: off
        logger.debug(_("首页推荐作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_follow_feed(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.FOLLOW_FEED, params.dict()
        )  # fmt: off
        logger.debug(_("关注作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_friend_feed(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.FRIEND_FEED, params.dict()
        )  # fmt: off
        logger.debug(_("朋友作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_related(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.POST_RELATED, params.dict()
        )
        logger.debug(_("相关推荐作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_live(self, params: UserLive):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.LIVE_INFO, params.dict()
        )  # fmt: off
        logger.debug(_("直播接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_live_room_id(self, params: UserLive2):
        original_headers = self.aclient.headers.copy()
        try:
            # 避免invalid session
            self.aclient.headers.update({"Cookie": ""})
            endpoint = XBogusManager.model_2_endpoint(
                dyendpoint.LIVE_INFO_ROOM_ID, params.dict()
            )
            logger.debug(_("直播接口地址（room_id）:" + endpoint))
            return await self._fetch_get_json(endpoint)
        finally:
            self.aclient.headers = original_headers

    async def fetch_follow_live(self, params: FollowUserLive):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.FOLLOW_USER_LIVE, params.dict()
        )
        logger.debug(_("关注用户直播接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_locate_post(self, params: UserPost):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.LOCATE_POST, params.dict()
        )  # fmt: off
        logger.debug(_("定位上一次作品接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_login_qrcode(self, parms: LoginGetQr):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.SSO_LOGIN_GET_QR, parms.dict()
        )
        logger.debug(_("SSO获取二维码接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_check_qrcode(self, parms: LoginCheckQr):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.SSO_LOGIN_CHECK_QR, parms.dict()
        )
        logger.debug(_("SSO检查扫码状态接口地址:" + endpoint))
        return await self._fetch_response(endpoint)

    async def fetch_check_login(self, parms: LoginCheckQr):
        endpoint = XBogusManager.model_2_endpoint(
            dyendpoint.SSO_LOGIN_CHECK_LOGIN, parms.dict()
        )
        logger.debug(_("SSO检查登录状态接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

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
    UserCollect,
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
    app_manager = ConfigManager(f2.APP_CONFIG_FILE_PATH)
    douyin_conf = app_manager.get_config("douyin")

    max_retries = douyin_conf["max_retries"]
    max_connections = douyin_conf["max_connections"]
    timeout = douyin_conf["timeout"]
    max_tasks = douyin_conf["max_tasks"]
    proxies_conf = douyin_conf.get("proxies", None)
    proxies = {
        "http://": proxies_conf.get("http", None),
        "https://": proxies_conf.get("https", None),
    }

    def __init__(self, cli_params=None):
        self.crawler_headers = {
            "User-Agent": self.douyin_conf["headers"]["User-Agent"],
            "Referer": self.douyin_conf["headers"]["Referer"],
            "Cookie": self.douyin_conf["cookie"],
        }

        # 如果提供了命令行参数，并且其中有cookie参数，则更新cookie
        if cli_params and "cookie" in cli_params:
            self.crawler_headers["Cookie"] = cli_params["cookie"]

        if self.crawler_headers["Cookie"] is None:
            raise ValueError(
                _("Cookie不能为空。请提供有效的 Cookie 参数，或自动从浏览器获取 f2 -d dy --help，如扫码登录请保留双引号cookie: ""，再使用--sso-login命令。")
            )

        super().__init__(
            max_retries=self.max_retries,
            max_connections=self.max_connections,
            timeout=self.timeout,
            max_tasks=self.max_tasks,
            crawler_headers=self.crawler_headers,
            proxies=self.proxies,
        )

    async def fetch_user_profile(self, params: UserProfile):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.USER_DETAIL, params.dict()
        )
        logger.debug(_("用户信息接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_user_post(self, params: UserPost):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.USER_POST, params.dict()
        )
        logger.debug(_("主页作品接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_user_like(self, params: UserLike):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.USER_FAVORITE_A, params.dict()
        )
        logger.debug(_("喜欢作品接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_user_collect(self, params: UserCollect):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.USER_COLLECTION, params.dict()
        )
        logger.debug(_("收藏作品接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_user_mix(self, params: UserMix):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.MIX_AWEME, params.dict()
        )
        logger.debug(_("合集作品接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_post_detail(self, params: PostDetail):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.POST_DETAIL, params.dict()
        )
        logger.debug(_("作品详情接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_post_comment(self, params: PostDetail):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.POST_COMMENT, params.dict()
        )
        logger.debug(_("作品评论接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_post_feed(self, params: PostDetail):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.TAB_FEED, params.dict()
        )
        logger.debug(_("首页推荐作品接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_follow_feed(self, params: PostDetail):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.FOLLOW_FEED, params.dict()
        )
        logger.debug(_("关注作品接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_friend_feed(self, params: PostDetail):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.FRIEND_FEED, params.dict()
        )
        logger.debug(_("朋友作品接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_post_related(self, params: PostDetail):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.POST_RELATED, params.dict()
        )
        logger.debug(_("相关推荐作品接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_live(self, params: UserLive):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.LIVE_INFO, params.dict()
        )
        logger.debug(_("直播接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_live_room_id(self, params: UserLive2):
        original_headers = self.aclient.headers.copy()
        try:
            self.aclient.headers.update({"Cookie": ""})  # 避免invalid session
            endpoint = XBogusManager.to_complete_endpoint(
                dyendpoint.LIVE_INFO_ROOM_ID, params.dict()
            )
            logger.debug(_("直播接口地址（room_id）:" + endpoint))
            return await self._fetch_json(endpoint)
        finally:
            self.aclient.headers = original_headers

    async def fetch_follow_live(self, params: FollowUserLive):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.FOLLOW_USER_LIVE, params.dict()
        )
        logger.debug(_("关注用户直播接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_locate_post(self, params: UserPost):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.LOCATE_POST, params.dict()
        )
        logger.debug(_("定位上一次作品接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_login_qrcode(self, parms: LoginGetQr):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.SSO_LOGIN_GET_QR, parms.dict()
        )
        logger.debug(_("SSO获取二维码接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def fetch_check_qrcode(self, parms: LoginCheckQr):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.SSO_LOGIN_CHECK_QR, parms.dict()
        )
        logger.info(_("SSO检查扫码状态接口地址:" + endpoint))
        return await self._fetch_response(endpoint)

    async def fetch_check_login(self, parms: LoginCheckQr):
        endpoint = XBogusManager.to_complete_endpoint(
            dyendpoint.SSO_LOGIN_CHECK_LOGIN, parms.dict()
        )
        logger.debug(_("SSO检查登录状态接口地址:" + endpoint))
        return await self._fetch_json(endpoint)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

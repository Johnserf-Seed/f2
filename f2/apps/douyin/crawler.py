# path: f2/apps/douyin/crawler.py

from f2.log.logger import logger
from f2.i18n.translator import _
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
    UserFollowing,
    UserFollower,
)
from f2.apps.douyin.utils import XBogusManager, ClientConfManager


class DouyinCrawler(BaseCrawler):
    def __init__(
        self,
        kwargs: dict = ...,
    ):
        # 需要与cli同步
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})

        self.user_agent = ClientConfManager.user_agent()
        self.referrer = ClientConfManager.referer()
        self.headers = {
            "User-Agent": self.user_agent,
            "Referer": self.referrer,
            "Cookie": kwargs["cookie"],
        }

        super().__init__(proxies=proxies, crawler_headers=self.headers)

    async def fetch_user_profile(self, params: UserProfile):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_DETAIL,
            params.model_dump(),
        )
        logger.debug(_("用户信息接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_post(self, params: UserPost):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_POST,
            params.model_dump(),
        )
        logger.debug(_("主页作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_like(self, params: UserLike):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_FAVORITE_A,
            params.model_dump(),
        )
        logger.debug(_("主页喜欢作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collection(self, params: UserCollection):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_COLLECTION,
            params.model_dump(),
        )
        logger.debug(_("主页收藏作品接口地址：{0}").format(endpoint))
        return await self._fetch_post_json(endpoint, params.model_dump())

    async def fetch_user_collects(self, params: UserCollects):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_COLLECTS,
            params.model_dump(),
        )
        logger.debug(_("收藏夹接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collects_video(self, params: UserCollectsVideo):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_COLLECTS_VIDEO,
            params.model_dump(),
        )
        logger.debug(_("收藏夹作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_music_collection(self, params: UserMusicCollection):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_MUSIC_COLLECTION,
            params.model_dump(),
        )
        logger.debug(_("音乐收藏接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_mix(self, params: UserMix):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.MIX_AWEME,
            params.model_dump(),
        )
        logger.debug(_("合集作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_detail(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.POST_DETAIL,
            params.model_dump(),
        )
        logger.debug(_("作品详情接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_comment(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.POST_COMMENT,
            params.model_dump(),
        )
        logger.debug(_("作品评论接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_feed(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.TAB_FEED,
            params.model_dump(),
        )
        logger.debug(_("首页推荐作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_follow_feed(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.FOLLOW_FEED,
            params.model_dump(),
        )
        logger.debug(_("关注作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_friend_feed(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.FRIEND_FEED,
            params.model_dump(),
        )
        logger.debug(_("朋友作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_related(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.POST_RELATED,
            params.model_dump(),
        )
        logger.debug(_("相关推荐作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_live(self, params: UserLive):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.LIVE_INFO,
            params.model_dump(),
        )
        logger.debug(_("直播接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_live_room_id(self, params: UserLive2):
        original_headers = self.aclient.headers.copy()
        try:
            # 避免invalid session
            self.aclient.headers.update({"Cookie": ""})
            endpoint = XBogusManager.model_2_endpoint(
                self.headers.get("User-Agent"),
                dyendpoint.LIVE_INFO_ROOM_ID,
                params.model_dump(),
            )
            logger.debug(_("直播接口地址（room_id）：{0}").format(endpoint))
            return await self._fetch_get_json(endpoint)
        finally:
            self.aclient.headers = original_headers

    async def fetch_follow_live(self, params: FollowUserLive):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.FOLLOW_USER_LIVE,
            params.model_dump(),
        )
        logger.debug(_("关注用户直播接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_locate_post(self, params: UserPost):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.LOCATE_POST,
            params.model_dump(),
        )
        logger.debug(_("定位上一次作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_login_qrcode(self, parms: LoginGetQr):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.SSO_LOGIN_GET_QR,
            parms.model_dump(),
        )
        logger.debug(_("SSO获取二维码接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_check_qrcode(self, parms: LoginCheckQr):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.SSO_LOGIN_CHECK_QR,
            parms.model_dump(),
        )
        logger.debug(_("SSO检查扫码状态接口地址：{0}").format(endpoint))
        return await self._fetch_response(endpoint)

    async def fetch_check_login(self, parms: LoginCheckQr):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.SSO_LOGIN_CHECK_LOGIN,
            parms.model_dump(),
        )
        logger.debug(_("SSO检查登录状态接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_following(self, params: UserFollowing):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_FOLLOWING,
            params.model_dump(),
        )
        logger.debug(_("用户关注列表接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_follower(self, params: UserFollower):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_FOLLOWER,
            params.model_dump(),
        )
        logger.debug(_("用户粉丝列表接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

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
    app_manager = ConfigManager(f2.APP_CONFIG_FILE_PATH)
    tiktok_conf = app_manager.get_config("tiktok")

    max_retries = tiktok_conf["max_retries"]
    max_connections = tiktok_conf["max_connections"]
    timeout = tiktok_conf["timeout"]
    max_tasks = tiktok_conf["max_tasks"]
    proxies_conf = tiktok_conf.get("proxies", None)
    proxies = {
        "http://": proxies_conf.get("http", None),
        "https://": proxies_conf.get("https", None),
    }

    def __init__(self, cli_params=None):
        if self.tiktok_conf["cookie"] is None:
            raise ValueError(
                _("Cookie不能为空。请提供有效的 Cookie 参数，或使用自动从浏览器获取  f2 -d tk --help")
            )

        self.crawler_headers = {
            "User-Agent": self.tiktok_conf["headers"]["User-Agent"],
            "Referer": self.tiktok_conf["headers"]["Referer"],
            "Cookie": self.tiktok_conf["cookie"],
        }

        # 如果提供了命令行参数，并且其中有cookie参数，则更新cookie
        if cli_params and "cookie" in cli_params:
            self.crawler_headers["Cookie"] = cli_params["cookie"]

        super().__init__(
            max_retries=self.max_retries,
            max_connections=self.max_connections,
            timeout=self.timeout,
            max_tasks=self.max_tasks,
            proxies=self.proxies,
            crawler_headers=self.crawler_headers,
        )

    async def fetch_user_profile(self, params: UserProfile):
        endpoint = XBogusManager.to_complete_endpoint(
            tkendpoint.USER_DETAIL, params.dict()
        )
        logger.debug(_("用户信息接口地址:" + endpoint))
        return await self._fetch(endpoint)

    async def fetch_user_post(self, params: UserPost):
        endpoint = XBogusManager.to_complete_endpoint(
            tkendpoint.USER_POST, params.dict()
        )
        logger.debug(_("主页作品接口地址:" + endpoint))
        return await self._fetch(endpoint)

    async def fetch_user_like(self, params: UserLike):
        endpoint = XBogusManager.to_complete_endpoint(
            tkendpoint.USER_LIKE, params.dict()
        )
        logger.debug(_("喜欢作品接口地址:" + endpoint))
        return await self._fetch(endpoint)

    async def fetch_user_collect(self, params: UserCollect):
        endpoint = XBogusManager.to_complete_endpoint(
            tkendpoint.USER_COLLECT, params.dict()
        )
        logger.debug(_("收藏作品接口地址:" + endpoint))
        return await self._fetch(endpoint)

    async def fetch_user_play_list(self, params: UserPlayList):
        endpoint = XBogusManager.to_complete_endpoint(
            tkendpoint.USER_PLAY_LIST, params.dict()
        )
        logger.debug(_("合辑列表接口地址:" + endpoint))
        return await self._fetch(endpoint)

    async def fetch_user_mix(self, params: UserMix):
        endpoint = XBogusManager.to_complete_endpoint(
            tkendpoint.USER_MIX, params.dict()
        )
        logger.debug(_("合辑作品接口地址:" + endpoint))
        return await self._fetch(endpoint)

    async def fetch_post_detail(self, params: PostDetail):
        endpoint = XBogusManager.to_complete_endpoint(
            tkendpoint.AWEME_DETAIL, params.dict()
        )
        logger.debug(_("作品详情接口地址:" + endpoint))
        return await self._fetch(endpoint)

    async def fetch_post_comment(self, params: PostComment):
        endpoint = XBogusManager.to_complete_endpoint(
            tkendpoint.POST_COMMENT, params.dict()
        )
        logger.debug(_("作品评论接口地址:" + endpoint))
        return await self._fetch(endpoint)

    async def fetch_post_recommend(self, params: PostDetail):
        endpoint = XBogusManager.to_complete_endpoint(
            tkendpoint.HOME_RECOMMEND, params.dict()
        )
        logger.debug(_("首页推荐接口地址:" + endpoint))
        return await self._fetch(endpoint)

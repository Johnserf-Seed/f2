# path: f2/apps/weibo/crawler.py

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.crawlers.base_crawler import BaseCrawler
from f2.apps.weibo.api import WeiboAPIEndpoints as wbendpoint
from f2.apps.weibo.model import (
    UserInfo,
    UserDetail,
    UserWeibo,
    WeiboDetail,
)
from f2.apps.weibo.utils import ModelManager


class WeiboCrawler(BaseCrawler):
    def __init__(
        self,
        kwargs: dict = ...,
    ):
        # 需要与cli同步
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        self.headers = kwargs.get("headers", {}) | {"Cookie": kwargs["cookie"]}
        super().__init__(kwargs, proxies=proxies, crawler_headers=self.headers)

    async def fetch_user_info(self, params: UserInfo):
        endpoint = ModelManager.model_2_endpoint(
            wbendpoint.USER_INFO, params.model_dump()
        )
        logger.debug(_("用户信息接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_detail(self, params: UserDetail):
        endpoint = ModelManager.model_2_endpoint(
            wbendpoint.USER_DETAIL, params.model_dump()
        )
        logger.debug(_("用户详情接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_weibo(self, params: UserWeibo):
        endpoint = ModelManager.model_2_endpoint(
            wbendpoint.USER_WEIBO, params.model_dump()
        )
        logger.debug(_("用户微博接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_weibo_detail(self, params: WeiboDetail):
        endpoint = ModelManager.model_2_endpoint(
            wbendpoint.WeiboDetail, params.model_dump()
        )
        logger.debug(_("单条微博接口地址:" + endpoint))
        return await self._fetch_get_json(endpoint)

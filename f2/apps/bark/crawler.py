# path: f2/apps/bark/crawler.py

from typing import Dict

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.crawlers.base_crawler import BaseCrawler
from f2.utils.utils import BaseEndpointManager
from f2.apps.bark.model import BarkModel
from f2.apps.bark.api import BarkAPIEndpoints as bkendpoint
from f2.apps.bark.utils import ClientConfManager


class BarkCrawler(BaseCrawler):
    def __init__(
        self,
        kwargs: Dict = ...,
    ):
        # 需要与cli同步
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        token = kwargs.get("token", "")
        self.server_endpoint = f"{bkendpoint.BARK_DOMAIN}/{token}"
        if ClientConfManager.encryption().get("enable"):
            self.encryption = ClientConfManager.encryption()
        super().__init__(
            kwargs, proxies=proxies, crawler_headers=kwargs.get("headers", {})
        )

    async def fetch_bark_notification(self, params: BarkModel) -> Dict:
        endpoint = BaseEndpointManager.model_2_endpoint(
            self.server_endpoint,
            params.model_dump(by_alias=True),
        )
        logger.debug(_("Bark 通知接口地址(GET)：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def post_bark_notification(self, params: BarkModel) -> Dict:
        endpoint = BaseEndpointManager.model_2_endpoint(
            self.server_endpoint,
            params.model_dump(by_alias=True),
        )
        logger.debug(_("Bark 通知接口地址(POST)：{0}").format(endpoint))
        return await self._fetch_post_json(endpoint, params.model_dump())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

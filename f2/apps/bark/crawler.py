# path: f2/apps/bark/crawler.py

from typing import Dict
from urllib.parse import quote

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.crawlers.base_crawler import BaseCrawler
from f2.utils.utils import BaseEndpointManager
from f2.apps.bark.model import BarkModel, BarkCipherModel
from f2.apps.bark.api import BarkAPIEndpoints as bkendpoint


class BarkCrawler(BaseCrawler):
    def __init__(
        self,
        kwargs: Dict = ...,
    ):
        # 需要与cli同步
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        api_key = kwargs.get("key", "")
        self.server_endpoint = f"{bkendpoint.BARK_DOMAIN}/{api_key}"
        super().__init__(
            kwargs, proxies=proxies, crawler_headers=kwargs.get("headers", {})
        )

    async def fetch_bark_notification(self, params: BarkModel) -> Dict:
        # 转义参数
        escaped_params = {
            k: quote(str(v), safe="")
            for k, v in params.model_dump(by_alias=True).items()
        }
        endpoint = BaseEndpointManager.model_2_endpoint(
            self.server_endpoint,
            escaped_params,
        )
        logger.debug(_("Bark 通知接口地址(GET)：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def post_bark_notification(self, params: BarkModel) -> Dict:
        logger.debug(_("Bark 通知接口地址(POST)：{0}").format(self.server_endpoint))
        return await self._fetch_post_json(
            self.server_endpoint, params.model_dump(by_alias=True)
        )

    async def cipher_bark_notification(self, params: BarkCipherModel) -> Dict:
        logger.debug(_("Bark 通知接口地址(Cipher)：{0}").format(self.server_endpoint))
        return await self._fetch_post_json(self.server_endpoint, params.model_dump())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

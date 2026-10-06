# path: tests/test_empty_ids.py

import httpx
import pytest

from f2.apps.douyin.utils import AwemeIdFetcher as DouyinAwemeIdFetcher
from f2.apps.douyin.utils import SecUserIdFetcher as DouyinSecUserIdFetcher
from f2.apps.douyin.utils import WebCastIdFetcher
from f2.apps.tiktok.utils import AwemeIdFetcher as TiktokAwemeIdFetcher
from f2.apps.tiktok.utils import SecUserIdFetcher as TiktokSecUserIdFetcher
from f2.apps.twitter.utils import TweetIdFetcher
from f2.apps.weibo.handler import WeiboHandler
from f2.apps.weibo.utils import WeiboScreenNameFetcher, WeiboUidFetcher
from f2.exceptions.api_exceptions import APINotFoundError
from f2.exceptions.base import F2Error


@pytest.fixture(autouse=True)
def no_redirect(monkeypatch):
    """请求链接时原样返回，不发出真实请求"""

    async def get(self, url, **kwargs):
        return httpx.Response(200, text="", request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)


@pytest.mark.parametrize(
    "fetch, url",
    [
        (DouyinSecUserIdFetcher.get_sec_user_id, "https://www.douyin.com/user/"),
        (DouyinSecUserIdFetcher.get_sec_user_id, "https://www.douyin.com/user/?a=1"),
        (DouyinAwemeIdFetcher.get_aweme_id, "https://www.douyin.com/video/"),
        (WebCastIdFetcher.get_webcast_id, "https://www.douyin.com/follow/live/"),
        (TiktokSecUserIdFetcher.get_uniqueid, "https://www.tiktok.com/@"),
        (TiktokAwemeIdFetcher.get_aweme_id, "https://www.tiktok.com/@a/video/"),
    ],
)
async def test_links_without_id_are_rejected(fetch, url):
    # 此前正则允许匹配空串，得到空的 ID，随后在请求前抛出普通的 ValueError，
    # 命令行打印完整堆栈（如 f2 dy -M post -u https://www.douyin.com/user/）
    with pytest.raises(F2Error):
        await fetch(url)


async def test_vid_does_not_include_other_parameters():
    # 失效作品会跳转到带 vid 参数的地址，此前会把 & 之后的参数也截进作品 ID
    url = "https://www.douyin.com/?vid=7123456789012345678&from=share"

    assert await DouyinAwemeIdFetcher.get_aweme_id(url) == "7123456789012345678"


async def test_tweet_link_without_id_is_rejected():
    # 此前报错时读取只在 t.co 短链分支中赋值的 response，抛出 UnboundLocalError
    with pytest.raises(F2Error):
        await TweetIdFetcher.get_tweet_id("https://x.com/a/status/")


async def test_weibo_link_without_user_is_rejected(monkeypatch):
    # 此前两种方式都取不到用户时抛出 ValueError，命令行打印完整堆栈
    async def not_found(cls, url):
        raise APINotFoundError("not found")

    monkeypatch.setattr(WeiboUidFetcher, "get_weibo_uid", classmethod(not_found))
    monkeypatch.setattr(
        WeiboScreenNameFetcher, "get_weibo_screen_name", classmethod(not_found)
    )
    handler = WeiboHandler({"headers": {"User-Agent": "f2-test"}, "cookie": "a=b"})

    with pytest.raises(F2Error):
        await handler.extract_weibo_uid("https://weibo.com/u/")

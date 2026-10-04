# path: tests/test_close_clients.py

import httpx
import pytest

import f2.apps.douyin.handler as douyin_handler
import f2.apps.douyin.utils as douyin_utils
import f2.apps.tiktok.handler as tiktok_handler
import f2.apps.tiktok.utils as tiktok_utils
import f2.apps.twitter.handler as twitter_handler
import f2.apps.twitter.utils as twitter_utils
import f2.apps.weibo.handler as weibo_handler
import f2.apps.weibo.utils as weibo_utils
from f2.apps.douyin.dl import DouyinDownloader
from f2.crawlers.base_crawler import BaseCrawler

KWARGS = {
    "cookie": "a=b",
    "headers": {"User-Agent": "f2-test"},
    "proxies": {"http://": None, "https://": None},
}


def refuse(self, url, *args, **kwargs):
    raise httpx.ConnectError("refused", request=httpx.Request("GET", url))


async def arefuse(self, url, *args, **kwargs):
    refuse(self, url)


@pytest.fixture
def closed(monkeypatch):
    """记录关闭的客户端；所有请求都以连接失败结束"""
    calls = []
    close = BaseCrawler.close

    async def record(self):
        calls.append(type(self).__name__)
        await close(self)

    def record_sync(self):
        calls.append("httpx.Client")

    monkeypatch.setattr(BaseCrawler, "close", record)
    monkeypatch.setattr(httpx.Client, "close", record_sync)
    for method in ("get", "post"):
        monkeypatch.setattr(httpx.AsyncClient, method, arefuse)
        monkeypatch.setattr(httpx.Client, method, refuse)
    return calls


ASYNC_CALLS = [
    (douyin_utils.SecUserIdFetcher.get_sec_user_id, "https://www.douyin.com/user/x"),
    (douyin_utils.AwemeIdFetcher.get_aweme_id, "https://v.douyin.com/iRNBho6u/"),
    (douyin_utils.MixIdFetcher.get_mix_id, "https://v.douyin.com/iRNBho6u/"),
    (douyin_utils.WebCastIdFetcher.get_webcast_id, "https://v.douyin.com/iRNBho6u/"),
    (douyin_utils.WebCastIdFetcher.get_room_id, "https://v.douyin.com/iRNBho6u/"),
    (tiktok_utils.SecUserIdFetcher.get_secuid, "https://www.tiktok.com/@nasa"),
    (tiktok_utils.SecUserIdFetcher.get_uniqueid, "https://vm.tiktok.com/ZMabc/"),
    (tiktok_utils.AwemeIdFetcher.get_aweme_id, "https://vm.tiktok.com/ZMabc/"),
    (twitter_utils.UniqueIdFetcher.get_unique_id, "https://x.com/i/flow/login"),
    (twitter_utils.TweetIdFetcher.get_tweet_id, "https://t.co/abc"),
    (tiktok_utils.DeviceIdManager.gen_device_id, None),
    (weibo_utils.VisitorManager.gen_visitor, None),
]


def call_id(call):
    return f"{call.__module__.split('.')[2]}.{call.__qualname__}"


@pytest.mark.parametrize(
    "call, url", ASYNC_CALLS, ids=[call_id(call) for call, _ in ASYNC_CALLS]
)
async def test_async_helpers_close_their_client(closed, call, url):
    # 此前每次调用新建的客户端都不关闭，连接要等事件循环关闭后才被回收
    with pytest.raises(Exception):
        await (call(url) if url else call())

    assert len(closed) == 1


SYNC_CALLS = [
    douyin_utils.TokenManager.gen_real_msToken,
    douyin_utils.TokenManager.gen_ttwid,
    douyin_utils.TokenManager.gen_webid,
    tiktok_utils.TokenManager.gen_real_msToken,
    tiktok_utils.TokenManager.gen_ttwid,
    tiktok_utils.TokenManager.gen_odin_tt,
]


@pytest.mark.parametrize("call", SYNC_CALLS, ids=call_id)
def test_token_managers_close_their_client(closed, call):
    try:
        call()
    except Exception:
        pass

    assert closed == ["httpx.Client"]


async def test_tiktok_secuid_closes_the_client_after_success(monkeypatch, closed):
    html = (
        '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
        '{"__DEFAULT_SCOPE__":{"webapp.user-detail":{"userInfo":{"user":'
        '{"secUid":"MS4wLjABAAAA-nasa"}}}}}</script>'
    )

    async def get(self, url, **kwargs):
        return httpx.Response(200, text=html, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)

    assert (
        await tiktok_utils.SecUserIdFetcher.get_secuid("https://www.tiktok.com/@nasa")
        == "MS4wLjABAAAA-nasa"
    )
    assert closed == ["SecUserIdFetcher"]


# ---------------- 各应用的 main 关闭下载器 ----------------


@pytest.mark.parametrize(
    "module",
    [douyin_handler, tiktok_handler, twitter_handler, weibo_handler],
    ids=lambda m: m.__name__.split(".")[2],
)
@pytest.mark.parametrize("fails", [False, True], ids=["done", "error"])
async def test_main_closes_the_downloader(monkeypatch, module, fails):
    clients = []

    async def run(handler):
        # 下载时才会创建下载器的客户端
        clients.append(handler.downloader.aclient)
        if fails:
            raise RuntimeError("download failed")

    monkeypatch.setattr(module, "get_mode_handlers", lambda name: {"post": run})

    if fails:
        with pytest.raises(RuntimeError):
            await module.main(KWARGS | {"mode": "post"})
    else:
        await module.main(KWARGS | {"mode": "post"})

    assert clients[0].is_closed


async def test_closing_a_downloader_does_not_create_clients():
    downloader = DouyinDownloader(KWARGS)

    await downloader.close()

    assert downloader._client is None and downloader._aclient is None

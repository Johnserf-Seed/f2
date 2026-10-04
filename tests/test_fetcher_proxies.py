# path: tests/test_fetcher_proxies.py

import json

import httpx
import pytest
from httpx_socks import AsyncProxyTransport

import f2.apps.douyin.handler as douyin_handler
import f2.apps.douyin.utils as douyin_utils
import f2.apps.tiktok.handler as tiktok_handler
import f2.apps.tiktok.utils as tiktok_utils
import f2.apps.twitter.handler as twitter_handler
import f2.apps.twitter.utils as twitter_utils

SOCKS = {"type": "socks5", "host": "127.0.0.1", "port": 1080}
NO_PROXY = {"http://": None, "https://": None}
FETCHERS = [
    douyin_utils.SecUserIdFetcher,
    douyin_utils.AwemeIdFetcher,
    douyin_utils.MixIdFetcher,
    douyin_utils.WebCastIdFetcher,
    tiktok_utils.SecUserIdFetcher,
    tiktok_utils.AwemeIdFetcher,
    twitter_utils.UniqueIdFetcher,
    twitter_utils.TweetIdFetcher,
]


def fetcher_id(fetcher):
    return f"{fetcher.__module__.split('.')[2]}.{fetcher.__name__}"


@pytest.mark.parametrize("fetcher", FETCHERS, ids=fetcher_id)
def test_fetcher_uses_the_callers_proxy(fetcher):
    # 此前只用客户端配置中的代理，应用配置与 --proxies 中的代理不生效
    assert fetcher(SOCKS)._get_proxy_config() == "socks5://127.0.0.1:1080"


@pytest.mark.parametrize("fetcher", FETCHERS, ids=fetcher_id)
@pytest.mark.parametrize("proxies", [None, NO_PROXY], ids=["none", "empty"])
def test_fetcher_falls_back_to_the_client_config(monkeypatch, fetcher, proxies):
    monkeypatch.setattr(fetcher, "proxies", {"http://": "http://10.0.0.1:3128"})

    assert fetcher(proxies)._get_proxy_config() == "http://10.0.0.1:3128"


async def test_tiktok_secuid_request_goes_through_the_proxy(monkeypatch):
    # 只在 F2 中配置了代理、没有系统代理时，获取 sec_uid 此前直连 tiktok.com
    data = {"__DEFAULT_SCOPE__": {"webapp.user-detail": {"userInfo": {"user": {}}}}}
    data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]["user"] = {
        "secUid": "MS4wLjABAAAA-nasa"
    }
    html = (
        '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
        f"{json.dumps(data)}</script>"
    )
    transports = []

    async def get(self, url, **kwargs):
        transports.append(self._transport_for_url(httpx.URL(url)))
        return httpx.Response(200, text=html, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)

    sec_uid = await tiktok_utils.SecUserIdFetcher.get_secuid(
        "https://www.tiktok.com/@nasa", proxies=SOCKS
    )

    assert sec_uid == "MS4wLjABAAAA-nasa"
    assert isinstance(transports[0], AsyncProxyTransport)


class Stop(Exception):
    pass


def recorder(calls):
    async def fetch(url, proxies=None):
        calls.append(proxies)
        raise Stop

    return fetch


@pytest.mark.parametrize(
    "module, handler_class, fetcher, method, handle, url",
    [
        (
            douyin_handler,
            "DouyinHandler",
            "SecUserIdFetcher",
            "get_sec_user_id",
            "handle_user_post",
            "https://www.douyin.com/user/x",
        ),
        (
            douyin_handler,
            "DouyinHandler",
            "AwemeIdFetcher",
            "get_aweme_id",
            "handle_one_video",
            "https://www.douyin.com/video/1",
        ),
        (
            tiktok_handler,
            "TiktokHandler",
            "SecUserIdFetcher",
            "get_secuid",
            "handle_user_post",
            "https://www.tiktok.com/@x",
        ),
        (
            twitter_handler,
            "TwitterHandler",
            "UniqueIdFetcher",
            "get_unique_id",
            "handle_post_tweet",
            "https://x.com/x",
        ),
    ],
    ids=["douyin-post", "douyin-one", "tiktok-post", "twitter-post"],
)
async def test_handlers_pass_their_proxies(
    monkeypatch, module, handler_class, fetcher, method, handle, url
):
    calls = []
    monkeypatch.setattr(getattr(module, fetcher), method, recorder(calls))
    kwargs = {
        "cookie": "a=b",
        "headers": {"User-Agent": "f2-test"},
        "proxies": SOCKS,
        "url": url,
    }

    with pytest.raises(Stop):
        await getattr(getattr(module, handler_class)(kwargs), handle)()

    assert calls == [SOCKS]

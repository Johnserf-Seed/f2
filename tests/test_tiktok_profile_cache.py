# path: tests/test_tiktok_profile_cache.py

import json

import httpx
import pytest

from f2.apps.tiktok import handler as tiktok_handler
from f2.apps.tiktok.utils import SecUserIdFetcher

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.tiktok.com/"},
    "cookie": "",
    "proxies": {"http://": None, "https://": None},
}
DETAIL = {
    "statusCode": 0,
    "userInfo": {
        "user": {"secUid": "MS4wLjABAAAA-nasa", "uniqueId": "nasa", "nickname": "NASA"},
        "stats": {"videoCount": 7, "followerCount": 100},
    },
}


@pytest.fixture(autouse=True)
def empty_cache(monkeypatch):
    monkeypatch.setattr(SecUserIdFetcher, "_user_details", {})


@pytest.fixture
def profile_page(monkeypatch):
    html = (
        '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
        + json.dumps({"__DEFAULT_SCOPE__": {"webapp.user-detail": DETAIL}})
        + "</script>"
    )

    async def get(self, url, **kwargs):
        return httpx.Response(200, text=html, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)


class NoApiCrawler:
    def __init__(self, kwargs=None):
        raise AssertionError("主页中已有用户信息时不应再请求用户信息接口")


async def test_profile_comes_from_the_profile_page(profile_page, monkeypatch):
    # 用户信息接口对游客与空 cookie 只返回空内容，主页、合集等模式此前在这一步就失败
    sec_uid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@nasa")
    monkeypatch.setattr(tiktok_handler, "TiktokCrawler", NoApiCrawler)

    user = await tiktok_handler.TiktokHandler(dict(KWARGS)).fetch_user_profile(
        secUid=sec_uid
    )

    assert (user.uniqueId, user.nickname, user.videoCount) == ("nasa", "NASA", 7)


async def test_cached_profile_expires(profile_page, monkeypatch):
    sec_uid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@nasa")
    assert SecUserIdFetcher.cached_user_detail(sec_uid) == DETAIL

    seen_at = SecUserIdFetcher._user_details[sec_uid][0]
    monkeypatch.setattr(
        tiktok_handler.SecUserIdFetcher,
        "_user_details",
        {sec_uid: (seen_at - SecUserIdFetcher._USER_DETAIL_TTL - 1, DETAIL)},
    )

    assert SecUserIdFetcher.cached_user_detail(sec_uid) is None

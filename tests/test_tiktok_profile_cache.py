# path: tests/test_tiktok_profile_cache.py

import json

import httpx
import pytest

from f2.apps.tiktok import handler as tiktok_handler
from f2.apps.tiktok.utils import SecUserIdFetcher
from f2.exceptions.api_exceptions import APINotFoundError

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


async def test_missing_user_is_explained(monkeypatch):
    # 账号不存在或被封禁时主页仍返回 200，此前只报 ValueError: 获取 sec_uid 失败
    html = (
        '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
        + json.dumps(
            {"__DEFAULT_SCOPE__": {"webapp.user-detail": {"statusCode": 10221}}}
        )
        + "</script>"
    )

    async def get(self, url, **kwargs):
        return httpx.Response(200, text=html, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)

    with pytest.raises(APINotFoundError, match="10221"):
        await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@gone")


class PostsCrawler:
    """主页作品接口返回一条作品，用户信息接口不应被调用"""

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def fetch_user_post(self, params):
        user = DETAIL["userInfo"]["user"]
        stats = DETAIL["userInfo"]["stats"]
        return {"itemList": [{"id": "1", "author": user, "authorStats": stats}]}

    async def fetch_user_profile(self, params):
        raise AssertionError("作品中已有作者信息时不应再请求用户信息接口")


async def test_profile_comes_from_posts_for_user_links(monkeypatch):
    # /user/<secUid> 链接不会打开主页，此前只能请求对游客返回空内容的用户信息接口
    monkeypatch.setattr(tiktok_handler, "TiktokCrawler", PostsCrawler)
    monkeypatch.setattr(tiktok_handler, "UserPost", dict)
    handler = tiktok_handler.TiktokHandler(dict(KWARGS))

    user = await handler.fetch_user_profile(secUid="MS4wLjABAAAA-nasa")

    assert (user.uniqueId, user.videoCount) == ("nasa", 7)
    assert SecUserIdFetcher.cached_user_detail("MS4wLjABAAAA-nasa") is not None


async def test_profile_by_unique_id_comes_from_the_profile_page(
    profile_page, monkeypatch
):
    # 直播、单个作品模式只有 uniqueId，此前直接请求对游客返回空内容的用户信息接口
    monkeypatch.setattr(tiktok_handler, "TiktokCrawler", NoApiCrawler)
    handler = tiktok_handler.TiktokHandler(dict(KWARGS))

    user = await handler.fetch_user_profile(uniqueId="nasa")

    assert (user.uniqueId, user.secUid, user.nickname) == (
        "nasa",
        "MS4wLjABAAAA-nasa",
        "NASA",
    )

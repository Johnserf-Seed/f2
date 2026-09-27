# path: tests/test_twitter_unique_id.py

import httpx
import pytest

from f2.apps.twitter.utils import UniqueIdFetcher
from f2.exceptions.api_exceptions import APIResponseError


def mock_x(monkeypatch, handler):
    monkeypatch.setattr(
        UniqueIdFetcher,
        "_create_mount",
        lambda self, async_mode=False: {"all://": httpx.MockTransport(handler)},
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://x.com/CaroylnG61544",
        "https://x.com/CaroylnG61544/followers",
        "https://www.twitter.com/CaroylnG61544/?lang=en",
        "https://x.com/@CaroylnG61544",
        "https://twitter.com/CaroylnG61544/status/1440000000000000000/photo/1",
    ],
)
async def test_username_in_link_is_used_without_request(monkeypatch, url):
    # 未登录时 x.com 会把用户页面跳转到 /i/flow/login，此前因此得到用户名 i
    def handler(request):
        raise AssertionError("不应发出请求")

    mock_x(monkeypatch, handler)
    assert await UniqueIdFetcher.get_unique_id(url) == "CaroylnG61544"


async def test_short_link_redirected_to_login_keeps_the_username(monkeypatch):
    def handler(request):
        if request.url.host == "t.co":
            return httpx.Response(
                301, headers={"Location": "https://x.com/CaroylnG61544"}
            )
        if request.url.path == "/CaroylnG61544":
            login = "https://x.com/i/flow/login?redirect_after_login=%2FCaroylnG61544"
            return httpx.Response(302, headers={"Location": login})
        return httpx.Response(200, text="login")

    mock_x(monkeypatch, handler)
    assert await UniqueIdFetcher.get_unique_id("https://t.co/abc123") == "CaroylnG61544"


async def test_reserved_path_is_not_a_username(monkeypatch):
    mock_x(monkeypatch, lambda request: httpx.Response(200, text="home"))
    with pytest.raises(APIResponseError):
        await UniqueIdFetcher.get_unique_id("https://x.com/home")

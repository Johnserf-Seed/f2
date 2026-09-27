# path: tests/test_tiktok_token_cookies.py

import httpx
import pytest

from f2.apps.tiktok.utils import TokenManager
from f2.exceptions.api_exceptions import APIResponseError


def mock_tiktok(monkeypatch, handler):
    monkeypatch.setattr(
        TokenManager,
        "_create_mount",
        lambda self, async_mode=False: {"all://": httpx.MockTransport(handler)},
    )


def test_gen_ttwid_reads_the_homepage_cookie(monkeypatch):
    sent = []

    def handler(request):
        sent.append(request)
        cookies = [
            ("set-cookie", "ttwid=1%7Cabc; Path=/"),
            ("set-cookie", "tt_csrf_token=x"),
        ]
        return httpx.Response(200, headers=cookies, text="<html></html>")

    mock_tiktok(monkeypatch, handler)
    assert TokenManager.gen_ttwid() == "1%7Cabc"
    # 此前请求 ttwid/check：它现在只做校验，不再下发 ttwid
    [request] = sent
    assert request.method == "GET" and str(request.url) == "https://www.tiktok.com/"
    assert "cookie" not in request.headers


def test_gen_ttwid_without_cookie_raises(monkeypatch):
    mock_tiktok(monkeypatch, lambda request: httpx.Response(200, text="<html></html>"))
    with pytest.raises(APIResponseError):
        TokenManager.gen_ttwid()


def test_gen_odin_tt_follows_redirect_and_explains_missing_cookie(monkeypatch):
    paths = []

    def handler(request):
        paths.append(request.url.path)
        if not request.url.path.endswith("/"):
            return httpx.Response(301, headers={"Location": request.url.path + "/"})
        return httpx.Response(200, json={"data": {}})

    mock_tiktok(monkeypatch, handler)
    # 游客 cookie 里已没有 odin_tt，报错要说明原因
    with pytest.raises(APIResponseError, match="odin_tt"):
        TokenManager.gen_odin_tt()
    assert paths == ["/passport/web/auth/config", "/passport/web/auth/config/"]


def test_gen_odin_tt_returns_the_cookie_when_issued(monkeypatch):
    mock_tiktok(
        monkeypatch,
        lambda request: httpx.Response(
            200, headers={"set-cookie": "odin_tt=abc"}, json={}
        ),
    )
    assert TokenManager.gen_odin_tt() == "abc"

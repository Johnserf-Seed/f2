# path: tests/test_douyin_live_room_cookie.py

import types

import httpx
import pytest

from f2.apps.douyin import handler as douyin_handler
from f2.apps.douyin.crawler import DouyinCrawler
from f2.exceptions.api_exceptions import APIResponseError

LOGIN_COOKIE = "sessionid=login-session; ttwid=abc"

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.douyin.com/"},
    "cookie": LOGIN_COOKIE,
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
}

ROOM = {
    "status_code": 0,
    "data": {
        "room": {
            "id": "7311111111111111111",
            "title": "直播间标题",
            "status": 2,
            "user_count": 10,
            "owner": {"web_rid": "123456", "nickname": "主播"},
            "stream_url": {"resolution_name": {"FULL_HD1": "蓝光"}},
        }
    },
}


async def test_room_id_api_is_requested_without_login_cookie():
    # 带登录 cookie 时这个接口返回 status_code 101 与空数据（#367）。此前只清空了客户端的默认
    # 请求头，而每次请求都会带上 crawler_headers，登录 cookie 仍然被发出去
    cookies = []

    def respond(request):
        cookies.append(request.headers.get("cookie"))
        return httpx.Response(200, json=ROOM)

    crawler = DouyinCrawler(dict(KWARGS))
    crawler._aclient = httpx.AsyncClient(
        transport=httpx.MockTransport(respond), headers=crawler.crawler_headers
    )
    params = types.SimpleNamespace(model_dump=lambda: {"room_id": "1"})

    async with crawler:
        assert await crawler.fetch_live_room_id(params) == ROOM
        # 其他接口照常带上配置的 cookie
        await crawler._fetch_get_json("https://live.douyin.com/webcast/other/")

    assert cookies == ["", LOGIN_COOKIE]
    assert crawler.crawler_headers["Cookie"] == LOGIN_COOKIE


class RoomCrawler:
    response: dict = {}

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def fetch_live_room_id(self, params):
        return type(self).response


@pytest.fixture
def handler(monkeypatch):
    # 请求参数模型构造时会联网获取 msToken，换成普通对象
    monkeypatch.setattr(douyin_handler, "UserLive2", types.SimpleNamespace)
    handler = douyin_handler.DouyinHandler(dict(KWARGS))

    return handler


def use_response(monkeypatch, response):
    crawler = type("Crawler", (RoomCrawler,), {"response": response})
    monkeypatch.setattr(douyin_handler, "DouyinCrawler", crawler)


async def test_missing_room_data_raises_api_error(handler, monkeypatch):
    # 此前在截取直播标题时抛出 TypeError: object of type 'NoneType' has no len()
    use_response(monkeypatch, {"status_code": 101, "data": {}})

    with pytest.raises(APIResponseError) as exc_info:
        await handler.fetch_user_live_videos_by_room_id("7311111111111111111")

    assert "101" in str(exc_info.value)


async def test_room_data_is_returned(handler, monkeypatch):
    use_response(monkeypatch, ROOM)

    live = await handler.fetch_user_live_videos_by_room_id("7311111111111111111")

    assert live.web_rid == "123456"
    assert live.live_status == 2

# path: tests/test_douyin_query_user.py

import logging
import types

import pytest

from f2.apps.douyin import handler as douyin_handler

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.douyin.com/"},
    "cookie": "ttwid=abc",
    "proxies": {"http://": None, "https://": None},
}


def use_response(monkeypatch, response):
    class QueryUserCrawler:
        def __init__(self, kwargs=None):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def fetch_query_user(self, params):
            return response

    monkeypatch.setattr(douyin_handler, "DouyinCrawler", QueryUserCrawler)
    # 请求参数模型构造时会联网获取 msToken，换成普通对象
    monkeypatch.setattr(douyin_handler, "QueryUser", types.SimpleNamespace)


def f2_warnings(caplog):
    return [
        r for r in caplog.records if r.name == "f2" and r.levelno == logging.WARNING
    ]


@pytest.mark.parametrize(
    "response, warned",
    [
        # 现在的接口成功时返回 status_code 0，此前被误报为“请提供正确的ttwid”
        ({"status_code": 0, "id": "1", "user_uid": "2", "create_time": 1}, False),
        # 旧版接口成功时不返回 status_code
        ({"id": "1", "user_uid": "2", "create_time": 1}, False),
        ({"status_code": 8, "status_msg": "login expired"}, True),
    ],
)
async def test_query_user_status(monkeypatch, caplog, response, warned):
    use_response(monkeypatch, response)
    handler = douyin_handler.DouyinHandler(dict(KWARGS))

    with caplog.at_level(logging.INFO):
        user = await handler.fetch_query_user()

    assert user.status_code == response.get("status_code")
    assert bool(f2_warnings(caplog)) is warned

# path: tests/test_weibo_one_mode.py

import logging

import pytest

from f2.apps.weibo import handler as weibo_handler
from f2.apps.weibo.utils import extract_desc

# 博主设置为不可见时接口的实际响应
HIDDEN = {"ok": 0, "message": "由于博主设置，目前内容暂不可见。", "error_code": 20170}


@pytest.fixture
def hidden_weibo(monkeypatch):
    class FakeCrawler:
        def __init__(self, kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def fetch_weibo_detail(self, params):
            return dict(HIDDEN)

    async def weibo_id(url):
        return "PaTOZxRJ4"

    monkeypatch.setattr(weibo_handler, "WeiboCrawler", FakeCrawler)
    monkeypatch.setattr(weibo_handler.WeiboIdFetcher, "get_weibo_id", weibo_id)
    handler = weibo_handler.WeiboHandler(
        {
            "headers": {"User-Agent": "f2-test"},
            "cookie": "SUB=guest",
            "url": "https://weibo.com/1839167003/PaTOZxRJ4",
        }
    )
    return handler


async def test_fetch_hidden_weibo_returns_the_reason(hidden_weibo):
    # 此前读取文案时报 AttributeError: 'NoneType' object has no attribute 'strip'
    weibo = await hidden_weibo.fetch_one_weibo("PaTOZxRJ4")

    assert (weibo.status, weibo.error_code) == (0, 20170)
    assert weibo.message == HIDDEN["message"]


async def test_one_mode_reports_why_the_weibo_is_hidden(
    hidden_weibo, monkeypatch, caplog
):
    async def no_user(*args, **kwargs):
        raise AssertionError("微博不可见时不应建立用户目录")

    monkeypatch.setattr(hidden_weibo, "get_or_add_user_data", no_user)

    with caplog.at_level(logging.ERROR):
        await hidden_weibo.handle_one_weibo()

    errors = [r.getMessage() for r in caplog.records if r.levelno == logging.ERROR]
    assert any(HIDDEN["message"] in m and "20170" in m for m in errors)


@pytest.mark.parametrize("text", [None, ""])
def test_extract_desc_without_text(text):
    assert extract_desc(text) == ""

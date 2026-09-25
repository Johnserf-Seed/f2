# path: tests/test_douyin_live_cookie.py

import uuid

import pytest

from f2.apps.douyin import handler as douyin_handler
from f2.apps.douyin.utils import TokenManager
from f2.utils.http.cookie import parse_cookie_str

GUEST_COOKIE = (
    "ttwid=guest; __live_version__=%221.1.4.7838%22; live_use_vvc=%22false%22;"
)


def test_gen_secsdk_uid_is_random_uuid4():
    values = {TokenManager.gen_secsdk_uid() for _ in range(20)}
    assert len(values) == 20
    assert all(uuid.UUID(value).version == 4 for value in values)


@pytest.mark.parametrize("cookie", [None, "", "ttwid=guest", GUEST_COOKIE])
def test_ensure_secsdk_uid_adds_missing_field(cookie):
    fields = parse_cookie_str(TokenManager.ensure_secsdk_uid(cookie))
    assert uuid.UUID(fields["x-web-secsdk-uid"]).version == 4
    # 原有字段保持不变
    for name, value in parse_cookie_str(cookie or "").items():
        assert fields[name] == value


def test_ensure_secsdk_uid_keeps_existing_value():
    cookie = "ttwid=guest; x-web-secsdk-uid=from-browser"
    assert TokenManager.ensure_secsdk_uid(cookie) == cookie


async def test_fetch_live_im_sends_secsdk_uid(monkeypatch):
    # #412：弹幕初始化接口缺少 x-web-secsdk-uid 时返回空内容
    seen = {}

    class FakeCrawler:
        def __init__(self, kwargs):
            seen["cookie"] = kwargs["cookie"]

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def fetch_live_im_fetch(self, params):
            return {}

    monkeypatch.setattr(douyin_handler, "DouyinCrawler", FakeCrawler)
    kwargs = {"cookie": GUEST_COOKIE, "headers": {"User-Agent": "f2-test"}}
    await douyin_handler.DouyinHandler(kwargs).fetch_live_im(room_id="1", unique_id="2")

    fields = parse_cookie_str(seen["cookie"])
    assert "x-web-secsdk-uid" in fields
    assert fields["ttwid"] == "guest"
    # 不修改调用方传入的 kwargs
    assert kwargs["cookie"] == GUEST_COOKIE

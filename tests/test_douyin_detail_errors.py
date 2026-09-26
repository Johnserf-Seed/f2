# path: tests/test_douyin_detail_errors.py

from types import SimpleNamespace

import pytest

from f2.apps.douyin import handler as douyin_handler
from f2.exceptions import APIResponseError

AWEME_ID = "7446700850673749305"
KWARGS = {"cookie": "a=b", "headers": {"User-Agent": "f2-test"}}


def use_response(monkeypatch, response):
    class FakeCrawler:
        def __init__(self, kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def fetch_post_detail(self, params):
            return response

    monkeypatch.setattr(douyin_handler, "DouyinCrawler", FakeCrawler)
    # 请求模型在构造时会联网获取 msToken，这里换成替身
    monkeypatch.setattr(
        douyin_handler, "PostDetail", lambda **kwargs: SimpleNamespace(**kwargs)
    )


async def test_removed_work_reports_reason(monkeypatch):
    # #214 中的作品已被设为私密，此前提示的是“接口正在维护中”
    use_response(
        monkeypatch,
        {
            "aweme_detail": None,
            "status_code": 0,
            "filter_detail": {
                "aweme_id": AWEME_ID,
                "detail_msg": "因作品权限或已被删除，无法观看，去看看其他作品吧",
                "filter_reason": "status_self_see",
            },
        },
    )
    with pytest.raises(APIResponseError) as exc_info:
        await douyin_handler.DouyinHandler(KWARGS).fetch_one_video(AWEME_ID)
    message = str(exc_info.value)
    assert AWEME_ID in message
    assert "因作品权限或已被删除" in message


@pytest.mark.parametrize(
    "response", [{"aweme_detail": None, "status_code": 0}, {"filter_detail": {}}]
)
async def test_unexplained_empty_response_keeps_generic_message(monkeypatch, response):
    use_response(monkeypatch, response)
    with pytest.raises(APIResponseError, match="fetch_one_video"):
        await douyin_handler.DouyinHandler(KWARGS).fetch_one_video(AWEME_ID)

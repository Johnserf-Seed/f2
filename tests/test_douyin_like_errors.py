# path: tests/test_douyin_like_errors.py

import types

import pytest

from f2.apps.douyin import handler as douyin_handler
from f2.exceptions.api_exceptions import APIRetryExhaustedError

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.douyin.com/"},
    "cookie": "ttwid=guest",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
}


class EmptyLikeCrawler:
    """点赞列表不公开时接口一直返回空内容，基类重试用尽后抛出 APIRetryExhaustedError"""

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def fetch_user_like(self, params):
        raise APIRetryExhaustedError("获取端点数据失败，重试次数达到上限")


async def test_empty_like_list_explains_the_likely_cause(monkeypatch):
    monkeypatch.setattr(douyin_handler, "DouyinCrawler", EmptyLikeCrawler)
    # 请求参数模型构造时会联网获取 msToken，换成普通对象
    monkeypatch.setattr(douyin_handler, "UserLike", types.SimpleNamespace)
    handler = douyin_handler.DouyinHandler(dict(KWARGS))

    with pytest.raises(APIRetryExhaustedError) as exc_info:
        async for _ in handler.fetch_user_like_videos("sec-uid", 0, 20, None):
            pass

    # 新的提示带上用户，原来的异常保留在异常链里
    assert "sec-uid" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, APIRetryExhaustedError)

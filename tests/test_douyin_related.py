# path: tests/test_douyin_related.py

import asyncio
import types
from urllib.parse import unquote

import pytest

from f2.apps.douyin import handler as douyin_handler

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.douyin.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
}
SEED = "7000000000000000000"
POOL = [str(7100000000000000000 + i) for i in range(100)]


class RelatedCrawler:
    """
    与实测一致的相关推荐接口：每页返回推荐池里最靠前、且不在 filterGids 中的 10 个作品，
    has_more 总是为真。filterGids 不带之前各页的作品时，这些作品会再次出现。
    """

    calls: list = []
    pool: list = POOL

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def fetch_post_related(self, params):
        excluded = set(unquote(params.filterGids).split(","))
        type(self).calls.append(excluded)
        items = [gid for gid in type(self).pool if gid not in excluded][:10]
        return {
            "status_code": 0,
            "has_more": 1,
            "aweme_list": [{"aweme_id": gid} for gid in items],
        }


@pytest.fixture
def handler(monkeypatch):
    # 请求参数模型构造时会联网获取 msToken，换成普通对象
    monkeypatch.setattr(douyin_handler, "PostRelated", types.SimpleNamespace)
    monkeypatch.setattr(douyin_handler, "DouyinCrawler", RelatedCrawler)
    RelatedCrawler.calls = []
    RelatedCrawler.pool = POOL
    handler = douyin_handler.DouyinHandler(dict(KWARGS))

    return handler


async def collect(handler, max_counts):
    ids = []

    async def run():
        async for page in handler.fetch_related_videos(SEED, "", 20, max_counts):
            ids.extend(str(gid) for gid in page.aweme_id)

    # 此前接口一直有 has_more 时会无限请求，这里限时
    await asyncio.wait_for(run(), 5)
    return ids


async def test_related_pages_do_not_repeat(handler):
    # 此前 filterGids 每页只带上一页的作品 ID，实测从第 3 页起大部分作品与前面重复，
    # 重复的也计入 --max-counts
    ids = await collect(handler, 50)

    assert ids == POOL[:50]
    # 每次请求都排除当前作品与之前出现过的全部作品
    for page, excluded in enumerate(RelatedCrawler.calls):
        assert SEED in excluded
        assert set(POOL[: page * 10]) <= excluded


async def test_related_stops_when_nothing_new(handler):
    # 推荐池用完后接口仍是 has_more，此前没有 --max-counts 时会无限请求
    RelatedCrawler.pool = POOL[:25]

    ids = await collect(handler, None)

    assert ids == POOL[:25]
    assert len(RelatedCrawler.calls) == 4

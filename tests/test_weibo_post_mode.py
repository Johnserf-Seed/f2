# path: tests/test_weibo_post_mode.py

from f2.apps.weibo import handler as weibo_handler

UID = "2265830070"


def weibo(idstr, created_at="Mon Jan 01 12:00:00 +0800 2024", **extra):
    return {
        "idstr": idstr,
        "mblogid": f"M{idstr}",
        "created_at": created_at,
        "text_raw": f"微博 {idstr}",
        "user": {"idstr": UID, "screen_name": "测试用户"},
        **extra,
    }


def page(weibos, since_id="next", total=100):
    return {"ok": 1, "data": {"since_id": since_id, "list": weibos, "total": total}}


def use_pages(monkeypatch, pages):
    """WeiboCrawler 按页码返回准备好的响应，返回记录请求页码的列表"""
    requested = []

    class FakeCrawler:
        def __init__(self, kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def fetch_user_weibo(self, params):
            requested.append(params.page)
            return pages[params.page - 1]

    monkeypatch.setattr(weibo_handler, "WeiboCrawler", FakeCrawler)
    return requested


def make_handler(**kwargs):
    handler = weibo_handler.WeiboHandler(
        {"headers": {"User-Agent": "f2-test"}, "cookie": "SUB=guest", "timeout": 0}
        | kwargs
    )
    handler.enable_bark = False
    return handler


async def collect_ids(handler, **kwargs):
    return [w.weibo_id async for w in handler.fetch_user_weibo(UID, **kwargs)]


# ---------------- 最大数量 ----------------


async def test_fetch_user_weibo_reads_until_last_page(monkeypatch):
    requested = use_pages(
        monkeypatch,
        [
            page([weibo("1"), weibo("2")]),
            page([weibo("3"), weibo("4")]),
            page([weibo("5")], since_id=""),
        ],
    )
    assert await collect_ids(make_handler()) == [["1", "2"], ["3", "4"], ["5"]]
    assert requested == [1, 2, 3]


async def test_fetch_user_weibo_stops_when_total_reached(monkeypatch):
    requested = use_pages(
        monkeypatch,
        [page([weibo("1"), weibo("2")], total=3), page([weibo("3")], total=3)],
    )
    assert await collect_ids(make_handler()) == [["1", "2"], ["3"]]
    assert requested == [1, 2]


async def test_fetch_user_weibo_truncates_to_max_counts(monkeypatch):
    requested = use_pages(
        monkeypatch,
        [
            page([weibo("1"), weibo("2")]),
            page([weibo("3"), weibo("4")]),
            page([weibo("5")], since_id=""),
        ],
    )
    pages = [w async for w in make_handler().fetch_user_weibo(UID, max_counts=3)]
    assert [w.weibo_id for w in pages] == [["1", "2"], ["3"]]
    # 截断后的页面只包含保留的微博，其余字段不变
    assert pages[1]._to_raw()["data"]["since_id"] == "next"
    assert [d["weibo_id"] for d in pages[1]._to_list()] == ["3"]
    assert requested == [1, 2]


async def test_post_mode_passes_max_counts(monkeypatch, tmp_path):
    captured = {}

    async def extract_weibo_uid(self, url):
        return UID

    async def get_or_add_user_data(self, kwargs, uid, db):
        return tmp_path

    async def fetch_user_weibo(self, uid, **kwargs):
        captured.update(kwargs)
        return
        yield

    class DummyDB:
        def __init__(self, name):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

    Handler = weibo_handler.WeiboHandler
    monkeypatch.setattr(Handler, "extract_weibo_uid", extract_weibo_uid)
    monkeypatch.setattr(Handler, "get_or_add_user_data", get_or_add_user_data)
    monkeypatch.setattr(Handler, "fetch_user_weibo", fetch_user_weibo)
    monkeypatch.setattr(weibo_handler, "AsyncUserDB", DummyDB)

    await make_handler(
        url=f"https://weibo.com/u/{UID}", max_counts=5
    ).handle_user_weibo()
    assert captured["max_counts"] == 5

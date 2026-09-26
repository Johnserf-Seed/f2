# path: tests/test_weibo_post_mode.py

import datetime

import pytest

from f2.apps.weibo import handler as weibo_handler
from f2.apps.weibo.cli import weibo as weibo_command
from f2.apps.weibo.utils import (
    filter_weibos_by_interval,
    is_pinned_weibo,
    weibo_created_at_to_timestamp,
)
from f2.exceptions import ConfError

UID = "2265830070"
TZ8 = datetime.timezone(datetime.timedelta(hours=8))


def at(*args):
    """生成与接口相同格式的发布时间，如 Mon Jan 01 12:00:00 +0800 2024"""
    return datetime.datetime(*args, tzinfo=TZ8).strftime("%a %b %d %H:%M:%S %z %Y")


def ts(*args):
    return int(datetime.datetime(*args, tzinfo=TZ8).timestamp())


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


# ---------------- 日期区间（#222） ----------------

MARCH_2024 = (ts(2024, 3, 1), ts(2024, 3, 31, 23, 59, 59))


@pytest.mark.parametrize(
    "created_at, expected",
    [
        ("Mon Jan 01 00:00:00 +0800 2024", 1704038400),
        ("Sun Dec 31 16:00:00 +0000 2023", 1704038400),
        (" Mon Jan 01 00:00:00 +0800 2024 ", 1704038400),
        ("2024-01-01 00-00-00", None),
        ("", None),
        (None, None),
        (1704038400, None),
    ],
)
def test_weibo_created_at_to_timestamp(created_at, expected):
    assert weibo_created_at_to_timestamp(created_at) == expected


@pytest.mark.parametrize(
    "item, expected",
    [
        ({"isTop": 1}, True),
        ({"mblogtype": 2}, True),
        ({"isTop": 0, "mblogtype": 0}, False),
        ({}, False),
    ],
)
def test_is_pinned_weibo(item, expected):
    assert is_pinned_weibo(item) is expected


def test_filter_keeps_weibos_in_range_including_boundaries():
    weibos = [
        weibo("1", at(2024, 4, 1)),
        weibo("2", at(2024, 3, 31, 23, 59, 59)),
        weibo("3", at(2024, 3, 1, 0, 0, 0)),
    ]
    kept, reached_start = filter_weibos_by_interval(weibos, *MARCH_2024)
    assert [w["idstr"] for w in kept] == ["2", "3"]
    assert reached_start is False


def test_filter_stops_after_last_regular_weibo_before_start():
    weibos = [weibo("1", at(2024, 3, 2)), weibo("2", at(2024, 2, 29, 23, 59, 59))]
    kept, reached_start = filter_weibos_by_interval(weibos, *MARCH_2024)
    assert [w["idstr"] for w in kept] == ["1"]
    assert reached_start is True


def test_filter_ignores_old_pinned_weibo_when_deciding_to_stop():
    weibos = [
        weibo("top", at(2020, 5, 1), isTop=1),
        weibo("1", at(2024, 3, 20)),
    ]
    kept, reached_start = filter_weibos_by_interval(weibos, *MARCH_2024)
    assert [w["idstr"] for w in kept] == ["1"]
    assert reached_start is False


def test_filter_keeps_pinned_weibo_in_range():
    weibos = [weibo("top", at(2024, 3, 8), mblogtype=2), weibo("1", at(2024, 5, 1))]
    kept, reached_start = filter_weibos_by_interval(weibos, *MARCH_2024)
    assert [w["idstr"] for w in kept] == ["top"]
    assert reached_start is False


def test_filter_page_with_only_old_pinned_weibos_keeps_paging():
    weibos = [weibo("top", at(2020, 5, 1), isTop=1)]
    assert filter_weibos_by_interval(weibos, *MARCH_2024) == ([], False)


def test_filter_skips_unparsable_publish_time():
    weibos = [
        weibo("1", at(2024, 2, 1)),
        weibo("2", "昨天 12:00"),
        weibo("3", None),
    ]
    kept, reached_start = filter_weibos_by_interval(weibos, *MARCH_2024)
    assert kept == []
    # 按最后一条能解析的非置顶微博判断
    assert reached_start is True


async def test_fetch_user_weibo_filters_by_interval_and_stops_early(monkeypatch):
    requested = use_pages(
        monkeypatch,
        [
            page(
                [
                    weibo("top", at(2020, 5, 1), isTop=1),
                    weibo("apr", at(2024, 4, 10)),
                    weibo("end", at(2024, 3, 31, 23, 59, 59)),
                    weibo("mar20", at(2024, 3, 20)),
                ]
            ),
            page(
                [
                    weibo("mar05", at(2024, 3, 5)),
                    weibo("start", at(2024, 3, 1, 0, 0, 0)),
                    weibo("feb", at(2024, 2, 29, 23, 59, 59)),
                ]
            ),
            page([weibo("jan", at(2024, 1, 1))], since_id=""),
        ],
    )
    pages = [w async for w in make_handler().fetch_user_weibo(UID, interval=MARCH_2024)]
    assert [w.weibo_id for w in pages] == [["end", "mar20"], ["mar05", "start"]]
    # 第二页已经出现区间开始之前的微博，不再请求第三页
    assert requested == [1, 2]


async def test_fetch_user_weibo_skips_pages_newer_than_range(monkeypatch):
    requested = use_pages(
        monkeypatch,
        [
            page([weibo("may", at(2024, 5, 1)), weibo("apr", at(2024, 4, 1))]),
            page([weibo("mar", at(2024, 3, 15))], since_id=""),
        ],
    )
    got = await collect_ids(make_handler(), interval=MARCH_2024)
    assert got == [[], ["mar"]]
    assert requested == [1, 2]


async def test_fetch_user_weibo_applies_max_counts_after_interval(monkeypatch):
    requested = use_pages(
        monkeypatch,
        [
            page([weibo("apr", at(2024, 4, 1)), weibo("mar20", at(2024, 3, 20))]),
            page([weibo("mar10", at(2024, 3, 10)), weibo("mar05", at(2024, 3, 5))]),
            page([weibo("mar02", at(2024, 3, 2))], since_id=""),
        ],
    )
    got = await collect_ids(make_handler(), interval=MARCH_2024, max_counts=2)
    assert got == [["mar20"], ["mar10"]]
    assert requested == [1, 2]


def patch_post_mode(monkeypatch, tmp_path, captured):
    async def extract_weibo_uid(self, url):
        captured["extract_called"] = True
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


@pytest.mark.parametrize(
    "interval, expected",
    [
        ("all", None),
        (None, None),
        ("2024-03-01|2024-03-31", MARCH_2024),
    ],
)
async def test_post_mode_passes_parsed_interval(
    monkeypatch, tmp_path, interval, expected
):
    captured = {}
    patch_post_mode(monkeypatch, tmp_path, captured)
    handler = make_handler(url=f"https://weibo.com/u/{UID}", interval=interval)
    await handler.handle_user_weibo()
    assert captured["interval"] == expected


@pytest.mark.parametrize("interval", ["2024-03-01", "2024-03-31|2024-03-01"])
async def test_post_mode_rejects_invalid_interval_before_requests(
    monkeypatch, tmp_path, interval
):
    captured = {}
    patch_post_mode(monkeypatch, tmp_path, captured)
    handler = make_handler(url=f"https://weibo.com/u/{UID}", interval=interval)
    with pytest.raises(ConfError):
        await handler.handle_user_weibo()
    assert "extract_called" not in captured


def test_cli_has_interval_option():
    option = next(p for p in weibo_command.params if p.name == "interval")
    assert option.opts == ["--interval", "-i"]

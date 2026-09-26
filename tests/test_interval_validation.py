# path: tests/test_interval_validation.py

import os
import re
import subprocess
import sys

import pytest

from f2.apps.douyin import handler as douyin_handler
from f2.apps.douyin.dl import DouyinDownloader
from f2.apps.tiktok import handler as tiktok_handler
from f2.apps.tiktok.dl import TiktokDownloader
from f2.apps.twitter.dl import TwitterDownloader
from f2.apps.twitter.handler import TwitterHandler
from f2.exceptions import ConfError
from f2.utils.time.timestamp import interval_2_timestamp

KWARGS = {
    "cookie": "a=b",
    "headers": {"User-Agent": "f2-test"},
    "proxies": {"http://": None, "https://": None},
}
INVALID = ["2024/01/01|2024/12/31", "2024-01-01", "2024-12-31|2024-01-01"]
INTERVAL = "2024-01-01|2024-12-31"
DOWNLOADERS = [DouyinDownloader, TiktokDownloader, TwitterDownloader]


# ---------------- 下载器在请求前校验 ----------------


@pytest.mark.parametrize("downloader_cls", DOWNLOADERS)
@pytest.mark.parametrize("interval", INVALID)
def test_downloader_rejects_invalid_interval(downloader_cls, interval):
    # 此前只记一条日志：各模式翻完所有页面，却因筛选失败一个都不下载
    with pytest.raises(ConfError) as exc_info:
        downloader_cls(KWARGS | {"interval": interval})
    assert exc_info.value.key == "interval"


@pytest.mark.parametrize("downloader_cls", DOWNLOADERS)
@pytest.mark.parametrize("interval", [None, "all", INTERVAL])
async def test_downloader_accepts_valid_interval(downloader_cls, interval):
    downloader = downloader_cls(KWARGS | {"interval": interval})
    await downloader.close()


@pytest.mark.parametrize(
    "handler_cls",
    [douyin_handler.DouyinHandler, tiktok_handler.TiktokHandler, TwitterHandler],
)
def test_handler_rejects_invalid_interval_on_creation(handler_cls):
    with pytest.raises(ConfError):
        handler_cls(KWARGS | {"interval": INVALID[0]})


# ---------------- 主页作品的翻页游标 ----------------


class DummyDB:
    def __init__(self, name):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


def expected_cursors():
    """与此前 interval_2_timestamp 的结果一致（毫秒）"""
    return (
        interval_2_timestamp(INTERVAL, date_type="start"),
        interval_2_timestamp(INTERVAL, date_type="end"),
    )


async def test_douyin_post_cursors_from_interval(monkeypatch, tmp_path):
    captured = {}

    async def get_sec_user_id(url):
        return "MS4wLjABAAAA"

    async def get_or_add_user_data(self, kwargs, sec_user_id, db):
        return tmp_path

    async def fetch_user_post_videos(self, sec_user_id, min_cursor, max_cursor, *args):
        captured["cursors"] = (min_cursor, max_cursor)
        return
        yield

    Handler = douyin_handler.DouyinHandler
    monkeypatch.setattr(
        douyin_handler.SecUserIdFetcher, "get_sec_user_id", get_sec_user_id
    )
    monkeypatch.setattr(douyin_handler, "AsyncUserDB", DummyDB)
    monkeypatch.setattr(Handler, "get_or_add_user_data", get_or_add_user_data)
    monkeypatch.setattr(Handler, "fetch_user_post_videos", fetch_user_post_videos)

    handler = Handler(
        KWARGS | {"url": "https://www.douyin.com/user/x", "interval": INTERVAL}
    )
    await handler.handle_user_post()

    assert captured["cursors"] == expected_cursors() == (1704038400000, 1735660799000)


async def test_tiktok_post_cursors_from_interval(monkeypatch, tmp_path):
    captured = {}

    async def get_secuid(url):
        return "MS4wLjABAAAA"

    async def get_or_add_user_data(self, secUid, uniqueId, db):
        return tmp_path

    async def fetch_user_post_videos(self, secUid, cursor, min_cursor, *args):
        captured["cursors"] = (min_cursor, cursor)
        return
        yield

    Handler = tiktok_handler.TiktokHandler
    monkeypatch.setattr(tiktok_handler.SecUserIdFetcher, "get_secuid", get_secuid)
    monkeypatch.setattr(tiktok_handler, "AsyncUserDB", DummyDB)
    monkeypatch.setattr(Handler, "get_or_add_user_data", get_or_add_user_data)
    monkeypatch.setattr(Handler, "fetch_user_post_videos", fetch_user_post_videos)

    handler = Handler(
        KWARGS | {"url": "https://www.tiktok.com/@x", "interval": INTERVAL}
    )
    await handler.handle_user_post()

    assert captured["cursors"] == expected_cursors()


# ---------------- CLI ----------------


def run_cli(tmp_path, *args):
    code = f"from f2.cli.cli_commands import main; main({list(args)!r})"
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env={**os.environ, "COLUMNS": "200"},
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.returncode, re.sub(
        r"\x1b\[[0-9;]*m", "", result.stdout + result.stderr
    )


@pytest.mark.parametrize(
    "app, url",
    [("dy", "https://www.douyin.com/user/x"), ("tk", "https://www.tiktok.com/@x")],
)
def test_cli_reports_invalid_interval_before_requests(tmp_path, app, url):
    code, output = run_cli(
        tmp_path, "--no-log-file", app, "-M", "post", "-u", url, "-i", INVALID[0]
    )
    assert code == 1
    assert "Setting: interval" in output
    assert "Traceback" not in output

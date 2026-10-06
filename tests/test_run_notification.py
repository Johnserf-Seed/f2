# path: tests/test_run_notification.py

import types

import pytest

from f2.apps.bark import handler as bark_handler
from f2.apps.bark import notifier as bark_notifier
from f2.apps.tiktok import handler as tiktok_handler
from f2.apps.weibo import handler as weibo_handler
from f2.cli.cli_commands import send_run_notification
from f2.dl.base_downloader import BaseDownloader
from f2.exceptions.base import F2Error
from f2.utils.core.run_report import (
    NullNotifier,
    collect_run_report,
    notify_now,
    record_notification,
)


class RecordingNotifier:
    def __init__(self):
        self.sent = []

    async def send(self, title, body, **options):
        self.sent.append((title, body, options))


# ---------------- 运行结束时的通知 ----------------


async def test_nothing_is_sent_without_activity():
    # 例如定时检查直播时未开播，此前每次都推送
    notifier = RecordingNotifier()
    with collect_run_report(notifier):
        await send_run_notification({"app_name": "douyin", "mode": "live"})

    assert notifier.sent == []


async def test_recorded_text_is_sent_with_the_results():
    notifier = RecordingNotifier()
    with collect_run_report(notifier) as report:
        record_notification(
            "[DouYin] 主页作品下载", "用户：作者\n作品数：3\n", "DouYin"
        )
        report.completed_downloads = 5
        report.skipped_downloads = 1
        report.failed_downloads.append("a.mp4")
        await send_run_notification({"app_name": "douyin", "mode": "post"})

    [(title, body, options)] = notifier.sent
    assert title == "[DouYin] 主页作品下载"
    assert body.startswith("用户：作者\n作品数：3")
    assert "完成 5 个，跳过 1 个，失败 1 个" in body
    assert options == {"group": "DouYin"}


async def test_aborted_run_reports_the_reason():
    notifier = RecordingNotifier()
    with collect_run_report(notifier):
        await send_run_notification(
            {"app_name": "tiktok", "mode": "post"}, F2Error("链接错误")
        )

    [(title, body, _)] = notifier.sent
    assert title.startswith("[TikTok] post")
    assert "链接错误" in body


async def test_several_recorded_texts_are_combined():
    notifier = RecordingNotifier()
    with collect_run_report(notifier):
        record_notification("[DouYin] 收藏夹作品下载", "收藏夹：A", "DouYin")
        record_notification("[DouYin] 收藏夹作品下载", "收藏夹：B", "DouYin")
        await send_run_notification({"app_name": "douyin", "mode": "collects"})

    [(title, body, _)] = notifier.sent
    assert body.index("收藏夹：A") < body.index("收藏夹：B")


# ---------------- 库调用不再发送通知 ----------------


class WeiboCrawler:
    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def fetch_weibo_detail(self, params):
        return {
            "ok": 1,
            "idstr": "1",
            "text_raw": "微博正文",
            "created_at": "Sun Oct 05 10:00:00 +0800 2026",
            "user": {"idstr": "2", "screen_name": "作者"},
        }


@pytest.fixture
def weibo(monkeypatch):
    monkeypatch.setattr(weibo_handler, "WeiboCrawler", WeiboCrawler)
    return weibo_handler.WeiboHandler({"headers": {}, "cookie": "a=b"})


async def test_fetching_only_records_the_text(weibo):
    # 此前在获取数据时就发送“下载”通知，早于下载完成
    notifier = RecordingNotifier()
    with collect_run_report(notifier) as report:
        await weibo.fetch_one_weibo("1")

    assert notifier.sent == []
    assert [n.title for n in report.notifications] == ["[Weibo] 单一微博下载"]


async def test_library_calls_send_nothing(weibo):
    # 没有活动的运行（作为库使用）时既不记录也不发送
    weibo_data = await weibo.fetch_one_weibo("1")

    assert weibo_data.weibo_id == "1"


# ---------------- 开播提醒 ----------------


class TiktokCrawler:
    status = 2

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def fetch_user_live(self, params):
        return {
            "data": {
                "user": {"roomId": "7001"},
                "liveRoom": {
                    "status": type(self).status,
                    "title": "直播标题",
                    "liveRoomStats": {"userCount": 10},
                },
            }
        }


@pytest.mark.parametrize("status, reminded", [(2, True), (4, False)])
async def test_live_reminder_is_sent_right_away(monkeypatch, status, reminded):
    monkeypatch.setattr(tiktok_handler, "TiktokCrawler", TiktokCrawler)
    monkeypatch.setattr(tiktok_handler, "UserLive", types.SimpleNamespace)
    monkeypatch.setattr(TiktokCrawler, "status", status)
    handler = tiktok_handler.TiktokHandler({"headers": {}, "cookie": "a=b"})
    notifier = RecordingNotifier()

    with collect_run_report(notifier):
        await handler.fetch_user_live_videos("someone")
        # 开播提醒不等运行结束
        sent_before_end = list(notifier.sent)

    assert bool(sent_before_end) is reminded
    if reminded:
        assert sent_before_end[0][0] == "[TikTok] 直播下载"


async def test_notify_now_without_a_run_sends_nothing():
    await notify_now("标题", "正文")


# ---------------- 下载结果计数 ----------------


class DummyProgress:
    async def add_task(self, *args, **kwargs):
        return 0

    async def update(self, *args, **kwargs):
        return None


async def test_completed_and_skipped_files_are_counted(tmp_path):
    downloader = BaseDownloader({"headers": {"User-Agent": "f2-test"}})
    downloader.progress = DummyProgress()
    (tmp_path / "old_desc.txt").write_text("已存在", encoding="utf-8")

    with collect_run_report() as report:
        await downloader.initiate_static_download(
            "文案", "新内容", tmp_path, "new", "_desc.txt"
        )
        await downloader.initiate_static_download(
            "文案", "新内容", tmp_path, "old", "_desc.txt"
        )
        await downloader.execute_tasks()
    await downloader.close()

    assert (report.completed_downloads, report.skipped_downloads) == (1, 1)


# ---------------- 通知对象 ----------------


@pytest.mark.parametrize("enabled", [True, False])
def test_notifier_follows_enable_bark(monkeypatch, enabled):
    monkeypatch.setattr(
        bark_notifier.ClientConfManager, "enable_bark", classmethod(lambda cls: enabled)
    )
    monkeypatch.setattr(
        bark_notifier.ClientConfManager, "merge", classmethod(lambda cls: {"key": "k"})
    )

    notifier = bark_notifier.notifier_from_config()

    expected = bark_notifier.BarkNotifier if enabled else NullNotifier
    assert isinstance(notifier, expected)


async def test_bark_failures_do_not_stop_the_run(monkeypatch):
    async def broken(self, *args, **kwargs):
        raise ValueError("加密配置缺失")

    monkeypatch.setattr(bark_handler.BarkHandler, "send_quick_notification", broken)

    await bark_notifier.BarkNotifier({"key": "k"}).send("标题", "正文")

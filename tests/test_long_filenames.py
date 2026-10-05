# path: tests/test_long_filenames.py

from pathlib import Path

import pytest

from f2.apps.douyin.dl import DouyinDownloader
from f2.apps.douyin.utils import format_file_name as douyin_format_file_name
from f2.apps.tiktok.dl import TiktokDownloader
from f2.apps.twitter.dl import TwitterDownloader
from f2.apps.weibo.dl import WeiboDownloader
from f2.dl.base_downloader import BaseDownloader
from f2.utils.core.run_report import collect_run_report
from f2.utils.file import path as path_module
from f2.utils.file.name import FILENAME_BYTE_LIMIT, fit_filename
from f2.utils.file.path import WINDOWS_MAX_DIR_PATH, extended_length_path, long_path

SUFFIX = "_video.mp4"


def size(text):
    return len(text.encode("utf-8"))


class DummyProgress:
    async def add_task(self, *args, **kwargs):
        return 0

    async def update(self, *args, **kwargs):
        return None


@pytest.fixture
async def downloader():
    dl = BaseDownloader({"headers": {"User-Agent": "f2-test"}})
    dl.progress = DummyProgress()
    yield dl
    await dl.close()


# ---------------- fit_filename ----------------


@pytest.mark.parametrize(
    "name", ["2024-09-05 18-40-18_每天有氧", "a" * (FILENAME_BYTE_LIMIT - len(SUFFIX))]
)
def test_fit_filename_keeps_names_within_limit(name):
    assert fit_filename(name, SUFFIX) == name + SUFFIX


@pytest.mark.parametrize(
    "name",
    [
        "a" * (FILENAME_BYTE_LIMIT - len(SUFFIX) + 1),
        "汉" * 100,
        "每天有氧😭#精神状态belike" * 12,
        "é" * 200,
    ],
)
def test_fit_filename_truncates_middle(name):
    result = fit_filename(name, SUFFIX)
    head, tail = result[: -len(SUFFIX)].split("......")
    assert result.endswith(SUFFIX)
    assert name.startswith(head) and name.endswith(tail)
    # 只丢弃被截断的半个字符，不会多截
    assert FILENAME_BYTE_LIMIT - 6 <= size(result) <= FILENAME_BYTE_LIMIT


def test_fit_filename_with_long_suffix():
    assert size(fit_filename("abcdef", "x" * 252)) <= FILENAME_BYTE_LIMIT


@pytest.mark.parametrize(
    "desc", ["a" * 500, "汉" * 500, "😭" * 500, "每天有氧 #健身打卡 " * 50]
)
@pytest.mark.parametrize(
    "suffix", ["_video.mp4", "_image_35.webp", "_cover.jpeg", "_desc.txt"]
)
def test_default_template_names_are_unchanged(desc, suffix):
    # 默认模板 {create}_{desc} 的文案已按 200 字节截断，文件名不会触及上限，升级后不会改名
    name = douyin_format_file_name(
        "{create}_{desc}", {"create_time": "2024-09-05 18-40-18", "desc": desc}
    )
    assert fit_filename(name, suffix) == name + suffix


# ---------------- 下载器 ----------------


async def test_static_download_saves_long_name_truncated(downloader, tmp_path):
    # #179：文件名超过 255 字节时，此前在 Linux、NAS 上无法创建
    name = "2024-09-05 18-40-18_" + "a" * 300
    with collect_run_report() as report:
        await downloader.initiate_static_download(
            "文案", "内容", tmp_path, name, "_desc.txt"
        )
        await downloader.execute_tasks()

    assert report.failed_downloads == []
    [saved] = tmp_path.iterdir()
    assert saved.name == fit_filename(name, "_desc.txt")
    assert saved.read_text(encoding="utf-8") == "内容"


async def test_download_task_uses_truncated_name(downloader, tmp_path, monkeypatch):
    targets = []

    async def fake_download_file(self, task_id, urls, full_path):
        targets.append(full_path)

    monkeypatch.setattr(BaseDownloader, "download_file", fake_download_file)
    await downloader.initiate_download(
        "视频", "https://a.example/1.mp4", tmp_path, "b" * 300, ".mp4"
    )
    await downloader.execute_tasks()

    assert targets == [tmp_path / fit_filename("b" * 300, ".mp4")]


# ---------------- Windows 长路径 ----------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        (r"C:\Users\f2\Download\a.mp4", r"\\?\C:\Users\f2\Download\a.mp4"),
        # #179 报告中的 NAS 共享目录
        (r"\\hy-nas\Data\douyin_f2\a.mp4", r"\\?\UNC\hy-nas\Data\douyin_f2\a.mp4"),
        (r"\\?\C:\Users\a.mp4", r"\\?\C:\Users\a.mp4"),
        (r"\\.\C:\Users\a.mp4", r"\\.\C:\Users\a.mp4"),
    ],
)
def test_extended_length_path(raw, expected):
    assert extended_length_path(raw) == expected


def test_long_path_keeps_paths_outside_windows(monkeypatch):
    monkeypatch.setattr(path_module.sys, "platform", "linux")
    raw = "/data/" + "a" * 300
    assert str(long_path(raw)) == raw


def windows_path(length):
    """生成指定长度的 Windows 绝对路径"""
    head = "C:\\Users\\f2\\Download\\douyin\\post\\"
    return head + "a" * (length - len(head) - len(".mp4")) + ".mp4"


def test_long_path_keeps_short_windows_paths(monkeypatch):
    monkeypatch.setattr(path_module.sys, "platform", "win32")
    raw = windows_path(WINDOWS_MAX_DIR_PATH)
    assert str(long_path(raw)) == raw


@pytest.mark.parametrize("length", [WINDOWS_MAX_DIR_PATH + 1, 400])
def test_long_path_extends_long_windows_paths(monkeypatch, length):
    monkeypatch.setattr(path_module.sys, "platform", "win32")
    raw = windows_path(length)
    assert str(long_path(raw)) == "\\\\?\\" + raw


def test_long_path_normalizes_before_extending(monkeypatch):
    # 扩展长度路径不再解析 . 与 ..，也不接受 /，转换前需要先规范化
    monkeypatch.setattr(path_module.sys, "platform", "win32")
    raw = "C:/Users/f2/./Download/../Download/" + "b" * 250 + ".mp4"
    expected = "\\\\?\\C:\\Users\\f2\\Download\\" + "b" * 250 + ".mp4"
    assert str(long_path(raw)) == expected


def test_long_path_extends_long_unc_paths(monkeypatch):
    monkeypatch.setattr(path_module.sys, "platform", "win32")
    raw = "\\\\hy-nas\\Data\\douyin_f2\\" + "c" * 250 + ".mp4"
    assert str(long_path(raw)) == "\\\\?\\UNC\\" + raw[2:]


async def test_download_targets_use_long_path_on_windows(downloader, monkeypatch):
    monkeypatch.setattr(path_module.sys, "platform", "win32")
    base = "C:\\Users\\f2\\Download\\douyin\\post\\" + "昵称" * 20
    file_path, full_path = downloader._build_target(base, "d" * 200, ".mp4")
    assert str(full_path) == "\\\\?\\" + base + "\\" + file_path


# ---------------- folderize 的作品目录 ----------------

CREATED = "2024-09-05 18-40-18"
NICKNAME = "每天有氧😭精神状态" * 2
DESC = "每天有氧 #健身打卡 " * 30  # 文案按 200 字节截断，加上昵称后仍超过 255 字节
VIDEO = "https://cdn.example/1.mp4"
APP_KWARGS = {
    "headers": {"User-Agent": "f2-test"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "naming": "{create}_{nickname}_{desc}",
    "folderize": True,
}


async def no_db(*args, **kwargs):
    return None


def record_folders(monkeypatch, downloader_class, methods):
    folders = []

    async def record(self, label, content, base_path, *args, **kwargs):
        folders.append(Path(base_path))

    for method in methods:
        monkeypatch.setattr(downloader_class, method, record)
    # 抖音、TikTok 结束时会在当前目录的用户数据库中记录最后一个作品
    if hasattr(downloader_class, "save_last_aweme_id"):
        monkeypatch.setattr(downloader_class, "save_last_aweme_id", no_db)
    return folders


def assert_folders_fit(folders, user_path):
    assert folders
    for folder in folders:
        assert folder.parent == user_path
        assert size(folder.name) <= FILENAME_BYTE_LIMIT
        assert folder.name.startswith(f"{CREATED}_{NICKNAME}")


@pytest.mark.parametrize(
    "downloader_class, data",
    [
        (
            DouyinDownloader,
            {
                "aweme_id": "1",
                "sec_user_id": "s",
                "private_status": 0,
                "aweme_type": 0,
                "video_play_addr": VIDEO,
                "create_time": CREATED,
                "nickname": NICKNAME,
                "desc": DESC,
            },
        ),
        (
            TiktokDownloader,
            {
                "aweme_id": "1",
                "secUid": "s",
                "privateItem": False,
                "secret": False,
                "video_playAddr": VIDEO,
                "createTime": CREATED,
                "nickname": NICKNAME,
                "desc": DESC,
            },
        ),
        (
            WeiboDownloader,
            {
                "weibo_id": "1",
                "uid": "u",
                "weibo_pic_num": 0,
                "is_video": 11,
                "playback_list": VIDEO,
                "weibo_created_at": CREATED,
                "nickname": NICKNAME,
                "weibo_desc": DESC,
            },
        ),
        (
            TwitterDownloader,
            {
                "user_id": "1",
                "tweet_id": "2",
                "tweet_media": [{"type": "video", "url": VIDEO}],
                "tweet_created_at": CREATED,
                "nickname": NICKNAME,
                "tweet_desc": DESC,
            },
        ),
    ],
    ids=["douyin", "tiktok", "weibo", "twitter"],
)
async def test_folderize_folder_name_fits(
    monkeypatch, tmp_path, downloader_class, data
):
    # #179：此前只截断文件名，作品目录名超过 255 字节时在 NAS 等文件系统上无法创建，
    # 这个作品的文件全部保存失败
    folders = record_folders(
        monkeypatch,
        downloader_class,
        ("initiate_download", "initiate_static_download"),
    )
    downloader = downloader_class(dict(APP_KWARGS))
    try:
        await downloader.handler_download(dict(APP_KWARGS), data, tmp_path)
    finally:
        await downloader.close()

    assert_folders_fit(folders, tmp_path)


@pytest.mark.parametrize(
    "downloader_class, data",
    [
        (
            DouyinDownloader,
            {
                "m3u8_pull_url": {"FULL_HD1": "https://cdn.example/a.m3u8"},
                "nickname": NICKNAME,
                "live_title": "直播标题" * 15,
            },
        ),
        (
            TiktokDownloader,
            {
                "live_hls_url": "https://cdn.example/a.m3u8",
                "nickname": NICKNAME,
                "live_title": "直播标题" * 15,
            },
        ),
    ],
    ids=["douyin", "tiktok"],
)
async def test_folderize_live_folder_name_fits(
    monkeypatch, tmp_path, downloader_class, data
):
    folders = record_folders(monkeypatch, downloader_class, ("initiate_m3u8_download",))
    # 直播的创建时间取当前时间
    monkeypatch.setattr(
        "f2.apps.douyin.dl.timestamp_2_str", lambda *args, **kwargs: CREATED
    )
    monkeypatch.setattr(
        "f2.apps.tiktok.dl.timestamp_2_str", lambda *args, **kwargs: CREATED
    )
    downloader = downloader_class(dict(APP_KWARGS))
    try:
        await downloader.handler_stream(dict(APP_KWARGS), data, tmp_path)
    finally:
        await downloader.close()

    assert_folders_fit(folders, tmp_path)

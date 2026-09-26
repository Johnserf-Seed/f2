# path: tests/test_download_local_errors.py

import pytest

from f2.dl import base_downloader as base_downloader_module
from f2.dl.base_downloader import BaseDownloader
from f2.utils.core.run_report import collect_run_report


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


@pytest.fixture
def forbid_requests(monkeypatch):
    async def forbid(*args, **kwargs):
        raise AssertionError("本地文件无法写入时不应发起请求")

    monkeypatch.setattr(base_downloader_module, "get_content_length", forbid)


def occupy(path):
    """在目录的位置放一个同名文件，让后续创建目录失败"""
    path.write_text("x", encoding="utf-8")
    return path


async def test_static_file_error_does_not_stop_other_tasks(downloader, tmp_path):
    # #179：一个文件写入失败时此前会中止整批下载
    blocker = occupy(tmp_path / "blocker")
    with collect_run_report() as report:
        await downloader.initiate_static_download("文案", "坏", blocker, "a", ".txt")
        await downloader.initiate_static_download("文案", "好", tmp_path, "b", ".txt")
        await downloader.execute_tasks()

    assert report.failed_downloads == [str(blocker / "a.txt")]
    assert (tmp_path / "b.txt").read_text(encoding="utf-8") == "好"


async def test_download_file_skips_requests_when_directory_cannot_be_created(
    downloader, tmp_path, forbid_requests
):
    target = occupy(tmp_path / "blocker") / "video.mp4"
    with collect_run_report() as report:
        await downloader.download_file(0, ["https://a.example/1.mp4"], target)

    assert report.failed_downloads == [str(target)]


async def test_download_file_does_not_try_other_links_when_file_cannot_be_opened(
    downloader, tmp_path, monkeypatch
):
    requested = []

    async def content_length(url, *args, **kwargs):
        requested.append(url)
        return 10**6

    monkeypatch.setattr(base_downloader_module, "get_content_length", content_length)
    target = tmp_path / "video.mp4"
    # 临时文件的位置被目录占住，打开时报错；换链接也会遇到同样的错误
    (tmp_path / "video.tmp").mkdir()

    with collect_run_report() as report:
        await downloader.download_file(
            0, ["https://a.example/1.mp4", "https://b.example/1.mp4"], target
        )

    assert requested == ["https://a.example/1.mp4"]
    assert report.failed_downloads == [str(target)]


async def test_too_long_directory_name_does_not_abort_batch(
    downloader, tmp_path, forbid_requests
):
    # 路径中有超过 255 字节的目录名时，Path.exists 会抛出 ENAMETOOLONG
    base = tmp_path / ("d" * 300)
    with collect_run_report() as report:
        await downloader.initiate_download(
            "视频", "https://a.example/1.mp4", base, "a", ".mp4"
        )
        await downloader.initiate_static_download("文案", "好", tmp_path, "b", ".txt")
        await downloader.execute_tasks()

    assert report.failed_downloads == [str(base / "a.mp4")]
    assert (tmp_path / "b.txt").exists()

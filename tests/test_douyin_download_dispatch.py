# path: tests/test_douyin_download_dispatch.py

import logging

import pytest

from f2.apps.douyin.dl import DouyinDownloader

VIDEO_URL = ["https://example.com/video.mp4"]
IMAGE_URLS = ["https://example.com/1.webp", "https://example.com/2.webp"]
KWARGS = {"naming": "{create}_{desc}", "folderize": False}


@pytest.fixture
def downloader(monkeypatch):
    """替换真正的下载与写数据库，只记录走了哪条下载路径"""
    dl = DouyinDownloader(
        {"cookie": "ttwid=guest", "headers": {"User-Agent": "f2-test"}}
    )
    dl.calls = []

    async def download_video():
        dl.calls.append("video")

    async def download_images():
        dl.calls.append("images")

    async def save_last_aweme_id(sec_user_id, aweme_id):
        dl.calls.append("saved")

    monkeypatch.setattr(dl, "download_video", download_video)
    monkeypatch.setattr(dl, "download_images", download_images)
    monkeypatch.setattr(dl, "save_last_aweme_id", save_last_aweme_id)
    return dl


def aweme(aweme_type, video=None, images=None, **extra):
    return {
        "aweme_id": "7255598074305809723",
        "sec_user_id": "MS4wLjABAAAA",
        "aweme_type": aweme_type,
        "private_status": 0,
        "is_prohibited": False,
        "video_play_addr": video,
        "images": images,
        **extra,
    }


def f2_warnings(caplog):
    return [
        r.getMessage()
        for r in caplog.records
        if r.name == "f2" and r.levelno == logging.WARNING
    ]


# 51、53、66 是 #402 中确认与视频结构相同的新类型，999 代表以后可能出现的未知类型
@pytest.mark.parametrize("aweme_type", [0, 4, 51, 53, 55, 61, 66, 109, 201, 999])
async def test_types_with_video_are_downloaded_as_video(
    downloader, tmp_path, aweme_type
):
    await downloader.handler_download(
        KWARGS, aweme(aweme_type, video=VIDEO_URL), tmp_path
    )
    assert downloader.calls == ["video", "saved"]


@pytest.mark.parametrize("aweme_type", [68, 150])
async def test_types_with_images_are_downloaded_as_gallery(
    downloader, tmp_path, aweme_type
):
    await downloader.handler_download(
        KWARGS, aweme(aweme_type, images=IMAGE_URLS), tmp_path
    )
    assert downloader.calls == ["images", "saved"]


async def test_aweme_without_media_is_reported(downloader, tmp_path, caplog):
    # 此前名单之外的类型既不下载也没有任何提示（#403 的症状）
    with caplog.at_level(logging.DEBUG):
        await downloader.handler_download(KWARGS, aweme(999), tmp_path)

    assert downloader.calls == ["saved"]
    assert any("999" in message for message in f2_warnings(caplog))


async def test_unsupported_private_status_is_reported(downloader, tmp_path, caplog):
    data = aweme(0, video=VIDEO_URL, private_status=3)
    with caplog.at_level(logging.DEBUG):
        await downloader.handler_download(KWARGS, data, tmp_path)

    assert downloader.calls == ["saved"]
    assert any("private_status=3" in message for message in f2_warnings(caplog))


async def test_prohibited_aweme_is_skipped(downloader, tmp_path):
    data = aweme(0, video=VIDEO_URL, is_prohibited=True)
    await downloader.handler_download(KWARGS, data, tmp_path)
    assert downloader.calls == []

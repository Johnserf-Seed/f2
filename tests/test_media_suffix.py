# path: tests/test_media_suffix.py

import httpx
import pytest

from f2.apps.douyin.dl import DouyinDownloader
from f2.apps.tiktok.dl import TiktokDownloader
from f2.dl.base_downloader import BaseDownloader

KWARGS = {
    "headers": {"User-Agent": "f2-test"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
}

# 各格式文件开头的字节
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + b"\x00" * 20
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 24
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8X" + b"\x00" * 16
GIF = b"GIF89a" + b"\x00" * 26
MP3_ID3 = b"ID3\x04\x00\x00" + b"\x00" * 26
MP3_FRAME = b"\xff\xfb\x90\x64" + b"\x00" * 28
AAC_ADTS = b"\xff\xf1\x50\x80" + b"\x00" * 28
M4A = b"\x00\x00\x00\x1cftypM4A \x00\x00\x02\x00" + b"\x00" * 16
AVIF = b"\x00\x00\x00\x1cftypavif" + b"\x00" * 20
MP4 = b"\x00\x00\x00\x18ftypisom" + b"\x00" * 20


@pytest.mark.parametrize(
    "head, expected",
    [
        (JPEG, ".jpeg"),
        (PNG, ".png"),
        (WEBP, ".webp"),
        (GIF, ".gif"),
        (MP3_ID3, ".mp3"),
        (MP3_FRAME, ".mp3"),
        (AAC_ADTS, ".aac"),
        (M4A, ".m4a"),
        (AVIF, ".avif"),
        (MP4, None),
        (b"<html>", None),
        (b"", None),
    ],
)
def test_suffix_from_magic(head, expected):
    assert BaseDownloader._suffix_from_magic(head) == expected


def with_files(downloader, files):
    """files：地址路径 -> (文件内容, Content-Type)；内容为 None 表示连接失败"""
    requests = []

    def handler(request):
        requests.append(
            (request.method, request.url.path, request.headers.get("range"))
        )
        content, content_type = files[request.url.path]
        if content is None:
            raise httpx.ConnectError("down")
        status = 404 if content == b"404" else 206
        return httpx.Response(
            status, content=content, headers={"Content-Type": content_type}
        )

    downloader._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return requests


@pytest.mark.parametrize(
    "content, content_type, expected",
    [
        (WEBP, "image/webp", ".webp"),
        (JPEG, "image/jpeg", ".jpeg"),
        # TikTok 的 MP3 原声标成 video/mp4，只能看内容
        (MP3_FRAME, "video/mp4", ".mp3"),
        (M4A, "video/mp4", ".m4a"),
        (MP4, "video/mp4", ".default"),
        (b"404", "text/html", ".default"),
        (None, "", ".default"),  # 请求失败
    ],
)
async def test_media_suffix_reads_only_the_first_bytes(content, content_type, expected):
    downloader = DouyinDownloader(KWARGS)
    requests = with_files(downloader, {"/a": (content, content_type)})

    assert (
        await downloader._media_suffix("https://cdn.example/a", ".default") == expected
    )
    assert requests == [("GET", "/a", "bytes=0-31")]
    await downloader.close()


@pytest.mark.parametrize(
    "fields, content, expected",
    [
        ({"animated_cover": "https://cdn.example/a"}, WEBP, ".webp"),
        ({"dynamic_cover": "https://cdn.example/a"}, WEBP, ".webp"),
        ({"dynamic_cover": "https://cdn.example/a"}, PNG, ".png"),
        ({"cover": "https://cdn.example/a"}, JPEG, ".jpeg"),
    ],
)
async def test_douyin_cover_suffix_matches_the_image(
    monkeypatch, tmp_path, fields, content, expected
):
    # 实测动态封面有 JPEG、PNG、WebP 与 WebP 动图，静态封面是 JPEG，
    # 此前一律存成 .gif（动画、动态封面）或 .webp（静态封面）
    downloader = DouyinDownloader(KWARGS)
    with_files(downloader, {"/a": (content, "image/jpeg")})
    saved = []

    async def record(self, label, url, base_path, name, suffix, *args, **kwargs):
        saved.append(suffix)

    monkeypatch.setattr(DouyinDownloader, "initiate_download", record)
    downloader.kwargs = {"naming": "{create}_{desc}"}
    downloader.aweme_id = "1"
    downloader.aweme_data_dict = {
        "create_time": "2026-10-05 10-00-00",
        "desc": "封面",
    } | fields
    downloader.base_path = tmp_path

    await downloader.download_cover()
    await downloader.close()

    assert saved == [expected]


async def no_db(*args, **kwargs):
    return None


@pytest.mark.parametrize(
    "music, cover, expected",
    [
        (M4A, JPEG, {"_music": ".m4a", "_cover": ".jpeg"}),
        (MP3_FRAME, WEBP, {"_music": ".mp3", "_cover": ".webp"}),
    ],
)
async def test_tiktok_music_and_dynamic_cover_suffix(
    monkeypatch, tmp_path, music, cover, expected
):
    # 实测原声有 MP3 也有 M4A，动态封面有 WebP 也有 JPEG，此前分别一律存成 .mp3 与 .webp
    downloader = TiktokDownloader(KWARGS)
    with_files(
        downloader, {"/music": (music, "video/mp4"), "/cover": (cover, "image/webp")}
    )
    saved = {}

    async def record(self, label, url, base_path, name, suffix, *args, **kwargs):
        saved[name.rsplit("_", 1)[-1]] = suffix

    monkeypatch.setattr(TiktokDownloader, "initiate_download", record)
    monkeypatch.setattr(TiktokDownloader, "save_last_aweme_id", no_db)

    await downloader.handler_download(
        KWARGS | {"naming": "{create}_{desc}", "music": True, "cover": True},
        {
            "aweme_id": "1",
            "secUid": "s",
            "privateItem": False,
            "secret": False,
            "createTime": "2026-10-05 10-00-00",
            "desc": "原声",
            "music_playUrl": "https://cdn.example/music",
            "video_dynamicCover": "https://cdn.example/cover",
        },
        tmp_path,
    )
    await downloader.close()

    assert {f"_{k}": v for k, v in saved.items() if k in ("music", "cover")} == expected

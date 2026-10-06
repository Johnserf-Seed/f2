# path: tests/test_douyin_cover.py

import httpx
import pytest

from f2.apps.douyin.dl import DouyinDownloader

KWARGS = {
    "headers": {"User-Agent": "f2-test"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
}


def downloader_with(content_types):
    """content_types：地址路径 -> HEAD 返回的 Content-Type（None 表示连接失败）"""
    requests = []

    def handler(request):
        requests.append((request.method, request.url.path))
        content_type = content_types[request.url.path]
        if content_type is None:
            raise httpx.ConnectError("down")
        return httpx.Response(200, headers={"Content-Type": content_type})

    downloader = DouyinDownloader(KWARGS)
    downloader._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return downloader, requests


@pytest.mark.parametrize(
    "content_type, expected",
    [
        ("image/webp", ".webp"),
        ("image/jpeg", ".jpeg"),
        ("image/png; charset=binary", ".png"),
        ("IMAGE/GIF", ".gif"),
        ("application/octet-stream", ".default"),
        (None, ".default"),  # 请求失败
    ],
)
async def test_image_suffix_follows_content_type(content_type, expected):
    downloader, requests = downloader_with({"/a": content_type})

    assert (
        await downloader._image_suffix("https://cdn.example/a", ".default") == expected
    )
    assert requests == [("HEAD", "/a")]
    await downloader.close()


@pytest.mark.parametrize(
    "fields, content_type, expected",
    [
        ({"animated_cover": "https://cdn.example/a"}, "image/webp", ".webp"),
        ({"dynamic_cover": "https://cdn.example/a"}, "image/webp", ".webp"),
        ({"dynamic_cover": "https://cdn.example/a"}, "image/jpeg", ".jpeg"),
        ({"cover": "https://cdn.example/a"}, "image/jpeg", ".jpeg"),
    ],
)
async def test_cover_suffix_matches_the_image(
    monkeypatch, tmp_path, fields, content_type, expected
):
    # 实测动态封面有 JPEG、PNG、WebP 与 WebP 动图，静态封面是 JPEG，
    # 此前一律存成 .gif（动画、动态封面）或 .webp（静态封面）
    downloader, _ = downloader_with({"/a": content_type})
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

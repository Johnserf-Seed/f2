# path: tests/test_download_resume.py

import os
import re

import aiofiles
import httpx
import pytest

from f2.dl import base_downloader as base_downloader_module
from f2.dl.base_downloader import BaseDownloader


class DummyProgress:
    async def update(self, *args, **kwargs):
        return None


class FlakyStream(httpx.AsyncByteStream):
    """先吐出 fail_after 字节，然后模拟读取超时"""

    def __init__(self, data: bytes, fail_after: int):
        self._data = data
        self._fail_after = fail_after

    async def __aiter__(self):
        yield self._data[: self._fail_after]
        raise httpx.ReadTimeout("simulated read timeout")


def _range_offset(request: httpx.Request) -> int:
    match = re.match(r"bytes=(\d+)-", request.headers.get("Range", ""))
    return int(match.group(1)) if match else 0


@pytest.fixture
def downloader(monkeypatch):
    dl = BaseDownloader(
        {"headers": {"User-Agent": "f2-test", "Referer": "https://x/"}, "cookie": "a=b"}
    )
    dl.progress = DummyProgress()

    async def no_sleep(_seconds):
        return None

    # 跳过重试退避，避免测试变慢
    monkeypatch.setattr(base_downloader_module.asyncio, "sleep", no_sleep)
    return dl


async def _run_download(downloader, tmp_path, handler, data, existing=b""):
    downloader._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    tmp_file = tmp_path / "video.tmp"
    if existing:
        tmp_file.write_bytes(existing)
    request = downloader.aclient.build_request("GET", "https://example.com/video.mp4")
    async with aiofiles.open(tmp_file, "ab" if existing else "wb") as file:
        ok = await downloader._download_chunks_optimized(
            request, file, len(data), task_id=0, start_byte=len(existing)
        )
    await downloader.aclient.aclose()
    return ok, tmp_file.read_bytes()


@pytest.mark.asyncio
async def test_retry_resumes_from_written_bytes_without_duplicates(
    downloader, tmp_path
):
    data = os.urandom(600 * 1024)  # 大于 256KB 缓冲区，保证超时前已有数据落盘
    seen_offsets = []
    tmp_file = tmp_path / "video.tmp"

    def handler(request: httpx.Request) -> httpx.Response:
        offset = _range_offset(request)
        seen_offsets.append(offset)
        if offset > 0:
            # 续传偏移必须等于此时磁盘上已有的字节数，否则会产生重复或缺失
            assert offset == tmp_file.stat().st_size
        if offset == 0:
            return httpx.Response(
                200,
                headers={"Content-Length": str(len(data))},
                stream=FlakyStream(data, fail_after=300 * 1024),
            )
        return httpx.Response(
            206,
            headers={
                "Content-Range": f"bytes {offset}-{len(data) - 1}/{len(data)}",
                "Content-Length": str(len(data) - offset),
            },
            content=data[offset:],
        )

    ok, written = await _run_download(downloader, tmp_path, handler, data)

    assert ok is True
    assert written == data, "重试后文件内容必须与源数据完全一致（无重复、无缺失）"
    assert seen_offsets[0] == 0
    # 第二次请求从已落盘的位置继续，而不是从 0 重新开始
    assert 0 < seen_offsets[1] <= 300 * 1024


@pytest.mark.asyncio
async def test_server_ignoring_range_restarts_file(downloader, tmp_path):
    data = os.urandom(50 * 1024)

    def handler(request: httpx.Request) -> httpx.Response:
        # 无论是否带 Range 都返回整个文件（服务器不支持断点续传）
        return httpx.Response(
            200, headers={"Content-Length": str(len(data))}, content=data
        )

    ok, written = await _run_download(
        downloader, tmp_path, handler, data, existing=b"OLD-PARTIAL-DATA"
    )

    assert ok is True
    assert written == data, "服务器返回 200 时必须丢弃旧内容，不能追加"


@pytest.mark.asyncio
async def test_content_range_mismatch_is_retried(downloader, tmp_path):
    data = os.urandom(600 * 1024)
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        offset = _range_offset(request)
        calls.append(offset)
        if len(calls) == 1:
            return httpx.Response(
                200,
                headers={"Content-Length": str(len(data))},
                stream=FlakyStream(data, fail_after=300 * 1024),
            )
        if len(calls) == 2:
            # 起点与请求不一致的 206，应被拒绝并重试
            return httpx.Response(
                206,
                headers={"Content-Range": f"bytes 0-{len(data) - 1}/{len(data)}"},
                content=data,
            )
        return httpx.Response(
            206,
            headers={"Content-Range": f"bytes {offset}-{len(data) - 1}/{len(data)}"},
            content=data[offset:],
        )

    ok, written = await _run_download(downloader, tmp_path, handler, data)

    assert ok is True
    assert written == data
    assert len(calls) == 3


def test_segment_request_does_not_touch_shared_client_headers(downloader):
    request = downloader._build_segment_request("https://cdn.example.com/seg.ts")

    assert "referer" not in request.headers
    assert "cookie" not in request.headers
    assert request.headers["user-agent"] == "f2-test"
    # 共享客户端的默认请求头必须保持不变
    assert downloader.aclient.headers["referer"] == "https://x/"
    assert downloader.aclient.headers["cookie"] == "a=b"

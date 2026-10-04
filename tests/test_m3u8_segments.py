# path: tests/test_m3u8_segments.py

from types import SimpleNamespace

import httpx
import pytest

import f2.dl.m3u8 as m3u8_module
from f2.apps.douyin.dl import DouyinDownloader
from f2.utils.core.signal import SignalManager

KWARGS = {
    "headers": {"User-Agent": "f2-test"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
}
SEGMENT = SimpleNamespace(absolute_uri="https://cdn.example/seg-1.ts", duration=0)
DATA = b"0123456789"


class Stream(httpx.AsyncByteStream):
    """先给出前 4 个字节，fail 为真时随后超时"""

    def __init__(self, fail):
        self.fail = fail

    async def __aiter__(self):
        yield DATA[:4]
        if self.fail:
            raise httpx.ReadTimeout("slow")
        yield DATA[4:]


@pytest.fixture
def downloader(monkeypatch, record_waits):
    playlists = [[SEGMENT], [SEGMENT], []]  # 第二轮播放列表里仍有该片段，第三轮直播结束
    attempts = []

    async def segments(url):
        return playlists.pop(0)

    async def content_length(*args, **kwargs):
        return 0

    def handler(request):
        attempts.append(request.url)
        return httpx.Response(200, stream=Stream(fail=len(attempts) == 1))

    monkeypatch.setattr(m3u8_module, "get_segments_from_m3u8", segments)
    monkeypatch.setattr(m3u8_module, "get_content_length", content_length)
    # 真实片段有几 MB，超时前已经交出若干个块；这里把块大小设为 4 字节来复现
    monkeypatch.setattr(m3u8_module, "get_chunk_size", lambda length: 4)
    record_waits(m3u8_module)
    monkeypatch.setattr(
        SignalManager, "is_shutdown_signaled", staticmethod(lambda: False)
    )

    downloader = DouyinDownloader(KWARGS)
    downloader._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    downloader.attempts = attempts
    return downloader


async def test_interrupted_segment_is_not_written_twice(downloader, tmp_path):
    # 此前片段下载到一半超时时，前 4 个字节已写入文件，下一轮重新下载又追加一遍
    target = tmp_path / "live.flv"
    task_id = await downloader.progress.add_task(
        description="live", filename=target.name, total=None
    )

    await downloader.download_m3u8_stream(
        task_id, "https://cdn.example/live.m3u8", target
    )
    await downloader.close()

    assert len(downloader.attempts) == 2
    assert target.read_bytes() == DATA

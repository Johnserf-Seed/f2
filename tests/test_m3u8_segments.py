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

    async def segments(url, **kwargs):
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


# ---------------- 播放列表 ----------------

PLAYLIST = "#EXTM3U\n#EXT-X-TARGETDURATION:2\n#EXTINF:2.0,\nseg-1.ts\n"
MASTER = (
    "#EXTM3U\n"
    "#EXT-X-STREAM-INF:BANDWIDTH=100000\nlow.m3u8\n"
    "#EXT-X-STREAM-INF:BANDWIDTH=900000\nhigh.m3u8\n"
)


def recorder(monkeypatch, record_waits, routes):
    """routes：URL 路径 -> 依次返回的响应（异常会被抛出）；返回请求记录"""
    requests = []

    def handler(request):
        requests.append(request)
        result = routes[request.url.path].pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    record_waits(m3u8_module)
    monkeypatch.setattr(m3u8_module, "get_content_length", content_length)
    monkeypatch.setattr(
        SignalManager, "is_shutdown_signaled", staticmethod(lambda: False)
    )
    downloader = DouyinDownloader(KWARGS)
    downloader._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return downloader, requests


async def content_length(*args, **kwargs):
    return 0


async def record(downloader, target):
    task_id = await downloader.progress.add_task(
        description="live", filename=target.name, total=None
    )
    await downloader.download_m3u8_stream(
        task_id, "https://cdn.example/live/index.m3u8", target
    )
    await downloader.close()


async def test_playlist_is_fetched_with_the_downloader_client(
    monkeypatch, record_waits, tmp_path
):
    # 此前由 m3u8 库用 urllib 请求，不经过配置的代理、没有超时，还会阻塞事件循环
    downloader, requests = recorder(
        monkeypatch,
        record_waits,
        {
            "/live/index.m3u8": [httpx.Response(200, text=MASTER), httpx.Response(404)],
            "/live/high.m3u8": [httpx.Response(200, text=PLAYLIST)],
            "/live/seg-1.ts": [httpx.Response(200, content=DATA)],
        },
    )
    target = tmp_path / "live.flv"

    await record(downloader, target)

    assert target.read_bytes() == DATA
    # 带宽最高的子播放列表；与 TS 片段一样不带 Referer、Cookie
    paths = [r.url.path for r in requests]
    assert paths == [
        "/live/index.m3u8",
        "/live/high.m3u8",
        "/live/seg-1.ts",
        "/live/index.m3u8",
    ]
    assert all("cookie" not in r.headers for r in requests)


async def test_network_error_does_not_end_the_recording(
    monkeypatch, record_waits, tmp_path
):
    # 此前刷新播放列表失败会被当作直播结束，录制提前停止
    downloader, requests = recorder(
        monkeypatch,
        record_waits,
        {
            "/live/index.m3u8": [
                httpx.ConnectError("reset"),
                httpx.Response(200, text=PLAYLIST),
                httpx.Response(404),
            ],
            "/live/seg-1.ts": [httpx.Response(200, content=DATA)],
        },
    )
    target = tmp_path / "live.flv"

    await record(downloader, target)

    assert target.read_bytes() == DATA


async def test_repeated_network_errors_fail_the_recording(
    monkeypatch, record_waits, tmp_path
):
    downloader, requests = recorder(
        monkeypatch,
        record_waits,
        {"/live/index.m3u8": [httpx.ConnectError("down")] * 5},
    )
    failed = []
    monkeypatch.setattr(m3u8_module, "record_failed_download", failed.append)

    await record(downloader, tmp_path / "live.flv")

    assert len(requests) == m3u8_module.MAX_PLAYLIST_ERRORS
    assert failed == [str(tmp_path / "live.flv")]

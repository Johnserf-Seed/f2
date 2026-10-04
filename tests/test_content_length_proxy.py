# path: tests/test_content_length_proxy.py

import httpx
import pytest
from httpx_socks import AsyncProxyTransport

from f2.dl import base_downloader as base_downloader_module
from f2.dl.base_downloader import BaseDownloader
from f2.utils.http.utils import get_content_length


class FakeClient:
    """记录创建客户端时的参数，HEAD 请求直接返回 Content-Length"""

    created: list = []

    def __init__(self, **kwargs):
        FakeClient.created.append(kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def head(self, url):
        return httpx.Response(
            200, headers={"Content-Length": "123"}, request=httpx.Request("HEAD", url)
        )


@pytest.fixture
def created(monkeypatch):
    FakeClient.created = []
    monkeypatch.setattr("f2.utils.http.utils.httpx.AsyncClient", FakeClient)
    return FakeClient.created


async def test_no_proxy_keeps_environment_and_system_proxies(created):
    # 指定传输层后 httpx 不再读取环境变量与系统代理，只靠系统代理上网时
    # HEAD 请求会直连超时，文件被当成 0 字节跳过（#462）
    assert await get_content_length("https://a.example/1.jpg", proxies={}) == 123
    assert created[0]["transport"] is None
    assert created[0]["mounts"] is None


async def test_configured_proxy_is_used(created):
    proxies = {"http://": "http://127.0.0.1:7890", "https://": "http://127.0.0.1:7890"}

    await get_content_length("https://a.example/1.jpg", proxies=proxies)

    assert isinstance(created[0]["transport"], httpx.AsyncHTTPTransport)


async def test_downloader_mounts_take_precedence(created):
    mounts = {"all://": httpx.AsyncHTTPTransport()}

    await get_content_length(
        "https://a.example/1.jpg",
        proxies={"http://": "http://127.0.0.1:7890"},
        mounts=mounts,
    )

    assert created[0]["mounts"] is mounts
    assert created[0]["transport"] is None


class DummyProgress:
    async def update(self, *args, **kwargs):
        return None


NONE = {"http://": None, "https://": None}


@pytest.mark.parametrize(
    "proxies, transport_type",
    [
        # 不配置代理时与下载请求一样直连或走系统代理
        (NONE, httpx.AsyncHTTPTransport),
        # 新格式的 SOCKS 代理此前在获取文件大小时被忽略
        ({"type": "socks5", "host": "127.0.0.1", "port": 1080}, AsyncProxyTransport),
    ],
)
async def test_downloader_reuses_its_transport(
    monkeypatch, tmp_path, proxies, transport_type
):
    received = []

    async def content_length(url, *args, **kwargs):
        received.append(kwargs)
        return 0

    monkeypatch.setattr(base_downloader_module, "get_content_length", content_length)
    downloader = BaseDownloader(
        {"headers": {"User-Agent": "f2-test"}, "proxies": proxies}
    )
    downloader.progress = DummyProgress()

    await downloader.download_file(0, ["https://a.example/1.mp4"], tmp_path / "1.mp4")
    await downloader.close()

    assert isinstance(received[0]["mounts"]["all://"], transport_type)
    # 配置了代理时与下载请求一样不再读取环境与系统代理
    assert received[0]["trust_env"] is (proxies is NONE)


async def test_cdn_access_denied_gives_a_hint(monkeypatch, caplog):
    # TikTok 视频 CDN（Akamai）按网络出口拒绝访问时，此前只显示 403 与“响应大小为 0 字节”
    def handler(request):
        return httpx.Response(
            403, headers={"Server": "AkamaiGHost"}, text="Access Denied"
        )

    real_client = httpx.AsyncClient

    def mocked_client(**kwargs):
        kwargs.pop("transport", None)
        kwargs.pop("mounts", None)
        return real_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr("f2.utils.http.utils.httpx.AsyncClient", mocked_client)

    with caplog.at_level("WARNING"):
        assert await get_content_length("https://v16-webapp-prime.us.tiktok.com/v") == 0

    assert "v16-webapp-prime.us.tiktok.com" in caplog.text
    assert "Access Denied" in caplog.text

# path: tests/test_impersonate_transport.py

import sys
from types import SimpleNamespace

import httpx
import pytest

import f2.apps.tiktok.crawler as crawler_module
from f2.apps.tiktok.crawler import TiktokCrawler
from f2.crawlers.base_crawler import BaseCrawler
from f2.utils.http import impersonate
from f2.utils.http.impersonate import ImpersonateTransport, create_impersonate_transport

SIGNED_URL = (
    "https://www.tiktok.com/api/post/item_list/"
    "?browser_version=5.0%20%28Windows%29&msToken=&X-Bogus=1&X-Gnarly=a/b-c="
)


class FakeCurlResponse:
    def __init__(self, status_code=200, headers=(), content=b"{}", http_version=3):
        self.status_code = status_code
        self.headers = SimpleNamespace(multi_items=lambda: list(headers))
        self.content = content
        self.http_version = http_version


class FakeSession:
    """记录请求参数的 curl_cffi AsyncSession 替身"""

    def __init__(self, response=None, error=None):
        self.calls = []
        self.response = response or FakeCurlResponse()
        self.error = error
        self.closed = False

    async def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if self.error is not None:
            raise self.error
        return self.response

    async def close(self):
        self.closed = True
        self.close_calls = getattr(self, "close_calls", 0) + 1


# ---------------- ImpersonateTransport ----------------


async def test_signed_url_and_headers_are_sent_as_is():
    session = FakeSession()
    headers = {"User-Agent": "UA", "Cookie": "msToken=t", "Referer": "r"}
    async with httpx.AsyncClient(
        transport=ImpersonateTransport(session), headers=headers
    ) as client:
        await client.get(SIGNED_URL, timeout=httpx.Timeout(5, read=10))

    [(method, url, kwargs)] = session.calls
    assert method == "GET"
    # 签名覆盖的是实际发送的字节，不能再被编码
    assert url == SIGNED_URL
    assert kwargs["quote"] is False
    # 重定向交给 httpx 客户端处理
    assert kwargs["allow_redirects"] is False
    sent = dict(kwargs["headers"])
    assert sent["user-agent"] == "UA" and sent["cookie"] == "msToken=t"
    # Host、Accept-Encoding 等由 curl 按浏览器的方式生成
    assert not {"host", "accept-encoding", "connection"} & set(sent)
    assert kwargs["timeout"] == (5, 10)
    assert kwargs["data"] is None
    assert session.closed


async def test_request_body_is_forwarded():
    session = FakeSession()
    async with httpx.AsyncClient(transport=ImpersonateTransport(session)) as client:
        await client.post(SIGNED_URL, content=b"a=1")
    assert session.calls[0][2]["data"] == b"a=1"


async def test_response_is_already_decoded():
    headers = [
        ("content-type", "application/json"),
        ("content-encoding", "br"),
        ("content-length", "7"),
        ("set-cookie", "msToken=new; Path=/"),
    ]
    session = FakeSession(FakeCurlResponse(headers=headers, content=b'{"a": 1}'))
    async with httpx.AsyncClient(transport=ImpersonateTransport(session)) as client:
        response = await client.get(SIGNED_URL)
        # curl 已经解压，httpx 不能再按 content-encoding 解码
        assert response.json() == {"a": 1}
        assert "content-encoding" not in response.headers
        assert response.http_version == "HTTP/2"
        # 响应中的 cookie 仍由 httpx 客户端处理
        assert client.cookies.get("msToken") == "new"


def test_missing_timeouts_mean_no_limit():
    assert impersonate._curl_timeout({}) is None
    assert impersonate._curl_timeout({"connect": 3, "read": None}) == 3


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("ConnectTimeout", httpx.ConnectTimeout),
        ("ReadTimeout", httpx.ReadTimeout),
        ("ProxyError", httpx.ProxyError),
        ("DNSError", httpx.ConnectError),
        ("SSLError", httpx.ConnectError),
        ("RequestException", httpx.TransportError),
    ],
)
async def test_curl_errors_become_httpx_errors(name, expected):
    curl_errors = pytest.importorskip("curl_cffi.requests.exceptions")
    session = FakeSession(error=getattr(curl_errors, name)("boom"))
    async with httpx.AsyncClient(transport=ImpersonateTransport(session)) as client:
        with pytest.raises(expected) as excinfo:
            await client.get(SIGNED_URL)
    assert excinfo.type is expected


async def test_other_errors_are_not_wrapped():
    session = FakeSession(error=ValueError("boom"))
    async with httpx.AsyncClient(transport=ImpersonateTransport(session)) as client:
        with pytest.raises(ValueError):
            await client.get(SIGNED_URL)


# ---------------- create_impersonate_transport ----------------


def test_missing_curl_cffi_falls_back_with_one_warning(monkeypatch):
    monkeypatch.setitem(sys.modules, "curl_cffi.requests", None)
    impersonate._warn_missing_once.cache_clear()
    warnings = []
    monkeypatch.setattr(impersonate.logger, "warning", warnings.append)

    assert create_impersonate_transport() is None
    assert create_impersonate_transport() is None
    assert len(warnings) == 1 and "curl_cffi" in warnings[0]
    impersonate._warn_missing_once.cache_clear()


async def test_session_impersonates_chrome_without_keeping_cookies():
    pytest.importorskip("curl_cffi")
    transport = create_impersonate_transport(
        proxy="socks5://127.0.0.1:1080", verify=False, max_clients=3
    )
    session = transport._session
    assert session.impersonate == "chrome"
    assert session.discard_cookies is True
    assert session.proxies == {"all": "socks5://127.0.0.1:1080"}
    assert session.verify is False and session.max_clients == 3
    await transport.aclose()


# ---------------- TiktokCrawler ----------------


def make_crawler(**kwargs):
    return TiktokCrawler(
        {
            "headers": {"User-Agent": "UA"},
            "cookie": "msToken=t",
            "proxies": {"http://": None, "https://": None},
            **kwargs,
        }
    )


def test_crawler_passes_network_settings(monkeypatch):
    seen = {}

    def factory(**kwargs):
        seen.update(kwargs)
        return None

    monkeypatch.setattr(crawler_module, "create_impersonate_transport", factory)
    # 只检查 TikTok 的覆盖逻辑，默认传输层不会读取这个不存在的 CA 文件
    monkeypatch.setattr(
        BaseCrawler, "_create_mount", lambda self, async_mode=False: {"all://": None}
    )
    crawler = make_crawler(
        proxies={"http://": "http://127.0.0.1:7890", "https://": None},
        max_connections=7,
        verify="/etc/f2/ca.pem",
    )

    mounts = crawler._create_mount(async_mode=True)
    assert seen == {
        "proxy": "http://127.0.0.1:7890",
        "verify": "/etc/f2/ca.pem",
        "max_clients": 7,
    }
    # 未安装 curl_cffi 时全部使用 httpx
    assert list(mounts) == ["all://"]


def test_sync_client_keeps_httpx(monkeypatch):
    def factory(**kwargs):
        raise AssertionError("同步客户端不应创建 curl_cffi 会话")

    monkeypatch.setattr(crawler_module, "create_impersonate_transport", factory)
    assert list(make_crawler()._create_mount()) == ["all://"]


async def test_tiktok_api_hosts_go_through_curl(monkeypatch):
    curl = FakeSession()
    monkeypatch.setattr(
        crawler_module,
        "create_impersonate_transport",
        lambda **kwargs: ImpersonateTransport(curl),
    )
    httpx_hosts = []

    def handler(request):
        httpx_hosts.append(request.url.host)
        return httpx.Response(200, json={})

    # 其他域名的默认传输层换成 MockTransport，避免联网
    monkeypatch.setattr(
        BaseCrawler,
        "_create_mount",
        lambda self, async_mode=False: {"all://": httpx.MockTransport(handler)},
    )
    crawler = make_crawler()

    webcast = "https://webcast.tiktok.com/webcast/im/fetch/?room_id=1"
    await crawler.aclient.get(SIGNED_URL)
    await crawler.aclient.get(webcast)
    await crawler.aclient.get("https://v16-webapp-prime.tiktok.com/video/tos/a")
    await crawler.close()

    # www 与 webcast 的接口经由 curl_cffi，视频 CDN 等其他域名仍使用 httpx
    assert [url for _method, url, _kwargs in curl.calls] == [SIGNED_URL, webcast]
    assert httpx_hosts == ["v16-webapp-prime.tiktok.com"]
    # 两个域名共用一个传输层，只关闭一次
    assert curl.close_calls == 1

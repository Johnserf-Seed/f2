# path: tests/test_get_content_length.py

from f2.utils.http.utils import get_content_length


class FakeResponse:
    def __init__(self, content_length="123"):
        self.headers = {"Content-Length": content_length}

    def raise_for_status(self):
        pass


class FakeClient:
    last_kwargs: dict = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        FakeClient.last_kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def head(self, url):
        return FakeResponse()


async def test_no_proxy_uses_default_client(monkeypatch):
    # 未配置代理时不传 transport：显式 transport 会让 httpx 绕过
    # 环境变量与系统代理，此前媒体下载因此全部连接超时
    monkeypatch.setattr("f2.utils.http.utils.httpx.AsyncClient", FakeClient)
    length = await get_content_length(
        "https://example.com/a.jpg", None, {"http://": None, "https://": None}
    )
    assert length == 123
    assert FakeClient.last_kwargs["transport"] is None


async def test_explicit_proxy_builds_transport(monkeypatch):
    # 显式配置了代理时仍然使用自定义传输层
    monkeypatch.setattr("f2.utils.http.utils.httpx.AsyncClient", FakeClient)
    length = await get_content_length(
        "https://example.com/a.jpg", None, {"http://": "http://127.0.0.1:7890"}
    )
    assert length == 123
    assert FakeClient.last_kwargs["transport"] is not None

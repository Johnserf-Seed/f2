# path: tests/test_tiktok_fetcher_headers.py

import json

import httpx
import pytest

from f2.apps.tiktok.utils import DeviceIdManager, SecUserIdFetcher, TokenManager


@pytest.fixture(autouse=True)
def forbid_mstoken(monkeypatch):
    # 旧的 msToken 生成接口已失效，获取 sec_uid 与设备 ID 时不应再调用
    def gen_real_msToken(cls):
        raise AssertionError("不应生成 msToken")

    monkeypatch.setattr(TokenManager, "_msToken_cache", None)
    monkeypatch.setattr(TokenManager, "gen_real_msToken", classmethod(gen_real_msToken))


def rehydration_page(scope: dict) -> str:
    data = json.dumps({"__DEFAULT_SCOPE__": scope})
    return (
        '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
        f"{data}</script>"
    )


async def test_get_secuid_does_not_send_mstoken(monkeypatch):
    sent = []

    def handler(request):
        sent.append(request)
        user = {"userInfo": {"user": {"secUid": "MS4w_f2"}}}
        return httpx.Response(200, text=rehydration_page({"webapp.user-detail": user}))

    monkeypatch.setattr(
        SecUserIdFetcher,
        "_create_mount",
        lambda self, async_mode=False: {"all://": httpx.MockTransport(handler)},
    )

    assert await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@f2") == "MS4w_f2"
    [request] = sent
    assert "cookie" not in request.headers
    assert request.headers["referer"] == "https://www.tiktok.com/@f2"


def test_device_id_headers_do_not_carry_mstoken():
    headers = DeviceIdManager._device_id_headers()
    assert list(headers) == ["User-Agent"]


@pytest.mark.parametrize("suffix", ["", "?lang=en", "/"])
async def test_get_secuid_reads_user_links_without_request(monkeypatch, suffix):
    # /user/<sec_uid> 的页面里没有用户数据（#366），sec_uid 直接从链接取出
    def handler(request):
        raise AssertionError("不应请求页面")

    monkeypatch.setattr(
        SecUserIdFetcher,
        "_create_mount",
        lambda self, async_mode=False: {"all://": httpx.MockTransport(handler)},
    )
    sec_uid = (
        "MS4wLjABAAAAXg0GY1OJPtnjttAj1Ha1a4FSzynLSdpA70MMIMmU3H-GZl-r-cSRydyhsC-Eb4bI"
    )
    url = f"https://www.tiktok.com/user/{sec_uid}{suffix}"
    assert await SecUserIdFetcher.get_secuid(url) == sec_uid

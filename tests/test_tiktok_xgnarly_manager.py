# path: tests/test_tiktok_xgnarly_manager.py

from urllib.parse import urlsplit

import httpx
import pytest

from f2.apps.tiktok.crawler import TiktokCrawler
from f2.apps.tiktok.model import CheckLiveAlive, UserPost
from f2.apps.tiktok.utils import TokenManager, XGnarlyManager
from f2.utils.crypto.bytedance.xgnarly import hash_state, unpack_payload, unseal

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
)
USER_POST = "https://www.tiktok.com/api/post/item_list/"


def query_params(url):
    """按出现顺序返回查询参数（不解码，签名的就是原始字节）"""
    return [part.split("=", 1) for part in urlsplit(url).query.split("&")]


# ---------------- XGnarlyManager ----------------


def test_signing_parameters_follow_business_parameters():
    url = XGnarlyManager.model_2_endpoint(
        UA, USER_POST, {"aid": "1988", "count": 35, "secUid": "MS4w"}, "a=b"
    )
    names = [name for name, _value in query_params(url)]
    assert names == [
        "aid",
        "count",
        "secUid",
        "X-Dynosaur",
        "msToken",
        "X-Bogus",
        "X-Gnarly",
    ]
    assert dict(query_params(url))["X-Bogus"] == "1"


def test_ms_token_comes_from_cookie():
    url = XGnarlyManager.model_2_endpoint(
        UA, USER_POST, {"aid": "1988"}, "ttwid=x; msToken=cookie_token=="
    )
    assert "&msToken=cookie_token==&X-Bogus=1&" in url


def test_missing_ms_token_is_left_empty():
    # 伪造的 msToken 会被拒绝，没有时留空
    url = XGnarlyManager.model_2_endpoint(UA, USER_POST, {"aid": "1988"}, "ttwid=x")
    assert "&msToken=&X-Bogus=1&" in url


def test_existing_query_string_is_extended():
    url = XGnarlyManager.model_2_endpoint(UA, f"{USER_POST}?a=1", {"aid": "1988"})
    assert url.startswith(f"{USER_POST}?a=1&aid=1988&X-Dynosaur=")


def test_httpx_sends_the_signed_url_unchanged():
    # 签名覆盖的是实际发送的字节，httpx 不能再重新编码
    params = UserPost(secUid="MS4wLjABAAAA").model_dump() | {"keyword": "猫 (cat)"}
    url = XGnarlyManager.model_2_endpoint(UA, USER_POST, params, "msToken=t")
    request = httpx.Request("GET", url)
    assert request.url.raw_path.decode("ascii") == url[len("https://www.tiktok.com") :]


def test_rejects_non_dict_params():
    with pytest.raises(TypeError):
        XGnarlyManager.model_2_endpoint(UA, USER_POST, [("aid", "1988")])


# ---------------- 请求模型 ----------------


def test_web_models_carry_raw_values_without_ms_token():
    params = UserPost(secUid="MS4w").model_dump()
    assert "msToken" not in params
    assert " (" in params["browser_version"]
    assert "%" not in params["tz_name"]
    url = XGnarlyManager.model_2_endpoint(UA, USER_POST, params)
    assert "&browser_version=5.0%20(" in url


def test_webcast_check_alive_keeps_legacy_encoding(monkeypatch):
    # webcast 接口仍使用 X-Bogus，参数与之前完全一致
    monkeypatch.setattr(TokenManager, "_msToken_cache", "legacy_token")
    params = CheckLiveAlive(room_ids="1").model_dump()
    assert params["msToken"] == "legacy_token"
    assert "%28" in params["browser_version"] and "%2F" in params["tz_name"]
    assert list(params)[-2:] == ["msToken", "room_ids"]


# ---------------- 爬虫 ----------------


@pytest.fixture
def crawler_requests(monkeypatch):
    monkeypatch.setattr(TokenManager, "_msToken_cache", "legacy_token")
    sent = []

    def handler(request):
        sent.append(request)
        return httpx.Response(200, json={"statusCode": 0})

    crawler = TiktokCrawler(
        {
            "headers": {"User-Agent": UA, "Referer": "https://www.tiktok.com/"},
            "cookie": "ttwid=x; msToken=cookie_token",
            "proxies": {"http://": None, "https://": None},
        }
    )
    crawler._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return crawler, sent


async def test_web_api_requests_use_new_signature(crawler_requests):
    crawler, sent = crawler_requests
    await crawler.fetch_user_post(UserPost(secUid="MS4w"))
    await crawler.close()

    [request] = sent
    params = dict(query_params(str(request.url)))
    assert request.url.path == "/api/post/item_list/"
    assert params["msToken"] == "cookie_token"
    assert params["X-Bogus"] == "1"
    # 签名中的 UA 哈希必须与请求头一致
    payload, _key = unseal(params["X-Dynosaur"])
    ua_hash = unpack_payload(payload)[0x30]
    assert ua_hash == hash_state(request.headers["User-Agent"]).to_bytes(4, "big")


async def test_webcast_requests_keep_x_bogus(crawler_requests):
    crawler, sent = crawler_requests
    await crawler.fetch_check_live_alive(CheckLiveAlive(room_ids="1"))
    await crawler.close()

    [request] = sent
    params = dict(query_params(str(request.url)))
    assert request.url.host == "webcast.tiktok.com"
    assert "X-Gnarly" not in params
    assert len(params["X-Bogus"]) == 28

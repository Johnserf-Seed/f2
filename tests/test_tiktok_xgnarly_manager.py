# path: tests/test_tiktok_xgnarly_manager.py

from urllib.parse import quote, urlsplit

import httpx
import pytest

from f2.apps.tiktok.crawler import TiktokCrawler
from f2.apps.tiktok.model import CheckLiveAlive, LiveImFetch, UserPost
from f2.apps.tiktok.proto.tiktok_webcast_pb2 import Response
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
    # 与网页一样按 RFC 3986 编码，括号、斜杠也会编码
    assert "&browser_version=5.0%20%28" in url
    assert f"&tz_name={quote(params['tz_name'], safe='')}&" in url


def test_query_hash_covers_the_encoded_query():
    # 2026-09-26 抓包：0x2E 是实际发送的业务查询串（编码后）的哈希
    params = {"keyword": "猫 (cat)", "root_referer": "https://www.tiktok.com/"}
    url = XGnarlyManager.model_2_endpoint(UA, USER_POST, params)
    query = urlsplit(url).query
    business = query[: query.index("&X-Dynosaur=")]
    assert business == (
        "keyword=%E7%8C%AB%20%28cat%29&root_referer=https%3A%2F%2Fwww.tiktok.com%2F"
    )
    payload, _key = unseal(dict(query_params(url))["X-Dynosaur"])
    assert unpack_payload(payload)[0x2E] == hash_state(business).to_bytes(4, "big")


def test_webcast_models_carry_raw_values_without_ms_token():
    # webcast 接口与 www 接口一样使用新版签名，模型保存原始值
    check = CheckLiveAlive(room_ids="1").model_dump()
    im = LiveImFetch(room_id="1").model_dump()
    assert "msToken" not in check and "msToken" not in im
    assert " (" in check["browser_version"] and " (" in im["browser_version"]
    assert im["host"] == "https://webcast.tiktok.com"
    url = XGnarlyManager.model_2_endpoint(UA, "https://webcast.tiktok.com/x/", im)
    assert "&host=https%3A%2F%2Fwebcast.tiktok.com&" in url


# ---------------- 爬虫 ----------------


def make_crawler(sent, cookie="ttwid=x; msToken=cookie_token"):
    def handler(request):
        sent.append(request)
        if request.url.path == "/webcast/im/fetch/":
            return httpx.Response(
                200, content=Response(cursor="c1").SerializeToString()
            )
        return httpx.Response(200, json={"statusCode": 0})

    crawler = TiktokCrawler(
        {
            "headers": {"User-Agent": UA, "Referer": "https://www.tiktok.com/"},
            "cookie": cookie,
            "proxies": {"http://": None, "https://": None},
        }
    )
    crawler._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return crawler


@pytest.fixture(autouse=True)
def forbid_mstoken_generation(monkeypatch):
    # 旧的 msToken 生成接口已失效，TikTok 的任何请求都不应再调用
    def gen_real_msToken(cls):
        raise AssertionError("不应生成 msToken")

    monkeypatch.setattr(TokenManager, "_msToken_cache", None)
    monkeypatch.setattr(TokenManager, "gen_real_msToken", classmethod(gen_real_msToken))


@pytest.fixture
def crawler_requests():
    sent = []
    return make_crawler(sent), sent


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


async def test_webcast_requests_use_new_signature(crawler_requests):
    crawler, sent = crawler_requests
    await crawler.fetch_check_live_alive(CheckLiveAlive(room_ids="1"))
    await crawler.close()

    [request] = sent
    params = dict(query_params(str(request.url)))
    assert request.url.host == "webcast.tiktok.com"
    # 2026-09-26 实测 im/fetch 只用 X-Bogus 签名时返回空内容，webcast 接口也改用新版签名
    assert params["X-Bogus"] == "1" and params["X-Gnarly"]
    assert params["msToken"] == "cookie_token"
    names = [name for name, _value in query_params(str(request.url))]
    assert names[-5:] == ["room_ids", "X-Dynosaur", "msToken", "X-Bogus", "X-Gnarly"]


async def test_webcast_im_fetch_uses_new_signature(crawler_requests):
    crawler, sent = crawler_requests
    response = await crawler.fetch_live_im_fetch(LiveImFetch(room_id="1"))
    await crawler.close()

    assert response.cursor == "c1"
    [request] = sent
    params = query_params(str(request.url))
    assert request.url.path == "/webcast/im/fetch/"
    assert [value for name, value in params if name == "msToken"] == ["cookie_token"]
    assert dict(params)["X-Gnarly"]


async def test_webcast_mstoken_is_empty_without_cookie_value():
    sent = []
    crawler = make_crawler(sent, cookie="ttwid=x")
    await crawler.fetch_check_live_alive(CheckLiveAlive(room_ids="1"))
    await crawler.close()

    assert "&msToken=&X-Bogus=1&X-Gnarly=" in str(sent[0].url)

# path: tests/test_douyin_gateway_headers.py

# 用例参考社区 PR #446（OrdinaryFolk01），并补充游客 cookie、UIFID_TEMP 回退与大小写覆盖场景

import pytest

from f2.apps.douyin.crawler import DouyinCrawler
from f2.apps.douyin.utils import GatewayHeaderManager
from f2.utils.http.cookie import parse_cookie_str


def build_crawler(cookie, headers=None):
    return DouyinCrawler(
        {
            "headers": headers
            or {"User-Agent": "f2-test", "Referer": "https://www.douyin.com/"},
            "cookie": cookie,
            "proxies": {"http://": None, "https://": None},
        }
    )


def test_parse_cookie_str_keeps_equal_signs_and_skips_invalid_parts():
    cookies = parse_cookie_str(" a=1; b=x=y ;flag; =bad; c= 3 ")
    assert cookies == {"a": "1", "b": "x=y", "c": "3"}


def test_parse_cookie_str_rejects_non_string():
    with pytest.raises(TypeError):
        parse_cookie_str(None)  # type: ignore[arg-type]


@pytest.mark.parametrize("cookie", [None, "", "ttwid=guest; s_v_web_id=verify"])
def test_argus_header_is_sent_even_without_uifid(cookie):
    # 网关只校验 x-tt-argus 是否存在：没有 UIFID 的游客 cookie 也必须带上它
    assert GatewayHeaderManager.gen_gateway_headers(cookie) == {
        "x-tt-argus": GatewayHeaderManager.ARGUS_PLACEHOLDER
    }


def test_uifid_prefers_login_cookie_over_temp():
    headers = GatewayHeaderManager.gen_gateway_headers(
        "UIFID_TEMP=temp-id; sessionid=session; UIFID=login-id"
    )
    assert headers["uifid"] == "login-id"


def test_uifid_falls_back_to_uifid_temp_for_guests():
    headers = GatewayHeaderManager.gen_gateway_headers(
        "ttwid=guest; UIFID_TEMP=temp-id"
    )
    assert headers["uifid"] == "temp-id"


def test_configured_headers_take_precedence_case_insensitively():
    merged = GatewayHeaderManager.merge_headers(
        {"X-TT-Argus": "configured-argus", "Uifid": "configured-id"}, "UIFID=cookie-id"
    )
    lowered = [name.lower() for name in merged]
    # 同一个请求头不能因为大小写不同而发送两次
    assert lowered.count("x-tt-argus") == 1
    assert lowered.count("uifid") == 1
    assert merged["X-TT-Argus"] == "configured-argus"
    assert merged["Uifid"] == "configured-id"


def test_crawler_clients_send_gateway_headers():
    crawler = build_crawler("ttwid=guest; UIFID=login-id")
    for client in (crawler.aclient, crawler.client):
        assert client.headers["x-tt-argus"] == "1"
        assert client.headers["uifid"] == "login-id"
        assert client.headers["cookie"] == "ttwid=guest; UIFID=login-id"
        assert client.headers["user-agent"] == "f2-test"


def test_crawler_keeps_configured_gateway_headers():
    crawler = build_crawler(
        "UIFID=cookie-id",
        {"User-Agent": "f2-test", "x-tt-argus": "configured", "uifid": "configured-id"},
    )
    assert crawler.aclient.headers["x-tt-argus"] == "configured"
    assert crawler.aclient.headers["uifid"] == "configured-id"

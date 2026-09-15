from unittest.mock import patch

from f2.apps.douyin.crawler import DouyinCrawler
from f2.crawlers.base_crawler import BaseCrawler


def build_crawler(cookie, headers=None):
    kwargs = {
        "cookie": cookie,
        "headers": headers or {},
        "proxies": {"http://": None, "https://": None},
    }
    with patch.object(BaseCrawler, "__init__", return_value=None):
        return DouyinCrawler(kwargs)


def test_gateway_headers_are_derived_from_uifid_cookie():
    crawler = build_crawler("sessionid=session; UIFID=gateway-id; ttwid=browser")

    assert crawler.headers["uifid"] == "gateway-id"
    assert crawler.headers["x-tt-argus"] == "1"


def test_gateway_headers_are_omitted_without_uifid_cookie():
    crawler = build_crawler("sessionid=session; ttwid=browser")

    assert "uifid" not in crawler.headers
    assert "x-tt-argus" not in crawler.headers


def test_explicit_gateway_headers_take_precedence():
    crawler = build_crawler(
        "UIFID=cookie-id",
        {"uifid": "configured-id", "x-tt-argus": "configured-argus"},
    )

    assert crawler.headers["uifid"] == "configured-id"
    assert crawler.headers["x-tt-argus"] == "configured-argus"

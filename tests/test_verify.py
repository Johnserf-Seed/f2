# path: tests/test_verify.py

import inspect
import ssl

import pytest

from f2.crawlers.base_crawler import BaseCrawler
from f2.utils.http.proxy import check_proxy_avail
from f2.utils.http.utils import get_content_length
from f2.utils.version import is_outdated


def _verify_mode(transport) -> ssl.VerifyMode:
    return transport._pool._ssl_context.verify_mode


def test_verify_defaults_to_true():
    crawler = BaseCrawler({})
    assert crawler._verify is True
    for async_mode in (True, False):
        transport = crawler._create_mount(async_mode)["all://"]
        assert _verify_mode(transport) == ssl.CERT_REQUIRED


def test_verify_false_disables_certificate_check():
    crawler = BaseCrawler({"verify": False})
    assert crawler._verify is False
    for async_mode in (True, False):
        transport = crawler._create_mount(async_mode)["all://"]
        assert _verify_mode(transport) == ssl.CERT_NONE


def test_verify_applies_to_http_proxy_transport():
    crawler = BaseCrawler(
        {"verify": False}, proxies={"http://": "http://127.0.0.1:8080"}
    )
    transport = crawler._create_mount(async_mode=True)["all://"]
    assert _verify_mode(transport) == ssl.CERT_NONE


def test_helpers_default_to_verifying():
    assert inspect.signature(check_proxy_avail).parameters["verify"].default is True
    assert inspect.signature(get_content_length).parameters["verify"].default is True


@pytest.mark.parametrize(
    "current, latest, expected",
    [
        ("0.0.1.7", "0.0.1.10", True),
        ("0.0.1.7", "0.0.1.7", False),
        ("0.0.1.8", "0.0.1.7", False),
        ("0.0.1.8rc1", "0.0.1.8", True),
        ("0.0.1.8", "0.0.1.8.dev1", False),
        ("v0.0.1.8-pw3", "0.0.1.8", None),
    ],
)
def test_is_outdated(current, latest, expected):
    assert is_outdated(current, latest) is expected

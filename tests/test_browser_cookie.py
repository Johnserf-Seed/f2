# path: tests/test_browser_cookie.py

from types import SimpleNamespace

import browser_cookie3
import pytest

from f2.log.redact import redact_text
from f2.utils.http import browser as browser_module
from f2.utils.http.browser import get_cookie_from_browser

KEY_ERROR = "Unable to get key for cookie decryption"
LOCKED_ERROR = "Unable to read database file"


def fake_chrome(monkeypatch, result):
    """替换 browser_cookie3.chrome，测试不会读取真实的浏览器"""

    def chrome(domain_name=""):
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(browser_module.browser_cookie3, "chrome", chrome)


def browser_error(monkeypatch, message):
    fake_chrome(monkeypatch, browser_cookie3.BrowserCookieError(message))
    with pytest.raises(browser_cookie3.BrowserCookieError) as exc_info:
        get_cookie_from_browser("chrome", "douyin.com")
    return str(exc_info.value)


def test_decryption_key_error_suggests_alternatives(monkeypatch):
    # #193：新版 Chrome、Edge 在 Windows 上改用应用绑定加密，此前只显示英文原因
    message = browser_error(monkeypatch, KEY_ERROR)
    assert message.startswith(KEY_ERROR)
    assert "--auto-cookie firefox" in message
    assert "https://f2.wiki/faq" in message
    assert redact_text(message) == message


def test_locked_database_asks_to_close_browser(monkeypatch):
    message = browser_error(monkeypatch, LOCKED_ERROR)
    assert message.startswith(LOCKED_ERROR)
    assert "关闭浏览器" in message


def test_other_errors_are_kept(monkeypatch):
    assert browser_error(monkeypatch, "Can not find cookie file") == (
        "Can not find cookie file"
    )


def test_cookies_are_filtered_by_domain(monkeypatch):
    fake_chrome(
        monkeypatch,
        [
            SimpleNamespace(name="sessionid", value="a", domain=".douyin.com"),
            SimpleNamespace(name="ttwid", value="b", domain="www.douyin.com"),
            SimpleNamespace(name="other", value="c", domain=".example.com"),
        ],
    )
    assert get_cookie_from_browser("chrome", "douyin.com") == {
        "sessionid": "a",
        "ttwid": "b",
    }

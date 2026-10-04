# path: tests/test_redact.py

import logging

import pytest

from f2.log.logger import logger, trace_logger
from f2.log.redact import (
    SecretRedactFilter,
    is_sensitive_key,
    mask_secret,
    redact_config,
    redact_text,
)

COOKIE = "ttwid=1%7Cabcdefghijklmnopqrstuvwxyz; msToken=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789; sessionid=deadbeefcafebabe"


def test_mask_secret_keeps_only_prefix_and_length():
    assert mask_secret("abcdefghijkl") == "abcd***(len=12)"
    assert "efghijkl" not in mask_secret("abcdefghijkl")
    # 太短的值整体打码，避免暴露
    assert mask_secret("short") == "***"
    assert mask_secret(None) == "***"


def test_is_sensitive_key():
    assert all(
        is_sensitive_key(k)
        for k in (
            "cookie",
            "Cookie",
            "key",
            "token",
            "X-Csrf-Token",
            "api_key",
            "msToken",
        )
    )
    assert not any(is_sensitive_key(k) for k in ("mode", "url", "keyword", "timeout"))


def test_redact_config_masks_secrets_and_keeps_other_values():
    kwargs = {
        "mode": "post",
        "url": "https://www.douyin.com/user/xxx",
        "cookie": COOKIE,
        "headers": {"User-Agent": "UA", "Cookie": COOKIE, "Referer": "https://x/"},
        "proxies": {"http://": "http://alice:s3cret@127.0.0.1:8080", "https://": None},
        "key": "bark-key-placeholder-aaaaaaaaaaaaaaaa",
        "token": None,
        "timeout": 10,
        "nested": [{"password": "hunter2hunter2"}],
    }
    redacted = redact_config(kwargs)

    text = str(redacted)
    for secret in (
        "abcdefghijklmnopqrstuvwxyz",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "deadbeef",
        "s3cret",
        "aaaaaaaaaaaaaaaa",
        "hunter2",
    ):
        assert secret not in text
    assert redacted["mode"] == "post"
    assert redacted["url"] == kwargs["url"]
    assert redacted["headers"]["User-Agent"] == "UA"
    assert redacted["headers"]["Referer"] == "https://x/"
    assert redacted["proxies"]["http://"] == "http://***:***@127.0.0.1:8080"
    assert redacted["proxies"]["https://"] is None
    assert redacted["token"] is None  # 未配置的项保持原样，便于排查
    assert redacted["timeout"] == 10
    # 原对象不被修改
    assert kwargs["cookie"] == COOKIE


def test_redact_text_patterns():
    assert (
        redact_text("socks5://user:pw123@10.0.0.1:1080")
        == "socks5://***:***@10.0.0.1:1080"
    )
    masked_cookie = redact_text(COOKIE)
    assert "abcdefghijklmnopqrstuvwxyz" not in masked_cookie
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ" not in masked_cookie
    assert "deadbeefcafebabe" not in masked_cookie
    assert masked_cookie.startswith("ttwid=1%7C***")
    assert redact_text("生成 ttwid：1234567890abcdef") == "生成 ttwid：1234***(len=16)"
    assert redact_text("设备密钥：0123456789abcdef") == "设备密钥：0123***(len=16)"
    # 普通文本不受影响
    assert (
        redact_text("下载完成：3 个作品，模式 post") == "下载完成：3 个作品，模式 post"
    )


def test_f2_loggers_redact_before_propagation(caplog):
    assert any(isinstance(f, SecretRedactFilter) for f in logger.filters)
    assert any(isinstance(f, SecretRedactFilter) for f in trace_logger.filters)

    with caplog.at_level(logging.DEBUG, logger="f2"):
        logger.debug("cookie=%s 代理 %s", COOKIE, "http://bob:passw0rd@proxy:3128")

    # caplog 挂在 root 上，能拿到的记录已经是脱敏后的
    assert "abcdefghijklmnopqrstuvwxyz" not in caplog.text
    assert "passw0rd" not in caplog.text
    assert "http://***:***@proxy:3128" in caplog.text


# ---------------- 各平台的登录 cookie ----------------

SECRET = "SECRETVALUE0123456789"
LOGIN_COOKIES = {
    "推特": ["auth_token", "ct0", "kdt", "twid"],
    "微博": ["SUB", "SUBP", "SRT", "SRF", "SCF", "WBPSESS"],
    "抖音与 TikTok": [
        "sessionid_ss",
        "sid_tt",
        "sid_guard",
        "uid_tt",
        "sid_ucp_v1",
        "tt_chain_token",
        "tt_csrf_token",
        "multi_sids",
    ],
}


@pytest.mark.parametrize(
    "name", [name for names in LOGIN_COOKIES.values() for name in names]
)
def test_login_cookie_items_are_masked(name):
    # 此前这些字段在 cookie 串里原样输出
    masked = redact_text(f"{name}={SECRET}; IsDouyinActive=true")

    assert SECRET[4:] not in masked
    assert masked.startswith(f"{name}=SECR***")
    assert masked.endswith("; IsDouyinActive=true")
    assert is_sensitive_key(name)


@pytest.mark.parametrize(
    "text",
    [
        f"Cookie: guest_id=v1%3A{SECRET}; lang=en",
        f"{{'User-Agent': 'UA', 'Cookie': 'guest_id={SECRET}; lang=en'}}",
        f'{{"cookie": "guest_id={SECRET}; lang=en"}}',
        f"Set-Cookie: guest_id={SECRET}; Path=/; HttpOnly",
    ],
)
def test_whole_cookie_string_is_masked(text):
    # 整个 cookie 串打码，不依赖字段名单；请求头字典与 JSON 中带引号的写法此前不会匹配
    masked = redact_text(text)

    assert SECRET[4:] not in masked
    assert "lang=en" not in masked


def test_quoted_header_values_are_masked():
    headers = {"X-Csrf-Token": SECRET, "Authorization": f"Bearer {SECRET}"}

    masked = redact_text(str(headers))

    assert SECRET[4:] not in masked
    assert masked == (
        "{'X-Csrf-Token': 'SECR***(len=21)', 'Authorization': 'Bear***(len=28)'}"
    )


def test_masked_values_keep_their_length():
    # cookie 串整体打码后不会再按“名称=值”打码一次，长度信息保持正确
    cookie = f"cookie=sessionid={SECRET}; lang=en"

    assert redact_text(cookie) == "cookie=sess***(len=40)"


def test_words_that_only_look_like_cookie_names_are_kept():
    text = "Subtitle: hello; submit: ok; monkey: 1; 自动获取Cookie失败：浏览器被占用"

    assert redact_text(text) == text


def test_logged_headers_are_redacted(caplog):
    headers = {"Cookie": f"auth_token={SECRET}; ct0={SECRET}", "x-csrf-token": SECRET}

    with caplog.at_level(logging.DEBUG, logger="f2"):
        logger.debug("请求头：%s", headers)

    assert SECRET[4:] not in caplog.text

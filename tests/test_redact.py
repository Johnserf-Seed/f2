# path: tests/test_redact.py

import logging

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

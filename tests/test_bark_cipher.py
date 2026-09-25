# path: tests/test_bark_cipher.py

import json
import logging
import string
from base64 import b64decode

import pytest

from f2.apps.bark import handler as bark_handler
from f2.apps.bark.utils import generate_alphanumeric_bytes
from f2.utils.crypto.aes import AESEncryptionUtils

ALPHANUMERIC = set(string.ascii_letters + string.digits)
# 低熵占位密钥（AES128 需要 16 字节），避免被 gitleaks 当成真实密钥
KEY = "f2" * 8


class FakeCrawler:
    """记录加密通知的请求参数，不访问网络"""

    sent: list = []

    def __init__(self, kwargs):
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def cipher_bark_notification(self, params):
        FakeCrawler.sent.append(params)
        return {"code": 200, "message": "success", "timestamp": 1735660800}


@pytest.fixture
def fake_crawler(monkeypatch):
    FakeCrawler.sent = []
    monkeypatch.setattr(bark_handler, "BarkCrawler", FakeCrawler)
    return FakeCrawler


async def send_cipher(mode):
    kwargs = {
        "key": "device-key",
        "title": "F2",
        "body": "下载完成",
        "encryption": {
            "algorithm": "AES128",
            "mode": mode,
            "padding": "PKCS7",
            "key": KEY,
        },
    }
    return await bark_handler.BarkHandler(kwargs).cipher_bark_notification()


def decrypt(params, mode):
    iv = params.iv.encode("ascii") if params.iv else None
    aes = AESEncryptionUtils(
        key=KEY.encode(), algorithm="AES128", mode=mode, padding_scheme="PKCS7", iv=iv
    )
    return json.loads(aes.aes_decrypt(b64decode(params.ciphertext), iv=iv))


def f2_warnings(caplog):
    return [
        r for r in caplog.records if r.name == "f2" and r.levelno == logging.WARNING
    ]


def test_generate_alphanumeric_bytes_is_printable_ascii():
    value = generate_alphanumeric_bytes(256)
    text = value.decode("ascii")
    assert len(value) == 256
    assert set(text) <= ALPHANUMERIC
    # 256 个字符全是数字的概率可以忽略，出现字母说明不再只用数字
    assert any(c.isalpha() for c in text)
    assert generate_alphanumeric_bytes(0) == b""


def test_generate_alphanumeric_bytes_is_random():
    assert len({generate_alphanumeric_bytes(16) for _ in range(50)}) == 50


@pytest.mark.parametrize("mode, iv_length", [("CBC", 16), ("GCM", 12)])
async def test_cipher_notification_sends_alphanumeric_iv(
    fake_crawler, caplog, mode, iv_length
):
    with caplog.at_level(logging.DEBUG):
        result = await send_cipher(mode)

    assert result.code == 200
    params = fake_crawler.sent[-1]
    assert len(params.iv) == iv_length
    assert set(params.iv) <= ALPHANUMERIC
    # 12 位以上的随机字母数字不含字母的概率低于十亿分之一，不再只用数字
    assert any(c.isalpha() for c in params.iv)
    assert decrypt(params, mode)["body"] == "下载完成"
    assert f2_warnings(caplog) == []


async def test_cipher_notification_warns_on_ecb(fake_crawler, caplog):
    with caplog.at_level(logging.DEBUG):
        result = await send_cipher("ECB")

    assert result.code == 200
    params = fake_crawler.sent[-1]
    assert params.iv == ""
    assert decrypt(params, "ECB")["body"] == "下载完成"
    warnings = f2_warnings(caplog)
    assert len(warnings) == 1
    assert "ECB" in warnings[0].getMessage()

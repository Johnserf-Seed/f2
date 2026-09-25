# path: tests/test_xbogus.py

import hashlib

import pytest

from f2.utils.crypto.bytedance import xbogus as xbogus_module
from f2.utils.crypto.bytedance.xbogus import XBogus

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)
FIXED_TIME = 1700000000.0


def test_get_xbogus():
    xb = XBogus().getXBogus(
        "aweme_id=7196239141472980280&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333"
    )
    assert xb is not None


# ---------------- #389：短查询串按原始字符计算 ----------------


def double_md5(text):
    return list(hashlib.md5(hashlib.md5(text.encode()).digest()).digest())


@pytest.mark.parametrize(
    "query",
    [
        "aid=1988",  # #389 的原始场景：只有一个参数
        "aid=19881",  # 奇数长度
        "a",
        "",
        "abcdef0123456789",  # 看起来像十六进制，也必须按原文计算
        "0123456789abcdef0123456789abcdef",
        "aweme_id=7196239141472980280&aid=1128&version_name=23.5.0",
    ],
)
def test_md5_encrypt_hashes_raw_query(query):
    assert XBogus(UA).md5_encrypt(query) == double_md5(query)


def test_short_query_gets_signed():
    params, xb, user_agent = XBogus(UA).getXBogus("aid=1988")
    assert params == f"aid=1988&X-Bogus={xb}"
    assert len(xb) == 28
    assert set(xb) <= set(XBogus().character)
    assert user_agent == UA


def test_short_user_agent_gets_signed():
    # UA 经 RC4 与 base64 后不超过 32 个字符时，此前同样会被当成十六进制
    assert len(XBogus("f2").getXBogus("aid=1988")[1]) == 28


@pytest.mark.parametrize(
    "query, expected",
    [
        (
            "aweme_id=7196239141472980280&aid=1128&version_name=23.5.0"
            "&device_platform=android&os_version=2333",
            "DFSzswVY7OiANnTJtmWx-e9WX7jo",
        ),
        ("aid=1988&count=20&cursor=0&x=1234", "DFSzswVYtfxANnTJtmWx-e9WX7rS"),
    ],
)
def test_long_query_signature_unchanged(monkeypatch, query, expected):
    # 期望值由修复前的实现在同一时间戳下算出，保证正常请求的签名不变
    monkeypatch.setattr(xbogus_module.time, "time", lambda: FIXED_TIME)
    assert XBogus(UA).getXBogus(query)[1] == expected


@pytest.mark.parametrize("digest", ["abc", "zz"])
def test_md5_str_to_array_rejects_non_hex(digest):
    with pytest.raises(ValueError):
        XBogus().md5_str_to_array(digest)

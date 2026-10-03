# path: tests/test_webcast_signature.py

import hashlib

import pytest

from f2.apps.douyin.algorithm import webcast_signature as ws
from f2.apps.douyin.algorithm.webcast_signature import DouyinWebcastSignature


class FixedRandom:
    """按给定顺序返回随机数"""

    def __init__(self, values):
        self.values = list(values)

    def random(self):
        return self.values.pop(0)


def unpack(signature):
    """把签名还原成标志字节、密钥与解密后的 10 字节数据块"""
    value_of = {char: index for index, char in enumerate(ws._S1_ALPHABET[:64])}
    raw = bytearray()
    for i in range(0, len(signature), 4):
        value = 0
        for char in signature[i : i + 4]:
            value = value << 6 | value_of[char]
        raw += value.to_bytes(3, "big")
    flags, key = raw[0], raw[1]
    # RC4 加密与解密是同一个运算
    return flags, key, ws._rc4(bytes([key]), bytes(raw[2:]))


# 以下签名由 webmssdk 1.0.0.53 的 JavaScript 原版计算（用 Node.js 运行，Math.random 依次返回相同的数），
# 每条都在新的 SDK 实例中计算，签名计数为 1
SDK_VECTORS = [
    ("dfc40239294909a536d77ff9d213d92a", None, (0.1, 0.3, 0.4), "f42vnD1JBZT1xOXx"),
    # room_id=7382517534467115826、user_unique_id=7382524529011246630 对应的 stub
    ("d6eebaec4b994615e0a0302f98c27642", None, (0.11, 0.5, 0.25), "6pt0VCsxRZdeMI8M"),
    # 没有 stub 时按 32 个 0 计算
    ("", None, (0.0, 0.0, 0.0), "fDpl4KbkGEihqVPD"),
    # SDK 只识别小写十六进制，大写字母按 0 处理
    (
        "DFC40239294909A536D77FF9D213D92A",
        None,
        (0.99, 0.999, 0.999),
        "6MVnhJC2lIWo0orZ",
    ),
    # 没有 stub 时取 X-MS-PAYLOAD 的 md5
    ("", "直播弹幕", (0.3, 0.5, 0.6), "fsbNzWXLsUwtD4rL"),
    # 长度为奇数时忽略最后一个字符
    ("abc", None, (0.42, 0.42, 0.42), "f4zmVOkvEFksAlkm"),
]


@pytest.mark.parametrize("stub, payload, randoms, expected", SDK_VECTORS)
def test_frontier_sign_matches_sdk(stub, payload, randoms, expected):
    signer = DouyinWebcastSignature(rng=FixedRandom(randoms))
    assert signer.frontier_sign(stub or None, payload) == expected


def test_get_signature_matches_sdk():
    signer = DouyinWebcastSignature(rng=FixedRandom((0.11, 0.5, 0.25)))
    signature = signer.get_signature("7382517534467115826", "7382524529011246630")
    assert signature == "6pt0VCsxRZdeMI8M"


def test_signature_structure():
    stub = hashlib.md5(b"f2").hexdigest()
    signature = DouyinWebcastSignature().frontier_sign(stub)

    assert len(signature) == 16
    assert set(signature) <= set(ws._S1_ALPHABET[:64])

    flags, _, block = unpack(signature)
    # kWebsocket 为 1、initialized 为 0，只有第 4 位是随机的
    assert flags & 0xEF == 0x40
    assert len(block) == 10
    assert block[0] == 1
    assert block[1:4] == b"\0\0\0"
    assert block[4:6] == hashlib.md5(hashlib.md5(b"").digest()).digest()[14:]
    assert block[6:8] == hashlib.md5(bytes.fromhex(stub)).digest()[14:]
    checksum = 0
    for byte in block[:9]:
        checksum ^= byte
    assert block[9] == checksum


def test_counter_increments_and_wraps():
    signer = DouyinWebcastSignature()
    counters = [unpack(signer.frontier_sign("0" * 32))[2][0] for _ in range(65)]

    assert counters[:3] == [1, 2, 3]
    # 计数只取低 6 位
    assert counters[62:] == [63, 0, 1]


def test_random_parts_change_between_calls():
    signer = DouyinWebcastSignature()
    assert len({signer.frontier_sign("0" * 32) for _ in range(20)}) > 1


def test_user_agent_is_not_accepted():
    # 签名计算从未用到 UA，构造时不再接受该参数，按位置传入会直接报错而不是被当成随机数来源
    with pytest.raises(TypeError):
        DouyinWebcastSignature("Mozilla/5.0")  # type: ignore[misc]


@pytest.mark.parametrize(
    "text, expected",
    [("0aff", b"\x0a\xff"), ("0AFF", b"\x00\x00"), ("abc", b"\xab"), ("", b"")],
)
def test_hex_decode_like_sdk(text, expected):
    assert ws._hex_decode(text) == expected


def test_encode_s1_padding():
    assert ws._encode_s1(b"") == ""
    assert ws._encode_s1(b"\x01").endswith("==")
    assert ws._encode_s1(b"\x01\x02").endswith("=")
    assert len(ws._encode_s1(b"\x01\x02\x03")) == 4

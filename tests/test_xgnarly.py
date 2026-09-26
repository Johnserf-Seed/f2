# path: tests/test_xgnarly.py

import hashlib

import pytest

from f2.utils.crypto.bytedance import xgnarly
from f2.utils.crypto.bytedance.xgnarly import (
    XGnarly,
    decode_field,
    encode_query,
    hash_state,
    sign,
    unpack_payload,
    unseal,
)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
)

# 固定输入与期望值由原始实现生成，该实现已与真实 SDK 逐字节核对
CASES = {
    "plain": dict(
        pairs=[
            ("aid", "1988"),
            ("count", "35"),
            ("cursor", "0"),
            ("secUid", "MS4wLjABAAAA"),
        ],
        ms_token="",
        body=b"",
        timestamp=1758000000,
        nonce=123456789,
        nonce2=987654321,
        sequence=1,
        key=tuple(range(1, 13)),
        key2=tuple(range(101, 113)),
    ),
    "escaped": dict(
        pairs=[
            ("keyword", '猫 cat (test) "q" #1'),
            ("tz_name", "Asia/Hong_Kong"),
            ("root_referer", "https://www.tiktok.com/"),
        ],
        ms_token="token-abc_123==",
        body=b"",
        timestamp=1758000123,
        nonce=4000000000,
        nonce2=17,
        sequence=2,
        key=tuple(0xFFFFFFFF - i for i in range(12)),
        key2=tuple(i * 0x01010101 for i in range(12)),
    ),
    "body": dict(
        pairs=[("aid", "1988"), ("item_id", "7300000000000000000")],
        ms_token="",
        body=b'{"a":1}',
        timestamp=1758009999,
        nonce=1,
        nonce2=2,
        sequence=3,
        key=tuple(0x12345678 + i for i in range(12)),
        key2=tuple(0x9ABCDEF0 - i for i in range(12)),
    ),
}

EXPECTED = {
    "plain": {
        "X-Dynosaur": (
            "MKeqYIvK9BOqLIYRiSvtpA6yV/AK63X-p2GwW71KTAF-RgSllWhYhMDF9DOE8a/g2jRl62UlCKI/"
            "ROZ2BX3J6nyU-VI0uuuuuIuuuueuuuubuuuu0ZuuuuAuuuuUuuuu9uuuuuWuuuuDuuuu9kuuuuku"
            "uu0YdqP3dUApVwJrExS1VUzG4Pe02Y9XjmbTR0HiFCpQJrbPrfkR/ZN7/vgcA4OMMv/fsymv8MDk"
            "2/A0Y6w9Po8A71s5Pim9Ud7E5EyuILC/l7saMKlzUG4rRHmahDfAxXPhyeM3I0Ts9hrn24DpVNUG"
            "oiOr4Rd1X49c7hQspFRoF5jOv0Ix846b6qz1Ff7Z0IIQClfvJE19w9ibu1drEK4zKXK8oLmTNMbl"
            "/xYZug8FWwWiVB-f"
        ),
        "X-Gnarly": (
            "MPrYf/b5r7KrZYupazYWoib00NLTmSOQzuA0Lk2f/A1oI1aQ0jNhWeS0o45ZNYS4uuuuoIuuu3nu"
            "uu0GuuuuhZuuu3Guuu0juuuuTuuuu3Ruuu0iuuuuTkuuuUuuuu0/eNxp8S/6eFGvJixTpXbmw0yZ"
            "iDuqlSzpgcn17Pn2CyKkD4HoLyK37z/Z6hd4kvhpbug6b76G0j-S9aUr7-1RtwZ1BghGYP-fToce"
            "cuqv2t1FG8FZCNTINrDaCmywRf8-mvVqX9kt9rN44XDD0foO1hWV9TFMpbRF6JerVIMJuehvjL3R"
            "UndjySXXVlBx83eEZ9w="
        ),
    },
    "escaped": {
        "X-Dynosaur": (
            "MFiiZ-yKH1q-qG2Zoxzp6kyR3jFhysa/ht1V/u/4Nhdq8EZjKPfGUIuJi3EN3WeHnauxBshLKwZL"
            "RcEFCjWXk8S7fd7oa2ft8gwq0pZBhfnmrjmNL0Or3Zzyyi/eGz3R0dqqaiwSQQql0w/v5yZ6FxG7"
            "XIOoGZ7Xkzjvyc2Su18m4XzUbaNgb/AamSnAPPPPPPHPPPPaPPPPP-PPPPyPPPPKPPPPcdPPPPlP"
            "PPP5PPPPayPPPPsPPPPRPPPPcuf34mISDMocbhFY2ty3bkhHtOpb80SRqXvRR3CLMV6UtuEvTaaY"
            "NOSbN/Zx9cDr5b-CqDfIxgCbEvQ2Z5o7bAWX6hihxw7RPeKS5Myh1aTUrh4i7upCsj7K/qNHN2-p"
            "nU85krpibNWLNeHG9Z=="
        ),
        "X-Gnarly": (
            "MHf0-aFe78M0Kdb/PXX8hxZFd0/oYgYkyyA/GJPOOVRlnanxEMvmSkVVXGocurTLtjkRr6AUEisS"
            "AR22RpaMob7ydN258VsfWx-pXxiobogYrDHukkE4IlZCNj9Fuuuuuub0uZb9uIv9uketukZb0uZS"
            "0ZzS0IA30InU0knv9uIv9ZWg9ZGD9IGE9kfEsgHUIULSVPDUVFH2PHylYrJ3EK5ZdqcYR9AF2u7k"
            "s3UzAMHpvaCaK9IrhApIHXL09n/oYn2g4fsIe8slLexZu3LyeLEFgJu74lJ11xTksdHHdUwgZ9lW"
            "kxJW24ZFRhU4uO-tq2f="
        ),
    },
    "body": {
        "X-Dynosaur": (
            "MRUEYpkcCOmJdFdI0xp1VUvu-kORVwskrnLz0iLiJ1xlmbnF2lHZvUMWH8VRBaesEb55LqZ8q1mO"
            "a9nuSb8ZqyEx2JWE8OZewfyz0ItijSpPj07hp5dQ9EaVavN3fCO4IAj765Np60gxLlZMm4ARb2Yp"
            "60gwLlZMdLARb2xp60gPLlZMISARbGSp60D9LlZMICARbGlihqieCqUP9M4GaBkiIDKPQVPU-7UT"
            "ZTn04uWZVletB419kMd/PfLpRq-JLgIDuYH3bhiCKttCWwsUsNKhBxictMTfT4IM-epHFafy-P5R"
            "H3Y6SEbkU80xCHmbCod4iEsWGSF5Wv9Vaw0FDV6CM0m6UWzJMkgzsExDz9hG61HkZOeoZrLGSKgg"
            "vteHAgFurk=="
        ),
        "X-Gnarly": (
            "MKOw2uJHvDNkgxifkwbL5iy5igXohGHszxm/aYYnT7twD3gEikjRr-OE5VgT5w/ulD02Z4xR2dy5"
            "DBfsnODfb0qlPmexkyJ3i-T5RBWn1vZa3dwHFjhOtHztKTVw1rVnG2fHtev4KJmrpDQNtsyAkXMY"
            "lsDDHW6jEnP4587tDKT6A2HFNqml6qQEFvv-QnG4TLFlkrAo9I4tSHcCqSVuHWOPX6OnLbG9-USO"
            "Laev-L-lM5XXTeFzoUglrDP-52M1frUk5jJhHaKw1iHmygjY5jJhH6Kw1iymygjB5jJhK7Kw1ilm"
            "ygj25jJhxYKw1ismygG="
        ),
    },
}


def signed(case):
    params = dict(CASES[case])
    return sign(params.pop("pairs"), UA, **params)


# ---------------- 固定向量 ----------------


@pytest.mark.parametrize("case", sorted(CASES))
def test_signatures_match_reference(case):
    query, params = signed(case)
    assert params["X-Dynosaur"] == EXPECTED[case]["X-Dynosaur"]
    assert params["X-Gnarly"] == EXPECTED[case]["X-Gnarly"]
    assert params["X-Bogus"] == "1"
    assert params["msToken"] == CASES[case]["ms_token"]
    assert query == (
        f"{encode_query(CASES[case]['pairs'])}"
        f"&X-Dynosaur={params['X-Dynosaur']}&msToken={params['msToken']}"
        f"&X-Bogus=1&X-Gnarly={params['X-Gnarly']}"
    )


def test_class_delegates_to_sign():
    params = dict(CASES["escaped"])
    pairs = params.pop("pairs")
    assert XGnarly(UA).sign(pairs, **params) == sign(pairs, UA, **params)


# ---------------- 查询串编码 ----------------


def test_encode_query_escapes_like_a_browser():
    query = encode_query(
        [
            ("browser_version", "5.0 (Windows NT 10.0; Win64; x64)"),
            ("root_referer", "https://www.tiktok.com/"),
            ("q", '"<>`#'),
            ("k", "猫"),
            ("c", "a\tb"),
        ]
    )
    assert query == (
        "browser_version=5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)"
        "&root_referer=https://www.tiktok.com/"
        "&q=%22%3C%3E%60%23"
        "&k=%E7%8C%AB"
        "&c=a%09b"
    )


# ---------------- 解开签名后逐字段核对 ----------------


def test_dynosaur_binds_query_and_user_agent():
    case = CASES["escaped"]
    _query, params = signed("escaped")
    payload, key = unseal(params["X-Dynosaur"])
    assert key == case["key"]
    fields = unpack_payload(payload)
    assert sorted(fields) == list(range(0x20, 0x39))
    assert fields[0x2E] == hash_state(encode_query(case["pairs"])).to_bytes(4, "big")
    assert fields[0x30] == hash_state(UA).to_bytes(4, "big")
    encoder = xgnarly._ENCODER_A
    assert decode_field(fields[0x27], encoder) == str(case["timestamp"])
    assert decode_field(fields[0x34], encoder) == str(case["nonce"])
    assert decode_field(fields[0x25], encoder) == str(case["sequence"])
    assert decode_field(fields[0x35], encoder) == xgnarly.PAGE
    assert decode_field(fields[0x2A], encoder) == xgnarly.SDK_VERSION
    assert decode_field(fields[0x31], encoder) == xgnarly.SCM_VERSION


def test_gnarly_seals_query_with_dynosaur_and_token():
    case = CASES["escaped"]
    query, params = signed("escaped")
    payload, key = unseal(params["X-Gnarly"])
    assert key == case["key2"]
    fields = unpack_payload(payload, lead_count=True)
    sealed = query.split("&X-Bogus=")[0]
    assert fields[0x03] == hashlib.md5(sealed.encode()).hexdigest().encode()
    assert fields[0x04] == hashlib.md5(case["body"]).hexdigest().encode()
    assert fields[0x05] == hashlib.md5(UA.encode()).hexdigest().encode()
    assert int.from_bytes(fields[0x06], "big") == case["timestamp"]
    assert int.from_bytes(fields[0x0F], "big") == case["nonce2"]
    assert 0x07 not in fields


def test_random_keys_still_round_trip():
    query, params = sign([("aid", "1988")], UA, ms_token="t")
    assert query.endswith(f"&X-Bogus=1&X-Gnarly={params['X-Gnarly']}")
    for token in (params["X-Dynosaur"], params["X-Gnarly"]):
        payload, key = unseal(token)
        assert payload and len(key) == 12


@pytest.mark.parametrize("token", ["", "AAAA"])
def test_unseal_rejects_non_signatures(token):
    with pytest.raises(ValueError):
        unseal(token)

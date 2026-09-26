# path: f2/utils/crypto/bytedance/xgnarly.py

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description:xgnarly.py
@Date       :2026/09/26 00:00:00
@Author     :JohnserfSeed
@version    :0.0.1
@License    :Apache License 2.0
@Github     :https://github.com/johnserf-seed
@Mail       :support@f2.wiki
-------------------------------------------------
Change Log  :
2026/09/26 00:00:00 - 纯 Python 实现 TikTok 网页 SDK（webmssdk 2.0.0.561）的 X-Dynosaur 与 X-Gnarly
-------------------------------------------------
"""

import base64
import hashlib
import random
import time
from typing import (
    Dict,
    Final,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from f2.i18n.translator import _

MASK32: Final = 0xFFFFFFFF

# 查询参数按网页 SDK 追加的顺序排列。顺序由平台决定：X-Gnarly 覆盖了追加 X-Dynosaur
# 与 msToken 之后的查询串，签名后再调整顺序，服务器收到的就不是被签名的字节
DYNOSAUR_PARAM: Final = "X-Dynosaur"
MS_TOKEN_PARAM: Final = "msToken"
BOGUS_PARAM: Final = "X-Bogus"
GNARLY_PARAM: Final = "X-Gnarly"

# HTTP 请求中的 X-Bogus 固定为字符串 "1"。完整计算的 X-Bogus（见 xbogus.py）只出现在
# SDK 的 frontierSign() 生成的 websocket 握手中，HTTP 请求带上它反而是网页从不发送的参数组合
BOGUS_VALUE: Final = "1"

# 自定义 base64 字母表，与标准字母表按位置一一对应，原样出现在 SDK 解码后的字符串表中。
# 两个签名都使用它；字符串表里的另一张字母表属于 X-Bogus，这里用不到
ALPHABET: Final = "u09tbS3UvgDEe6r-ZVMXzLpsAohTn7mdINQlW412GqBjfYiyk8JORCF5/xKHwacP"
_STANDARD: Final = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_TO_CUSTOM: Final = str.maketrans(_STANDARD, ALPHABET)
_FROM_CUSTOM: Final = str.maketrans(ALPHABET, _STANDARD)

# 信封的第一个字节，位于插入了密钥的密文之前
ENVELOPE_TAG: Final = 0x4B

# ChaCha 状态的第 0～3 个字。不是标准的 "expand 32-byte k" 常量，而是 SDK 中的值
CHACHA_INIT: Final = (1196819126, 600974999, 3863347763, 1451689750)

# FNV-1a 32 位变体：偏移基数非标准，且每个字节额外乘 33。两个常量都来自 SDK
FNV_OFFSET: Final = 2166136260
FNV_PRIME: Final = 16777619

# 载荷中携带的版本号，来自 SDK 2.0.0.561。它们是数据而不是装饰：2.0.0.514 携带的是
# "5.3.1"/"2.0.0.514" 且字段表不同，SDK 升级后需要重新核对
SDK_VERSION: Final = "5.3.2"
SCM_VERSION: Final = "2.0.0.561"

# 载荷上报的环境指纹，取自真实浏览器。
#
# 整个载荷中只有这两个值会被服务器校验，而且写错时没有任何提示：除 /api/post/item_list/
# 以外的接口都会正常响应签名有误的请求；item_list 则返回 200、空内容并带 tt_orcas_res: 1
# 响应头，看起来和被拦截的路径一模一样。用 Node 驱动真实 SDK 的最小 DOM 环境得到的是
# 129 与 14，Chrome 实际抓取的是 65 与 8，只改这两个值就能让 item_list 返回完整内容。
# 这两个值要以浏览器抓包为准，不能以模拟环境为准
ENV_CODE: Final = 65
UB_CODE: Final = 8

# X-Dynosaur 的 0x38 字段。在 SDK 2.0.0.514 与 2.0.0.561 之间、以及各种环境改动
# （UA、屏幕、位置、有无 canvas）下都不变，属于 SDK 构建本身而不是机器。它是 SDK 内部
# 某个 md5 的 hash_state，该 md5 的输入从不经过 TextEncoder 或 charCodeAt，没能还原；
# 值与环境无关，所以直接使用观测值是安全的
VM_STATE_HASH: Final = 0xC46CE353

# canvas 指纹。"-1" 表示没有 canvas，即没有 2d 上下文的页面上报的值。这是载荷中最明显的
# 机器特征，写成具名常量，以便 TikTok 日后开始校验时换成每个身份固定的值
CANVAS_HASH: Final = "-1"

# 另外三个模拟环境无法生成的字段，暂时固定为 "0"。真实浏览器在 0x28 上报一个 32 位哈希，
# 0x32 上报组件版本字符串，0x33 上报一个 md5
WEBGL_HASH: Final = "0"
COMPONENT_VERSION: Final = "0"
DEVICE_HASH: Final = "0"

# SDK 认为自己所在页面的 location.host + location.pathname。把模拟环境指向视频页时
# 这个字段会随之变化；没有页面的客户端如实上报首页
PAGE: Final = "www.tiktok.com/"

# SDK 从 1 开始统计自己的签名次数，并写入四个字段。新页面签第一个请求时上报 1，
# 每次请求都是新身份的客户端就是这种情况
CALL_SEQUENCE_START: Final = 1

# 空请求体的 md5，GET 请求都是这个值。SDK 的字符串表中也有这个字面量
EMPTY_BODY_MD5: Final = "d41d8cd98f00b204e9800998ecf8427e"

# SDK 的两种字节编码参数 (xor_base, add_base, pre_xor, rot, post_add)。
# A 用于除校验和以外的所有字段；B 用于校验和与三个标志位
_ENCODER_A: Final = (103, 1, None, 2, 1)
_ENCODER_B: Final = (102, 0, 165, 1, 0)

# 签名信封中插入的密钥字数，与 _random_key 生成的数量一致
KEY_WORDS: Final = 12

# 浏览器在查询串中只会转义这几个字符。Chrome 对括号、斜杠、冒号、逗号等都保持原样，
# # 会开始片段，所以也要转义
_MUST_ESCAPE: Final = {
    " ": "%20",
    '"': "%22",
    "<": "%3C",
    ">": "%3E",
    "`": "%60",
    "#": "%23",
}

EncoderConfig = Tuple[int, int, Optional[int], int, int]


def encode_query(pairs: Iterable[Tuple[str, str]]) -> str:
    """
    按浏览器的方式序列化业务参数 (Serialize business parameters as a browser does)

    这不是 urlencode。X-Dynosaur 的 0x2E 字段是查询串的 hash_state，SDK 计算的是浏览器
    规范化之后的地址。Chrome 只把空格转义为 %20，括号、斜杠、冒号保持原样，所以真实页面
    计算的是 browser_version=5.0%20(Windows)&root_referer=https://www.tiktok.com/。
    如果全部百分号编码，得到的是另一个字符串、另一个哈希，签名绑定到了平台收不到的字节上；
    /api/user/detail/ 会校验这一点，而 /api/item/detail/、/api/comment/list/ 不校验，
    于是表现为只有一个接口不返回内容。

    计算哈希与实际发送的必须是同一个字符串，因此这里必须是唯一的编码入口。

    Args:
        pairs (Iterable[Tuple[str, str]]): 按平台顺序排列的业务参数

    Returns:
        str: 编码后的查询串
    """
    return "&".join(f"{_escape(key)}={_escape(value)}" for key, value in pairs)


def _escape(text: str) -> str:
    """
    只转义浏览器必须转义的字符，其余保持原样

    可打印 ASCII 除 _MUST_ESCAPE 中的几个外原样保留；控制字符与非 ASCII 字符按 UTF-8 字节
    百分号编码，与浏览器发送文本查询串时的行为一致。
    """
    out: List[str] = []
    for ch in text:
        if ch in _MUST_ESCAPE:
            out.append(_MUST_ESCAPE[ch])
        elif " " < ch <= "~":
            out.append(ch)
        else:
            out.extend(f"%{byte:02X}" for byte in ch.encode("utf-8"))
    return "".join(out)


def hash_state(text: str) -> int:
    """SDK 的 FNV-1a 变体：标准的一轮之后再乘 33 (The SDK's FNV-1a variant)"""
    value = FNV_OFFSET
    for byte in text.encode("utf-8"):
        step = ((value ^ byte) * FNV_PRIME) & MASK32
        value = (step + ((step * 32) & MASK32)) & MASK32
    return value


def _encode_bytes(text: str, config: EncoderConfig) -> bytes:
    """
    编码一个载荷字段：逐位置打乱字节、填充并带上长度

    输出至少 6 字节，以 0x00 和原始长度结尾，填充字节为 (221 + index) & 255。
    填充很重要：单字符字符串的第 1 个字节总是 0xDE，这让下面 X-Dynosaur 的校验和
    与被校验的内容无关、始终稳定。
    """
    xor_base, add_base, pre_xor, rotate, post_add = config
    size = max(len(text) + 2, 6)
    out = bytearray(size)
    for index, char in enumerate(text):
        value = (ord(char) ^ (xor_base + index)) & MASK32
        value = (value + add_base + (170 & index)) % 256
        if pre_xor is not None:
            value ^= pre_xor
        value = ((value << rotate) | (value >> (8 - rotate))) & 0xFF
        out[index] = ((value ^ 187) + post_add) % 256
    for index in range(len(text), size - 2):
        out[index] = (221 + index) & 0xFF
    out[size - 2] = 0
    out[size - 1] = len(text)
    return bytes(out)


def pack_payload(
    fields: Mapping[int, bytes],
    order: Optional[Sequence[int]] = None,
    *,
    lead_count: bool = False,
) -> bytes:
    """
    把字段排列为平台解析的 TLV 条目 (Lay out the fields as TLV entries)

    order 参数存在的原因是：X-Gnarly 的输出顺序是唯一推断而非实测的部分。SDK 输出 16 个
    字段的顺序在同一进程内稳定、换一个进程就不同，说明服务器按键解析而不依赖位置。
    默认按键升序；传入 order 可以逐字节复现抓到的签名，测试中就是这样用的。
    """
    keys = sorted(fields) if order is None else list(order)
    body = b"".join(bytes((key, 0, len(fields[key]))) + fields[key] for key in keys)
    return bytes((len(keys),)) + body if lead_count else body


def _be(value: int, size: int) -> bytes:
    return int(value).to_bytes(size, "big")


def _mix(timestamp: int, nonce: int, env_code: int) -> int:
    """把两个 32 位值折叠为 16 位，再在高位写入环境码"""
    folded = ((timestamp >> 16) ^ (nonce >> 16) ^ timestamp ^ nonce) & 0xFFFF
    return folded | (env_code << 16)


def _checksum(values: Sequence[Union[int, str]], mode: int) -> int:
    """
    对 X-Gnarly 字段值做异或折叠，初值为全 1

    两种模式只在字符串的处理上不同：模式 1 视为 0，模式 2 取前 4 个 UTF-8 字节按大端解析。
    初值为全 1，所以 SDK 输出的两个校验和都是普通折叠结果的补码。
    """
    accumulator = MASK32
    for value in values:
        if isinstance(value, str):
            number = (
                0 if mode == 1 else int.from_bytes(value.encode("utf-8")[:4], "big")
            )
        else:
            number = value
        accumulator ^= number & MASK32
    return accumulator & MASK32


def _quarter_round(state: List[int], a: int, b: int, c: int, d: int) -> None:
    state[a] = (state[a] + state[b]) & MASK32
    state[d] ^= state[a]
    state[d] = ((state[d] << 16) | (state[d] >> 16)) & MASK32
    state[c] = (state[c] + state[d]) & MASK32
    state[b] ^= state[c]
    state[b] = ((state[b] << 12) | (state[b] >> 20)) & MASK32
    state[a] = (state[a] + state[b]) & MASK32
    state[d] ^= state[a]
    state[d] = ((state[d] << 8) | (state[d] >> 24)) & MASK32
    state[c] = (state[c] + state[d]) & MASK32
    state[b] ^= state[c]
    state[b] = ((state[b] << 7) | (state[b] >> 25)) & MASK32


def _keystream(state: Sequence[int], rounds: int) -> List[int]:
    """
    生成一个 64 字节的密钥流块。这不是 ChaCha20，差异都会影响结果

    rounds 计的是单轮而非双轮，且取决于数据（5～20），奇数时在列轮之后退出；退出时机
    写错会让部分调用通过、部分失败，看起来像随机的限流而不像代码错误。对角轮的第三组是
    (2, 7, 12, 13)，标准实现是 (2, 7, 8, 13)——第 12 位出现了两次，几乎可以肯定是原实现
    的笔误，这里有意保持一致。
    """
    working = list(state)
    done = 0
    while done < rounds:
        _quarter_round(working, 0, 4, 8, 12)
        _quarter_round(working, 1, 5, 9, 13)
        _quarter_round(working, 2, 6, 10, 14)
        _quarter_round(working, 3, 7, 11, 15)
        done += 1
        if done >= rounds:
            break
        _quarter_round(working, 0, 5, 10, 15)
        _quarter_round(working, 1, 6, 11, 12)
        _quarter_round(working, 2, 7, 12, 13)
        _quarter_round(working, 3, 4, 13, 14)
        done += 1
    return [(working[i] + state[i]) & MASK32 for i in range(16)]


def _crypt(key: Sequence[int], rounds: int, payload: bytes) -> bytes:
    """
    把载荷按小端 uint32 读取，与密钥流异或

    计数器位于状态的第 12 个字，只有处理完一个完整的 16 字块后才递增，因此末尾不完整的块
    使用已经递增过的状态。这里的载荷都只有一个块，但循环写法与 SDK 保持一致。
    """
    state = [*CHACHA_INIT, *(word & MASK32 for word in key)]
    length = len(payload)
    word_count = (length + 3) // 4
    words = [
        int.from_bytes(payload[4 * i : 4 * i + 4].ljust(4, b"\0"), "little")
        for i in range(word_count)
    ]
    offset = 0
    while offset + 16 < word_count:
        block = _keystream(state, rounds)
        state[12] = (state[12] + 1) & MASK32
        for i in range(16):
            words[offset + i] ^= block[i]
        offset += 16
    block = _keystream(state, rounds)
    for i in range(word_count - offset):
        words[offset + i] ^= block[i]
    return b"".join(word.to_bytes(4, "little") for word in words)[:length]


def seal(payload: bytes, key: Sequence[int]) -> str:
    """加密、把密钥插回密文并编码 (Encrypt, splice the key back in, and encode)"""
    rounds = (sum(word & 0xF for word in key) & 0xF) + 5
    ciphertext = _crypt(key, rounds, payload)
    key_bytes = b"".join(int(word).to_bytes(4, "little") for word in key)
    position = (sum(key_bytes) + sum(ciphertext)) % (len(ciphertext) + 1)
    spliced = ciphertext[:position] + key_bytes + ciphertext[position:]
    raw = bytes((ENVELOPE_TAG,)) + spliced
    return base64.b64encode(raw).decode("ascii").translate(_TO_CUSTOM)


def unseal(token: str) -> Tuple[bytes, Tuple[int, ...]]:
    """
    从签名中还原 (载荷, 密钥) (Recover the payload and key from a signature)

    信封把密钥藏在密文中，位置由密钥与密文字节决定。服务器也要用同样的方法找回密钥，
    所以逐个尝试候选位置，满足这一关系的位置只有一个。

    这是核对本模块的唯一可靠依据：请以浏览器抓到的签名为准，用本函数解开后比对各字段。

    Args:
        token (str): X-Dynosaur 或 X-Gnarly 的值

    Returns:
        Tuple[bytes, Tuple[int, ...]]: 解密后的载荷与 12 个字的密钥

    Raises:
        ValueError: 不是签名信封，或找不到满足密钥关系的位置
    """
    raw = base64.b64decode(token.translate(_FROM_CUSTOM))
    if not raw or raw[0] != ENVELOPE_TAG:
        raise ValueError(_("不是有效的签名信封"))
    spliced = raw[1:]
    width = KEY_WORDS * 4
    for position in range(len(spliced) - width + 1):
        key_bytes = spliced[position : position + width]
        ciphertext = spliced[:position] + spliced[position + width :]
        if position != (sum(key_bytes) + sum(ciphertext)) % (len(ciphertext) + 1):
            continue
        key = tuple(
            int.from_bytes(key_bytes[4 * i : 4 * i + 4], "little")
            for i in range(KEY_WORDS)
        )
        rounds = (sum(word & 0xF for word in key) & 0xF) + 5
        return _crypt(key, rounds, ciphertext), key
    raise ValueError(_("找不到满足密钥关系的插入位置"))


def unpack_payload(payload: bytes, *, lead_count: bool = False) -> Dict[int, bytes]:
    """把载荷拆回 TLV 字段，是 pack_payload 的逆操作 (The inverse of pack_payload)"""
    fields: Dict[int, bytes] = {}
    offset = 1 if lead_count else 0
    while offset + 3 <= len(payload):
        key, _unused, length = payload[offset], payload[offset + 1], payload[offset + 2]
        fields[key] = payload[offset + 3 : offset + 3 + length]
        offset += 3 + length
    return fields


def decode_field(raw: bytes, config: EncoderConfig) -> str:
    """读回一个字符串字段，是 _encode_bytes 的逆操作 (The inverse of _encode_bytes)"""
    xor_base, add_base, pre_xor, rotate, post_add = config
    out = []
    for index in range(raw[-1]):
        value = ((raw[index] - post_add) % 256) ^ 187
        value = ((value >> rotate) | (value << (8 - rotate))) & 0xFF
        if pre_xor is not None:
            value ^= pre_xor
        value = (value - add_base - (170 & index)) % 256
        out.append(chr(value ^ (xor_base + index)))
    return "".join(out)


def dynosaur_payload(
    query: str,
    user_agent: str,
    *,
    timestamp: int,
    nonce: int,
    sequence: int = CALL_SEQUENCE_START,
    env_code: int = ENV_CODE,
    ub_code: int = UB_CODE,
) -> bytes:
    """
    环境报告，共 25 个 TLV 字段，键为 0x20～0x38 升序 (The environment report)

    其中三个字段是 hash_state，也是报告与请求绑定的仅有依据：0x2B 是空字符串
    （GET 请求没有请求体），0x2E 是查询串（只有查询串，不含路径），0x30 是 User-Agent，
    因此签名必须使用与发送请求时相同的 UA。
    """
    fields: Dict[int, bytes] = {
        0x21: _encode_bytes("1", _ENCODER_B),
        0x22: _encode_bytes("1", _ENCODER_B),
        0x23: _encode_bytes("0", _ENCODER_A),
        0x24: _encode_bytes(str(_mix(timestamp, nonce, env_code)), _ENCODER_A),
        0x25: _encode_bytes(str(sequence), _ENCODER_A),
        0x26: _encode_bytes(str(env_code), _ENCODER_A),
        0x27: _encode_bytes(str(timestamp), _ENCODER_A),
        0x28: _encode_bytes(WEBGL_HASH, _ENCODER_A),
        0x29: _encode_bytes("0", _ENCODER_A),
        0x2A: _encode_bytes(SDK_VERSION, _ENCODER_A),
        0x2B: _be(hash_state(""), 4),
        0x2C: _encode_bytes(CANVAS_HASH, _ENCODER_A),
        0x2D: _encode_bytes("0", _ENCODER_A),
        0x2E: _be(hash_state(query), 4),
        0x2F: _encode_bytes(str(sequence), _ENCODER_A),
        0x30: _be(hash_state(user_agent), 4),
        0x31: _encode_bytes(SCM_VERSION, _ENCODER_A),
        0x32: _encode_bytes(COMPONENT_VERSION, _ENCODER_A),
        0x33: _encode_bytes(DEVICE_HASH, _ENCODER_A),
        0x34: _encode_bytes(str(nonce), _ENCODER_A),
        0x35: _encode_bytes(PAGE, _ENCODER_A),
        0x36: _encode_bytes(str(ub_code), _ENCODER_A),
        0x37: _encode_bytes("0", _ENCODER_A),
        0x38: _be(VM_STATE_HASH, 4),
        # 计算下面的校验和时先占位。任何单字符字符串都可以，因为单字符字段的第 1 个字节
        # 是固定的填充字节；SDK 用的是 "0"，这里保持一致
        0x20: _encode_bytes("0", _ENCODER_A),
    }
    checksum = 0
    for key in sorted(fields):
        checksum ^= fields[key][1]
    fields[0x20] = _encode_bytes(str(checksum), _ENCODER_B)
    return pack_payload(fields)


def gnarly_fields(
    signed_query: str,
    user_agent: str,
    *,
    body: bytes = b"",
    timestamp: int,
    nonce: int,
    nonce2: int,
    sequence: int = CALL_SEQUENCE_START,
    env_code: int = ENV_CODE,
    ub_code: int = UB_CODE,
) -> Dict[int, bytes]:
    """
    请求封印的字段表，共 16 项，没有 0x07 (The request seal, as a field table)

    signed_query 是已经追加了 &X-Dynosaur=...&msToken=... 的业务查询串。即使 msToken
    为空也必须带上这段后缀，这使 X-Gnarly 成为对整个改写后地址的封印，而不只是对调用方参数的封印。

    两个校验和按固定的逻辑顺序折叠，与输出顺序不同。异或折叠与顺序无关，保持 SDK 的列表
    形状只是为了便于对照。
    """
    query_md5 = hashlib.md5(signed_query.encode("utf-8")).hexdigest()
    body_md5 = hashlib.md5(body).hexdigest()
    agent_md5 = hashlib.md5(user_agent.encode("utf-8")).hexdigest()
    mixed = _mix(timestamp, nonce, env_code)
    covered: List[Union[int, str]] = [
        0,
        env_code,
        ub_code,
        query_md5,
        body_md5,
        agent_md5,
        timestamp,
        0,
        nonce,
        SDK_VERSION,
        SCM_VERSION,
        CALL_SEQUENCE_START,
        sequence,
        sequence,
        mixed,
        nonce2,
    ]
    first = _checksum(covered, 2)
    second = _checksum([*covered, first], 1)
    return {
        0x00: _be(second, 4),
        0x01: _be(env_code, 2),
        0x02: _be(ub_code, 2),
        0x03: query_md5.encode("ascii"),
        0x04: body_md5.encode("ascii"),
        0x05: agent_md5.encode("ascii"),
        0x06: _be(timestamp, 4),
        0x08: _be(nonce, 4),
        0x09: SDK_VERSION.encode("ascii"),
        0x0A: SCM_VERSION.encode("ascii"),
        0x0B: _be(CALL_SEQUENCE_START, 2),
        0x0C: _be(sequence, 2),
        0x0D: _be(sequence, 2),
        0x0E: _be(mixed, 4),
        0x0F: _be(nonce2, 4),
        0x10: _be(first, 4),
    }


def gnarly_payload(
    signed_query: str,
    user_agent: str,
    *,
    body: bytes = b"",
    timestamp: int,
    nonce: int,
    nonce2: int,
    sequence: int = CALL_SEQUENCE_START,
    order: Optional[Sequence[int]] = None,
    env_code: int = ENV_CODE,
    ub_code: int = UB_CODE,
) -> bytes:
    """gnarly_fields 的字段表，打包在一字节的字段数之后 (Packed behind the field count)"""
    fields = gnarly_fields(
        signed_query,
        user_agent,
        body=body,
        timestamp=timestamp,
        nonce=nonce,
        nonce2=nonce2,
        sequence=sequence,
        env_code=env_code,
        ub_code=ub_code,
    )
    return pack_payload(fields, order, lead_count=True)


def _clock_nonce() -> int:
    """
    由微秒时钟得到的 32 位值，与 SDK 的做法一致

    实测冻结 Date.now、performance.now 与 Math.random 后两个随机数都变得确定，
    多次运行时大约每微秒增加 1。均匀随机数在可观测的范围内同样可用，
    但平台一直看到的是基于时钟的值，保持一致没有代价。
    """
    return int(time.time() * 1_000_000) & MASK32


def _random_key(rng: random.Random) -> Tuple[int, ...]:
    return tuple(rng.getrandbits(32) for _unused in range(KEY_WORDS))


def sign(
    pairs: Sequence[Tuple[str, str]],
    user_agent: str,
    *,
    ms_token: str = "",
    body: bytes = b"",
    timestamp: Optional[int] = None,
    nonce: Optional[int] = None,
    nonce2: Optional[int] = None,
    sequence: int = CALL_SEQUENCE_START,
    rng: Optional[random.Random] = None,
    key: Optional[Sequence[int]] = None,
    key2: Optional[Sequence[int]] = None,
) -> Tuple[str, Dict[str, str]]:
    """
    为一个 TikTok 网页接口请求签名，返回 (查询串, 签名参数)
    (Sign one TikTok web API request and return the query and the parameters)

    pairs 是按平台顺序排列的业务参数，四个签名参数追加在其后，不会穿插。返回的查询串就是
    要发送的字节序列，重新编码会破坏封印。

    ms_token 原样使用，空字符串也一样，绝不能伪造。TikTok 在带有 msToken 时会校验它，
    不带时也能接受，所以伪造的值比不带更糟。同一身份实测（2026-09-08）：身份自己的令牌
    返回 2545 字节，不带令牌返回 2541 字节，伪造的同长度令牌返回 0 字节并带 tt_orcas_res: 1。
    msToken 位于被封印的字节之内，签名与发送的必须是同一个字符串。

    Args:
        pairs (Sequence[Tuple[str, str]]): 按平台顺序排列的业务参数
        user_agent (str): 发送请求时使用的 User-Agent
        ms_token (str): cookie 中的 msToken，没有时为空字符串
        body (bytes): 请求体，GET 请求为空
        timestamp (int): 秒级时间戳，默认使用当前时间
        nonce (int): 第一个随机数，默认由微秒时钟生成
        nonce2 (int): 第二个随机数，默认由微秒时钟生成
        sequence (int): SDK 的签名计数
        rng (random.Random): 生成密钥的随机数发生器
        key (Sequence[int]): X-Dynosaur 使用的 12 个字的密钥，默认随机生成
        key2 (Sequence[int]): X-Gnarly 使用的 12 个字的密钥，默认随机生成

    Returns:
        Tuple[str, Dict[str, str]]: 签名后的查询串与四个签名参数
    """
    source = rng or random.Random()
    stamp = int(time.time()) if timestamp is None else int(timestamp)
    first_nonce = _clock_nonce() if nonce is None else int(nonce)
    second_nonce = (~_clock_nonce()) & MASK32 if nonce2 is None else int(nonce2)

    query = encode_query(pairs)
    dynosaur = seal(
        dynosaur_payload(
            query, user_agent, timestamp=stamp, nonce=first_nonce, sequence=sequence
        ),
        key if key is not None else _random_key(source),
    )
    # 封印覆盖追加了 X-Dynosaur 与 msToken 之后的查询串，所以要先拼接这两个参数再计算
    # X-Gnarly；而在它们之间发送的 X-Bogus 不在封印范围内，这种不对称是平台的设计
    sealed_query = f"{query}&{DYNOSAUR_PARAM}={dynosaur}&{MS_TOKEN_PARAM}={ms_token}"
    gnarly = seal(
        gnarly_payload(
            sealed_query,
            user_agent,
            body=body,
            timestamp=stamp,
            nonce=first_nonce,
            nonce2=second_nonce,
            sequence=sequence,
        ),
        key2 if key2 is not None else _random_key(source),
    )
    parameters = {
        DYNOSAUR_PARAM: dynosaur,
        MS_TOKEN_PARAM: ms_token,
        BOGUS_PARAM: BOGUS_VALUE,
        GNARLY_PARAM: gnarly,
    }
    # 原样拼接，不做百分号编码：字母表中有 /，填充是 =，TikTok 网页发送时两者都不转义
    signed = f"{sealed_query}&{BOGUS_PARAM}={BOGUS_VALUE}&{GNARLY_PARAM}={gnarly}"
    return signed, parameters


def pick_ms_token(cookies: Optional[Mapping[str, str]]) -> str:
    """取身份自己 cookie 中的 msToken，没有时与 SDK 一样为空字符串"""
    return (cookies or {}).get(MS_TOKEN_PARAM) or ""


class XGnarly:
    """
    TikTok 网页请求签名 (TikTok web request signer)

    TikTok 网页加载的 webmssdk 会改写每个接口请求的地址，在业务参数之后按固定顺序追加
    四个参数：

        <业务参数>&X-Dynosaur=<环境报告>&msToken=<会话令牌>&X-Bogus=1&X-Gnarly=<请求封印>

    本类不依赖浏览器生成这四个参数。两个签名共用一种信封：

        payload    = TLV 字段，每项为 [key][0x00][length][value...]
        key12      = 每次调用随机生成的 12 个 uint32
        rounds     = 5 + (sum(word & 0xF for word in key12) & 0xF)
        ciphertext = 类 ChaCha 的密钥流按小端 uint32 与载荷异或
        spliced    = 把 48 字节的密钥插入密文，位置为
                     (sum(密钥字节) + sum(密文字节)) % (len(密文) + 1)
        signature  = 自定义 base64(b"\\x4b" + spliced)

    签名自带密钥，服务器据此解密，unseal 也借此还原浏览器生成的签名。由于每次调用的密钥
    不同，两个独立签名不可能逐字节相同，只能解开后逐字段比对。

    来源：从 lf16-tiktok-web.tiktokcdn-us.com 下发的 webmssdk 2.0.0.561 中解码字符串表、
    读取算法常量移植而来，两套自定义字母表与 CHACHA_INIT、FNV_OFFSET、FNV_PRIME 都原样
    出现在 SDK 中。没有使用任何第三方实现的代码：xvhuan/tiktok-web-params 的 MIT 许可证
    附加了“仅供学习交流”的限制，与许可授予相矛盾；JoeanAmier/TikTokDownloader 是 GPL-3.0，
    复制其代码会改变本项目的许可证。前者只用来交叉核对，且在多处与真实 SDK 不一致。

    核对方式：用 Node 在无界面环境中运行真实 SDK，解开它生成的 X-Dynosaur，读出其中的时间戳
    与随机数，代入本模块重新生成后比对。2026-09-08 在 4 个接口、3 种 User-Agent、含中文的
    百分号编码查询、30 个参数的查询与签名计数 1～3 上核对了 20 组向量：X-Dynosaur 的 249 字节
    载荷逐字节一致，用还原的密钥重新加密可逐字符复现 400 字符的签名；X-Gnarly 的 16 个字段
    逐项一致（SDK 输出顺序每个进程不同，服务器按键解析，本模块按升序输出），用其载荷重新加密
    可复现 324 字符的签名。

    SDK 升级后 SDK_VERSION、SCM_VERSION 与字段表可能随之变化，需要重新抓取 SDK 核对。

    使用示例:
    ```python
        signed_query, params = XGnarly(user_agent).sign(
            [("aid", "1988"), ("secUid", sec_uid)], ms_token=ms_token
        )
        url = f"https://www.tiktok.com/api/post/item_list/?{signed_query}"
    ```
    """

    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent

    def sign(
        self,
        pairs: Sequence[Tuple[str, str]],
        ms_token: str = "",
        body: bytes = b"",
        **kwargs,
    ) -> Tuple[str, Dict[str, str]]:
        """
        为一个请求签名，返回 (查询串, 签名参数)，参数含义见模块函数 sign
        (Sign one request; see the module-level sign for the parameters)
        """
        return sign(pairs, self.user_agent, ms_token=ms_token, body=body, **kwargs)


__all__ = [
    "ALPHABET",
    "BOGUS_PARAM",
    "BOGUS_VALUE",
    "CALL_SEQUENCE_START",
    "DYNOSAUR_PARAM",
    "ENV_CODE",
    "GNARLY_PARAM",
    "MS_TOKEN_PARAM",
    "SCM_VERSION",
    "SDK_VERSION",
    "UB_CODE",
    "XGnarly",
    "decode_field",
    "dynosaur_payload",
    "encode_query",
    "gnarly_fields",
    "gnarly_payload",
    "hash_state",
    "pack_payload",
    "pick_ms_token",
    "seal",
    "sign",
    "unpack_payload",
    "unseal",
]

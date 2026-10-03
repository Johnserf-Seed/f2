# path: f2/apps/douyin/algorithm/webcast_signature.py

import hashlib
import random
from itertools import count
from typing import Optional, Protocol, Union

# 抖音网页端 webmssdk 1.0.0.53 中 frontierSign 的纯 Python 实现，生成直播弹幕 WebSocket 的 signature。
# 以下取值与 SDK 一致：kWebsocket 为 1，未调用 init 时 initialized 为 false，envcode 与 ubcode 为 0。
# 结果用 "s1" 字母表编码，它与 X-Bogus 的字母表只差第 28 个字符（"+" 与 "-"）。
_S1_ALPHABET = "Dkdpgh4ZKsQB80/Mfvw36XI1R25+WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe="
_K_WEBSOCKET = 1
_INITIALIZED = 0
_ENVCODE = 0
_UBCODE = 0
_ZERO_STUB = "0" * 32
_HEX_VALUES = {char: value for value, char in enumerate("0123456789abcdef")}

# 计算 X-MS-STUB 的原始字符串，格式与抖音网页端一致
_STUB_TEMPLATE = (
    "live_id=1,aid=6383,version_code=180800,webcast_sdk_version=1.0.14-beta.0,"
    "room_id={room_id},sub_room_id=,sub_channel_id=,did_rule=3,"
    "user_unique_id={user_unique_id},device_platform=web,device_type=,ac=,"
    "identity=audience"
)


class RandomSource(Protocol):
    """提供 random() 方法的随机数来源，测试时可传入固定序列 (A source of random floats)"""

    def random(self) -> float: ...


def _hex_decode(text: str) -> bytes:
    """
    按 SDK 的方式把十六进制字符串转成字节 (Decode hex the same way as the SDK)

    只识别小写的 0-9、a-f，其他字符按 0 处理；长度为奇数时忽略最后一个字符。
    """
    return bytes(
        (_HEX_VALUES.get(text[i], 0) << 4 | _HEX_VALUES.get(text[i + 1], 0)) & 0xFF
        for i in range(0, len(text) >> 1 << 1, 2)
    )


def _md5_tail(data: bytes) -> bytes:
    """MD5 摘要的最后两个字节 (The last two bytes of the MD5 digest)"""
    return hashlib.md5(data).digest()[14:16]


def _rc4(key: bytes, data: bytes) -> bytes:
    """标准 RC4 (Standard RC4)"""
    box = list(range(256))
    j = 0
    for i in range(256):
        j = (j + box[i] + key[i % len(key)]) % 256
        box[i], box[j] = box[j], box[i]
    i = j = 0
    out = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + box[i]) % 256
        box[i], box[j] = box[j], box[i]
        out.append(byte ^ box[(box[i] + box[j]) % 256])
    return bytes(out)


def _encode_s1(data: bytes) -> str:
    """
    用 "s1" 字母表做 base64 式编码 (Base64-style encoding with the s1 alphabet)

    每 3 个字节转成 4 个字符，最后不足 3 个字节时用 "=" 补齐。
    """
    chars = []
    for i in range(0, len(data), 3):
        chunk = data[i : i + 3]
        value = int.from_bytes(chunk.ljust(3, b"\0"), "big")
        chars.append(_S1_ALPHABET[value >> 18 & 63])
        chars.append(_S1_ALPHABET[value >> 12 & 63])
        chars.append(_S1_ALPHABET[value >> 6 & 63] if len(chunk) > 1 else "=")
        chars.append(_S1_ALPHABET[value & 63] if len(chunk) > 2 else "=")
    return "".join(chars)


# md5(md5("")) 的最后两个字节。WebSocket 签名时请求体固定为空字符串，所以是常量
_EMPTY_BODY_TAIL = _md5_tail(hashlib.md5(b"").digest())


class DouyinWebcastSignature:
    """
    抖音直播间签名生成器 (Douyin Webcast Signature Generator)

    纯 Python 实现网页端 SDK 的 frontierSign，用于直播弹幕 WebSocket 地址中的 signature 参数，
    不需要 Node.js 等 JavaScript 运行时。

    签名由 12 个字节编码成 16 个字符：
    - 第 1 个字节：kWebsocket 与 initialized 标志，以及 1 个随机位
    - 第 2 个字节：随机的 RC4 密钥
    - 其余 10 个字节：用该密钥做 RC4 加密的数据块，依次是签名计数、环境码、
      md5(md5("")) 与 md5(X-MS-STUB 的字节) 各自的最后两个字节、1 个随机字节和前 9 个字节的异或校验

    类方法:
    - get_signature: 根据直播间 ID 和用户唯一 ID 生成签名。
    - frontier_sign: 按 SDK 的 frontierSign 对 X-MS-STUB（或 X-MS-PAYLOAD）签名。

    使用示例:
    ```python
        # 创建 DouyinWebcastSignature 实例
        signature_handler = DouyinWebcastSignature()

        # 获取直播间签名
        signature = signature_handler.get_signature("7382517534467115826", "7382524529011246630")

        # 输出签名，16 个字符，每次调用的结果都不同
        print(signature)
    ```

    备注:
    - 签名计算不使用 UA，构造时不需要也不接受 user_agent。
    - 签名含 3 个随机成分，同样的输入每次结果都不同，这与网页端一致。
    - 签名计数（bogusIndex）在同一个实例内从 1 开始递增，与网页端 SDK 一致。
    """

    def __init__(self, *, rng: Optional[RandomSource] = None):
        """
        Args:
            rng: (RandomSource) 随机数来源，默认使用 random.SystemRandom()；测试时可传入固定序列
        """
        self._rng: RandomSource = rng or random.SystemRandom()
        self._bogus_index = count(1)

    def get_signature(self, room_id: str, user_unique_id: str) -> str:
        """
        获取直播间签名

        Args:
            room_id: (str) 直播间 ID
            user_unique_id: (str) 用户唯一 ID

        Returns:
            signature: (str) 签名
        """
        raw_string = _STUB_TEMPLATE.format(
            room_id=room_id, user_unique_id=user_unique_id
        )
        # md5 计算 X-MS-STUB
        x_ms_stub = hashlib.md5(raw_string.encode("utf-8")).hexdigest()
        return self.frontier_sign(x_ms_stub)

    def frontier_sign(
        self,
        x_ms_stub: Optional[str] = None,
        x_ms_payload: Optional[Union[str, bytes]] = None,
    ) -> str:
        """
        按 SDK 的 frontierSign 生成签名 (Sign like the SDK's frontierSign)

        Args:
            x_ms_stub: (str) 32 位十六进制的 X-MS-STUB，有值时优先使用
            x_ms_payload: (str | bytes) 没有 X-MS-STUB 时，取它的 md5 作为 stub；两者都没有时 stub 为 32 个 0

        Returns:
            signature: (str) 签名
        """
        if x_ms_stub:
            stub = x_ms_stub
        elif x_ms_payload:
            payload = (
                x_ms_payload.encode("utf-8")
                if isinstance(x_ms_payload, str)
                else bytes(x_ms_payload)
            )
            stub = hashlib.md5(payload).hexdigest()
        else:
            stub = _ZERO_STUB

        # 随机数的取用顺序与 SDK 一致：标志位、数据块的最后一个字节、RC4 密钥
        flag_random = int(100 * self._rng.random())
        tail_random = int(255 * self._rng.random()) & 0xFF
        key = int(255 * self._rng.random()) & 0xFF

        flags = _K_WEBSOCKET << 6 | _INITIALIZED << 5 | (flag_random & 1) << 4
        block = bytearray(9)
        block[0] = next(self._bogus_index) & 63
        block[1] = _ENVCODE >> 8 & 0xFF
        block[2] = _ENVCODE & 0xFF
        block[3] = _UBCODE & 0xFF
        block[4:6] = _EMPTY_BODY_TAIL
        block[6:8] = _md5_tail(_hex_decode(stub))
        block[8] = tail_random

        checksum = 0
        for byte in block:
            checksum ^= byte
        block.append(checksum)

        return _encode_s1(bytes([flags, key]) + _rc4(bytes([key]), bytes(block)))


if __name__ == "__main__":
    signature_handler = DouyinWebcastSignature()
    signature = signature_handler.get_signature(
        "7382517534467115826", "7382524529011246630"
    )
    print(signature)

# path: tests/test_webcast_protobuf.py

import json
from pathlib import Path

import pytest
from google.protobuf import json_format

from f2.apps.douyin.crawler import DouyinWebSocketCrawler
from f2.apps.douyin.proto import douyin_webcast_pb2
from f2.apps.tiktok.crawler import TiktokWebSocketCrawler
from f2.apps.tiktok.proto import tiktok_webcast_pb2

DATA = Path(__file__).parent / "data"
APPS = {
    "douyin": (DouyinWebSocketCrawler, douyin_webcast_pb2),
    "tiktok": (TiktokWebSocketCrawler, tiktok_webcast_pb2),
}


# 与当前 proto 不一致的样本：录制时 badgeImageList 等字段还不是列表，或文件为空
STALE = {
    ("douyin", "WebcastGiftMessage"): "按旧版 proto 录制",
    ("douyin", "WebcastLiveShoppingMessage"): "按旧版 proto 录制",
    ("douyin", "WebcastProductChangeMessage"): "按旧版 proto 录制",
    ("douyin", "WebcastSocialMessage"): "按旧版 proto 录制",
    ("douyin", "WebcastUpdateFanTicketMessage"): "按旧版 proto 录制",
    ("tiktok", "WebcastLinkMicFanTicketMethod"): "样本文件为空",
}


def recorded_messages():
    """录制的直播间消息：回调名 WebcastXxx 对应生成代码中的 Xxx"""
    for app, (crawler, module) in APPS.items():
        for path in sorted((DATA / app / "webcast" / "dict").glob("*.json")):
            method = path.stem
            message_cls = getattr(module, method.removeprefix("Webcast"), None)
            if message_cls is None or not hasattr(crawler, method):
                continue
            reason = STALE.get((app, method))
            yield pytest.param(
                crawler,
                method,
                message_cls,
                path,
                id=f"{app}-{method}",
                marks=[pytest.mark.skip(reason=reason)] if reason else [],
            )


@pytest.mark.parametrize(
    "crawler, method, message_cls, path", list(recorded_messages())
)
async def test_callbacks_parse_recorded_messages(crawler, method, message_cls, path):
    # 生成代码由 protoc 5.29.3 生成，升级 protobuf 运行时后由这些真实消息检查解析结果
    message = json_format.ParseDict(
        json.loads(path.read_text(encoding="utf-8")),
        message_cls(),
        ignore_unknown_fields=True,
    )
    expected = json_format.MessageToDict(message, preserving_proto_field_name=True)

    parsed = await getattr(crawler, method)(message.SerializeToString())

    assert parsed == expected
    assert parsed.get("common", {}).get("method") == method


@pytest.mark.parametrize(
    "path",
    sorted((DATA / "tiktok" / "webcast" / "protobuf").glob("*.bin")),
    ids=lambda path: path.stem,
)
async def test_callbacks_parse_recorded_binary(path):
    method = path.stem.rsplit("_", 1)[0]

    parsed = await getattr(TiktokWebSocketCrawler, method)(path.read_bytes())

    assert parsed

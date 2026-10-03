# path: tests/test_webcast_ack_closed.py

import gzip
import logging

import pytest
from websockets import ConnectionClosedError

from f2.apps.douyin.crawler import DouyinWebSocketCrawler
from f2.apps.douyin.proto.douyin_webcast_pb2 import PushFrame as DouyinPushFrame
from f2.apps.douyin.proto.douyin_webcast_pb2 import Response as DouyinResponse
from f2.apps.tiktok.crawler import TiktokWebSocketCrawler
from f2.apps.tiktok.proto.tiktok_webcast_pb2 import PushFrame as TiktokPushFrame
from f2.apps.tiktok.proto.tiktok_webcast_pb2 import Response as TiktokResponse


class ClosedWebSocket:
    """连接已经关闭的 WebSocket，发送时抛出 ConnectionClosedError"""

    def __init__(self):
        self.sent = 0

    async def send(self, data):
        self.sent += 1
        raise ConnectionClosedError(None, None)


def douyin_frame():
    response = DouyinResponse(need_ack=True, internal_ext="ext")
    payload = gzip.compress(response.SerializeToString())
    return DouyinPushFrame(logId=1, payload=payload).SerializeToString()


def tiktok_frame():
    response = TiktokResponse(needAck=True, internalExt="ext")
    payload = gzip.compress(response.SerializeToString())
    return TiktokPushFrame(logid=1, payload=payload).SerializeToString()


@pytest.mark.parametrize(
    "crawler_class, frame",
    [
        (DouyinWebSocketCrawler, douyin_frame),
        (TiktokWebSocketCrawler, tiktok_frame),
    ],
    ids=["douyin", "tiktok"],
)
async def test_ack_on_closed_connection_is_not_an_error(crawler_class, frame, caplog):
    # 本地转发服务没有客户端时会主动关闭连接，正在处理的消息再发 ack 会抛出
    # ConnectionClosedError，此前被当作“处理消息出错”连同完整堆栈打印出来
    crawler = object.__new__(crawler_class)  # 构造函数会联网获取 ttwid，这里跳过
    crawler.callbacks = {}
    crawler.connected_clients = set()
    crawler.websocket = ClosedWebSocket()

    with caplog.at_level(logging.DEBUG):
        await crawler.handle_wss_message(frame())

    assert crawler.websocket.sent == 1
    assert [
        r for r in caplog.records if r.name == "f2" and r.levelno >= logging.WARNING
    ] == []

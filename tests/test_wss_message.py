# path: tests/test_wss_message.py

import gzip
import logging

import pytest

from f2.apps.douyin.crawler import DouyinWebSocketCrawler
from f2.apps.douyin.proto import douyin_webcast_pb2 as douyin_pb
from f2.apps.douyin.utils import TokenManager as DouyinTokenManager
from f2.apps.tiktok.crawler import TiktokWebSocketCrawler
from f2.apps.tiktok.proto import tiktok_webcast_pb2 as tiktok_pb

KWARGS = {
    "headers": {"User-Agent": "UA"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "show_message": False,
}


@pytest.fixture(autouse=True)
def no_ttwid_request(monkeypatch):
    # 抖音弹幕爬虫构造时会请求 ttwid.bytedance.com 生成 ttwid
    monkeypatch.setattr(
        DouyinTokenManager, "gen_ttwid", classmethod(lambda cls: "fake-ttwid")
    )


def douyin_frame(methods, compress=True):
    response = douyin_pb.Response(need_ack=True, internal_ext="ext")
    for method in methods:
        response.messages.add(method=method)
    payload = response.SerializeToString()
    return douyin_pb.PushFrame(
        logId=7, payload=gzip.compress(payload) if compress else payload
    ).SerializeToString()


def tiktok_frame(methods, compress=True):
    response = tiktok_pb.Response(needAck=True, internalExt="ext")
    for method in methods:
        response.messages.add(method=method)
    payload = response.SerializeToString()
    return tiktok_pb.PushFrame(
        logid=7, payload=gzip.compress(payload) if compress else payload
    ).SerializeToString()


APPS = pytest.mark.parametrize(
    "crawler_class, frame",
    [(DouyinWebSocketCrawler, douyin_frame), (TiktokWebSocketCrawler, tiktok_frame)],
    ids=["douyin", "tiktok"],
)


def crawler_with(crawler_class, callbacks):
    crawler = crawler_class(KWARGS, callbacks=callbacks)
    acks = []

    async def send_ack(log_id, internal_ext):
        acks.append((log_id, internal_ext))

    crawler.send_ack = send_ack
    return crawler, acks


def f2_records(caplog, level):
    return [
        r.getMessage() for r in caplog.records if r.name == "f2" and r.levelno == level
    ]


@APPS
async def test_callback_error_names_the_failing_method(crawler_class, frame, caplog):
    # 此前按回调结果的下标回查 messages，前面有没回调的消息时报出的是别的方法名
    async def failing(data):
        raise ValueError("boom")

    crawler, acks = crawler_with(crawler_class, {"WebcastChatMessage": failing})

    with caplog.at_level(logging.DEBUG):
        await crawler.handle_wss_message(
            frame(["WebcastUnknownMessage", "WebcastChatMessage"])
        )

    errors = [m for m in f2_records(caplog, logging.ERROR) if "boom" in m]
    assert len(errors) == 1
    assert "WebcastChatMessage" in errors[0]
    assert "WebcastUnknownMessage" not in errors[0]


async def test_uncompressed_tiktok_frame_is_not_a_warning(caplog):
    # 连接后的第一帧不压缩，此前每次连接都报“解压缩数据时出错”
    crawler, acks = crawler_with(TiktokWebSocketCrawler, {})

    with caplog.at_level(logging.DEBUG):
        await crawler.handle_wss_message(tiktok_frame([], compress=False))

    assert f2_records(caplog, logging.WARNING) == []
    assert f2_records(caplog, logging.ERROR) == []
    assert (7, "ext") in acks

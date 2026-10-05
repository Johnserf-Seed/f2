# path: tests/test_tiktok_live_filter.py

import json

import pytest

from f2.apps.tiktok.filter import UserLiveFilter


def live(qualities):
    # 与接口一致，stream_data 是 JSON 字符串
    stream_data = {
        "data": {
            quality: {
                "main": {
                    "flv": f"https://cdn.example/{quality}.flv",
                    "hls": f"https://cdn.example/{quality}.m3u8",
                }
            }
            for quality in qualities
        }
    }
    return UserLiveFilter(
        {
            "data": {
                "liveRoom": {
                    "streamData": {
                        "pull_data": {"stream_data": json.dumps(stream_data)}
                    }
                }
            }
        }
    )


@pytest.mark.parametrize(
    "qualities, best",
    [
        (["hd", "ao"], "hd"),  # 实测多数直播只有这两种
        (["ao", "sd", "origin", "hd"], "origin"),
        (["ld", "uhd", "sd"], "uhd"),
        (["ao"], None),  # 纯音频不能当录像
        ([], None),
    ],
)
def test_live_url_uses_the_best_available_quality(qualities, best):
    # 此前固定读取 origin（原画），没有原画的直播取不到地址，录制提示地址无效
    user = live(qualities)

    if best is None:
        assert (user.live_hls_url, user.live_flv_url) == (None, None)
    else:
        assert user.live_hls_url == f"https://cdn.example/{best}.m3u8"
        assert user.live_flv_url == f"https://cdn.example/{best}.flv"


def test_live_without_stream_data_has_no_url():
    user = UserLiveFilter({"data": {"liveRoom": {}}})

    assert (user.live_hls_url, user.live_flv_url) == (None, None)

# path: tests/test_douyin_video_quality.py

import pytest

from f2.apps.douyin.filter import (
    FriendFeedFilter,
    HomePostSearchFilter,
    PostDetailFilter,
    UserPostFilter,
)
from f2.apps.douyin.utils import get_video_play_urls, select_best_bit_rate


def variant(gear, bit_rate, width, height, h265=0):
    return {
        "gear_name": gear,
        "bit_rate": bit_rate,
        "is_h265": h265,
        "play_addr": {
            "width": width,
            "height": height,
            "url_list": [f"https://v.example/{gear}/1", f"https://v.example/{gear}/2"],
        },
    }


# 与真实作品的清晰度列表一致（接口按码率从高到低排列，最高 1080p）
TYPICAL = [
    variant("normal_1080_0", 2114952, 1080, 1920),
    variant("normal_720_0", 1341492, 720, 1280),
    variant("normal_540_0", 1211066, 576, 1024),
    variant("adapt_lowest_1080_1", 570590, 1080, 1920, h265=1),
    variant("adapt_540_1", 378594, 576, 1024, h265=1),
]
# #214：2K 只有 H.265 版本，码率低于 1080p 的 H.264，排在后面
WITH_2K = [
    variant("normal_1080_0", 2114952, 1080, 1920),
    variant("adapt_2k_1", 1893210, 1440, 2560, h265=1),
    variant("normal_720_0", 1341492, 720, 1280),
]


def gear(item):
    return item["gear_name"]


def test_typical_work_keeps_first_variant():
    assert gear(select_best_bit_rate(TYPICAL)) == "normal_1080_0"


def test_higher_resolution_wins_over_higher_bit_rate():
    assert gear(select_best_bit_rate(WITH_2K)) == "adapt_2k_1"


def test_equal_quality_keeps_earlier_variant():
    items = [variant("a", 100, 720, 1280), variant("b", 100, 720, 1280)]
    assert gear(select_best_bit_rate(items)) == "a"


def test_variants_without_urls_are_skipped():
    empty = variant("empty_2k", 3000000, 1440, 2560)
    empty["play_addr"]["url_list"] = []
    assert gear(select_best_bit_rate([empty] + TYPICAL)) == "normal_1080_0"


def test_missing_size_falls_back_to_bit_rate():
    items = [variant("low", 500, None, None), variant("high", 900, None, None)]
    assert gear(select_best_bit_rate(items)) == "high"


def test_non_numeric_size_is_ignored():
    items = [variant("odd", 900, "?", "?"), variant("hd", 500, 720, 1280)]
    assert gear(select_best_bit_rate(items)) == "hd"


@pytest.mark.parametrize("bit_rates", [None, [], [None, "x"]])
def test_no_usable_variant(bit_rates):
    assert select_best_bit_rate(bit_rates) is None


def test_play_urls_fall_back_to_play_addr():
    video = {"bit_rate": [], "play_addr": {"url_list": ["https://v.example/p"]}}
    assert get_video_play_urls(video) == ["https://v.example/p"]


@pytest.mark.parametrize("video", [None, {}, "video", {"bit_rate": None}])
def test_play_urls_without_video(video):
    assert get_video_play_urls(video) is None


# ---------------- 各个过滤器 ----------------


def urls(gear_name):
    return [f"https://v.example/{gear_name}/1", f"https://v.example/{gear_name}/2"]


def test_post_detail_picks_highest_resolution():
    data = {"aweme_detail": {"video": {"bit_rate": WITH_2K}}}
    assert PostDetailFilter(data).video_play_addr == urls("adapt_2k_1")


def test_user_post_keeps_alignment_with_works():
    data = {
        "aweme_list": [
            {"video": {"bit_rate": WITH_2K}},
            {"images": [{}]},  # 图集作品没有视频
            {"video": {"bit_rate": TYPICAL}},
        ]
    }
    assert UserPostFilter(data).video_play_addr == [
        urls("adapt_2k_1"),
        None,
        urls("normal_1080_0"),
    ]


def test_friend_feed_and_search_use_the_same_rule():
    feed = {"data": [{"aweme": {"video": {"bit_rate": WITH_2K}}}]}
    search = {"aweme_list": [{"item": {"video": {"bit_rate": WITH_2K}}}]}
    assert FriendFeedFilter(feed).video_play_addr == [urls("adapt_2k_1")]
    assert HomePostSearchFilter(search).video_play_addr == [urls("adapt_2k_1")]

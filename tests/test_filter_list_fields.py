# path: tests/test_filter_list_fields.py

import ast
from pathlib import Path

import pytest

from f2.apps.douyin.filter import UserLiveRankingFilter, UserPostFilter
from f2.apps.tiktok.filter import PostDetailFilter

FILTERS_DIR = Path(__file__).resolve().parents[1] / "f2" / "apps"


def ranker(i, signature=True):
    user = {
        "id": str(i),
        "nickname": f"用户{i}",
        "sec_uid": f"sec{i}",
        "display_id": f"d{i}",
        "gender": 1,
        "webcast_uid": f"w{i}",
    }
    if signature:
        user["signature"] = f"签名{i}"
    return {"rank": i, "score": i * 10, "is_hidden": False, "user": user}


def test_live_ranking_with_one_viewer():
    # 此前只有一位观众时字段是单个值，_to_list 报“由于接口更新，部分字段处理失败”
    rows = UserLiveRankingFilter({"data": {"ranks": [ranker(1)]}})._to_list()

    assert [(r["nickname_raw"], r["signature_raw"], r["rank"]) for r in rows] == [
        ("用户1", "签名1", 1)
    ]


def test_live_ranking_fields_stay_aligned():
    # 此前第二位没有签名时，第三位的签名会算到第二位头上
    ranking = UserLiveRankingFilter(
        {"data": {"ranks": [ranker(1), ranker(2, signature=False), ranker(3)]}}
    )

    assert ranking.signature_raw == ["签名1", None, "签名3"]
    assert [r["signature_raw"] for r in ranking._to_list()] == ["签名1", None, "签名3"]


def test_douyin_caption_is_a_list_aligned_with_posts():
    single = UserPostFilter({"aweme_list": [{"aweme_id": "1", "caption": "标题1"}]})
    posts = UserPostFilter(
        {
            "aweme_list": [
                {"aweme_id": "1", "caption": "标题1"},
                {"aweme_id": "2"},
                {"aweme_id": "3", "caption": "标题3"},
            ]
        }
    )

    # 此前只有一个作品时是字符串，命名模板的 {caption} 只取到第一个字
    assert single.caption_raw == ["标题1"]
    assert posts.caption_raw == ["标题1", None, "标题3"]
    assert posts.caption == ["标题1", "", "标题3"]


def test_tiktok_single_challenge_is_a_list():
    detail = PostDetailFilter(
        {"itemInfo": {"itemStruct": {"challenges": [{"title": "tag", "desc": "d"}]}}}
    )

    assert detail.challenges_title == ["tag"]
    assert detail.challenges_desc == ["d"]


@pytest.mark.parametrize("app", ["douyin", "tiktok", "weibo"])
def test_wildcard_paths_are_read_as_lists(app):
    # _get_attr_value 只匹配到一个值时返回值本身，匹配不到时返回 None，带 [*] 的路径要用
    # _get_list_attr_value。twitter 的推文详情下载器目前依赖“单个媒体是字符串”的行为，不在此列
    tree = ast.parse((FILTERS_DIR / app / "filter.py").read_text(encoding="utf-8"))
    offenders = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and getattr(node.func, "attr", "") == "_get_attr_value"
        and node.args
        and "[*]" in ast.unparse(node.args[0])
    ]

    assert offenders == []

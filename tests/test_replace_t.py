# path: tests/test_replace_t.py

import pytest

from f2.utils.string.formatter import replaceT


@pytest.mark.parametrize(
    "text, expected",
    [
        # #248：日文假名是正常文字，保留
        ("どういう意味", "どういう意味"),
        ("カタカナ・ラーメン", "カタカナ・ラーメン"),
        ("ㇰㇱㇲ", "ㇰㇱㇲ"),
        # 标点与空格照旧替换，已下载作品的文件名不会因此变化
        ("有同学问「どういう意味？」", "有同学问_どういう意味__"),
        (
            "男朋友的经典名言，我这是在哄你开心啊！ abc",
            "男朋友的经典名言_我这是在哄你开心啊__abc",
        ),
        # 中文、英文字母、数字与 # 不变
        ("抖音#日语学习abc123", "抖音#日语学习abc123"),
    ],
)
def test_replace_t(text, expected):
    assert replaceT(text) == expected


def test_replace_t_handles_lists_and_other_types():
    assert replaceT(["ひらがな", None, "中文，标点"]) == ["ひらがな", "", "中文_标点"]
    assert replaceT(123) == 123

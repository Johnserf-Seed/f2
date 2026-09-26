# path: tests/test_replace_t.py

import pytest

from f2.utils.string.formatter import replaceT


@pytest.mark.parametrize(
    "text, expected",
    [
        # #248：标点、空格与各国文字原样保留
        ("有同学问「どういう意味？」", "有同学问「どういう意味？」"),
        (
            "男朋友的经典名言，我这是在哄你开心啊！ #日语",
            "男朋友的经典名言，我这是在哄你开心啊！ #日语",
        ),
        ("カタカナ・ラーメン ㇰㇱ", "カタカナ・ラーメン ㇰㇱ"),
        ("한국어 😀 café", "한국어 😀 café"),
        # 文件名不允许的字符换成外观相近的全角字符
        ('a/b\\c:d*e?f"g<h>i|j', "a／b＼c：d＊e？f＂g＜h＞i｜j"),
        # 换行与制表符换成空格，其余控制字符去掉
        ("第一行\n第二行\t制表\x07响铃", "第一行 第二行 制表响铃"),
        # Windows 不允许以空格或点结尾
        ("  结尾的点和空格. . ", "结尾的点和空格"),
        # 非空内容被清空时用下划线兜底，空字符串保持为空
        ("...", "_"),
        ("", ""),
    ],
)
def test_replace_t(text, expected):
    assert replaceT(text) == expected


def test_replace_t_handles_lists_and_other_types():
    assert replaceT(["ひらがな", None, "x/y"]) == ["ひらがな", "", "x／y"]
    assert replaceT(123) == 123

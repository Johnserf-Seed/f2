# path: tests/test_replace_t.py

import pytest

import f2.utils.string.formatter as formatter
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


@pytest.mark.parametrize(
    "text, expected",
    [
        ("con", "con_"),
        ("NUL", "NUL_"),
        ("Com1", "Com1_"),
        ("aux.txt", "aux_.txt"),
        ("nul.tar.gz", "nul_.tar.gz"),
        ("console", "console"),
        ("lpt", "lpt"),
    ],
)
def test_windows_reserved_names(monkeypatch, text, expected):
    # Windows 不允许 CON、NUL、COM1 等设备名作为文件名或目录名，此前作者昵称为 con 时无法建立用户目录
    monkeypatch.setattr(formatter, "_IS_WINDOWS", True)

    assert replaceT(text) == expected


def test_reserved_names_are_kept_on_other_systems(monkeypatch):
    monkeypatch.setattr(formatter, "_IS_WINDOWS", False)

    assert replaceT("con") == "con"

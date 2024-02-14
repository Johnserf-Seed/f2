# path: tests/test_desc_limit.py

import pytest
from unittest.mock import patch
from f2.utils.utils import split_filename

os_limit = {
    "win32": 200,
    "cygwin": 60,
    "darwin": 60,
    "linux": 60,
}


def test_long_text_split():
    text = "见字如晤_展信舒颜___有段时间我常失眠_双目无神地看着天花板_思绪像团乱麻_可没有办法变成语言_原来一个人面对自己也会词不达意_因为有这样的经历_有时候你也不知道自己的情\
        绪到底从何而来_生活的难_但失去这件事的重量_所以那时候写_是不能从外表和性格判断的_事实是他也的确乐观__失眠的时候_为什么会变成现在这样_告别的人_想要的生活_后来发现原来登山的路那么长_连尊严都能被\
        踩在脚下_换来一个没有回响_于是你站在自己的世界中心_身旁没有一个人__大概在某些时刻_为什么会变成现在这样__就是我们必经的站台_理解是稀缺品_如果有人能站在你身旁_这才是一件类似于奇迹的事_恐怕你此时此刻_\
        正在想__这几年我经历生老病死_很多时候我都觉得无力前行_我比谁都讨厌自己_讨厌自己的无能为力_然后_我重新坐到书桌_一个字一个字写__有条捷径可以迅速摆脱所有烦恼_我自己也想走\
        _身边的朋友也没能找到这么一条路_只是继续往前走_ 也继续往前走_发现自己没事了_发 现即使过去依然值得怀念_哪怕现在发生的__所以你会没事的_照常吃饭_照常把那些需要做的 事做好_就\
        停下来歇一歇_烦恼大概不会消失_这些纪念品__时间就是时间_让时间变得值得纪念的__它们最后会绕一个圈__以上_祝你早安午安晚安"

    with patch("sys.platform", "win32"):  # 模拟 Windows 系统
        split_text = split_filename(text, os_limit)
        assert len(split_text) <= os_limit["win32"]

    with patch("sys.platform", "linux"):  # 模拟 Linux 系统
        split_text = split_filename(text, os_limit)
        assert len(split_text) <= os_limit["linux"]


def test_short_text_no_split():
    text = "见字如晤_展信舒颜___有段时间我常失眠_双目无神地看着天花板_思绪像团乱麻_可没有办法变成语言_原来一个人面对自己也会词不达意_因为有这样的经历_有时候你也不知道自己的情绪到底从何而来_生活的难_但失去这件事的重量_所以那时候"
    with patch("sys.platform", "win32"):  # 模拟 Windows 系统
        split_text = split_filename(text, os_limit)
        assert len(split_text) <= os_limit["win32"]

    with patch("sys.platform", "linux"):  # 模拟 Linux 系统
        split_text = split_filename(text, os_limit)
        assert len(split_text) <= os_limit["linux"]


def test_long_english_text_split():
    text = "Stay_tuned_to_hear_my_French_progress__DISCLAIMER__this_video_is_NOT_a_political_statement__I_m_just_sharing_the_languages_that_I_speak_with_you___Any_comments_about_politics_will_have_to_be_blocked__This_is_not_the_right_place_for_such_discussions"
    with patch("sys.platform", "win32"):  # 模拟 Windows 系统
        split_text = split_filename(text, os_limit)
        assert len(split_text) <= os_limit["win32"]

    with patch("sys.platform", "linux"):  # 模拟 Linux 系统
        split_text = split_filename(text, os_limit)
        assert len(split_text) <= os_limit["linux"]

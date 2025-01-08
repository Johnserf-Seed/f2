# path: tests/test_desc_limit.py

import pytest

from unittest.mock import patch

from f2.utils.utils import split_filename

# 操作系统字符限制
os_limit = {
    "win32": 200,
    "cygwin": 200,
    "darwin": 200,
    "linux": 200,
}


# ===== Fixture =====
@pytest.fixture
def mock_platform(request):
    """Fixture to mock sys.platform"""
    platform = request.param
    with patch("sys.platform", platform):
        yield platform


# ===== 测试：长文本分割 =====
@pytest.mark.parametrize("mock_platform", ["win32", "linux"], indirect=True)
def test_long_text_split(mock_platform):
    """
    测试长文本是否按照操作系统限制进行分割，并确保前半部分较长
    """
    text = "见字如晤_展信舒颜___有段时间我常失眠_双目无神地看着天花板_思绪像团乱麻_可没有办法变成语言_原来一个人面对自己也会词不达意_因为有这样的经历_有时候你也不知道自己的情\
        绪到底从何而来_生活的难_但失去这件事的重量_所以那时候写_是不能从外表和性格判断的_事实是他也的确乐观__失眠的时候_为什么会变成现在这样_告别的人_想要的生活_后来发现原来登山的路那么长_连尊严都能被\
        踩在脚下_换来一个没有回响_于是你站在自己的世界中心_身旁没有一个人__大概在某些时刻_为什么会变成现在这样__就是我们必经的站台_理解是稀缺品_如果有人能站在你身旁_这才是一件类似于奇迹的事_恐怕你此时此刻_\
        正在想__这几年我经历生老病死_很多时候我都觉得无力前行_我比谁都讨厌自己_讨厌自己的无能为力_然后_我重新坐到书桌_一个字一个字写__有条捷径可以迅速摆脱所有烦恼_我自己也想走\
        _身边的朋友也没能找到这么一条路_只是继续往前走_ 也继续往前走_发现自己没事了_发 现即使过去依然值得怀念_哪怕现在发生的__所以你会没事的_照常吃饭_照常把那些需要做的 事做好_就\
        停下来歇一歇_烦恼大概不会消失_这些纪念品__时间就是时间_让时间变得值得纪念的__它们最后会绕一个圈__以上_祝你早安午安晚安"

    split_text = split_filename(text, os_limit)

    # 确保分割后的长度符合限制
    assert (
        len(split_text.encode("utf-8")) <= os_limit[mock_platform]
    ), f"Platform {mock_platform} exceeded OS limit."

    # 检查是否包含 '......'，表示已被截断
    if len(text.encode("utf-8")) > os_limit[mock_platform]:
        assert (
            "......" in split_text
        ), "Long text should contain '......' after splitting"

        # 检查前后部分比例
        parts = split_text.split("......")
        assert len(parts) == 2, "Split text should have two parts separated by '......'"
        assert len(parts[0].encode("utf-8")) >= len(
            parts[1].encode("utf-8")
        ), "The first part should be longer than the second part."


# ===== 测试：短文本不分割 =====
@pytest.mark.parametrize("mock_platform", ["win32", "linux"], indirect=True)
def test_short_text_no_split(mock_platform):
    """
    测试短文本不需要分割
    """
    text = "见字如晤_展信舒颜"

    split_text = split_filename(text, os_limit)
    assert text == split_text, "Short text should not be modified."


# ===== 测试：长英文文本分割 =====
@pytest.mark.parametrize("mock_platform", ["win32", "linux"], indirect=True)
def test_long_english_text_split(mock_platform):
    """
    测试长英文文本是否按照操作系统限制进行分割
    """
    text = "Stay_tuned_to_hear_my_French_progress__DISCLAIMER__this_video_is_NOT_a_political_statement"

    split_text = split_filename(text, os_limit)

    # 确保分割后的长度符合限制
    assert (
        len(split_text.encode("utf-8")) <= os_limit[mock_platform]
    ), f"Platform {mock_platform} exceeded OS limit."

    if len(text.encode("utf-8")) > os_limit[mock_platform]:
        assert (
            "......" in split_text
        ), "Long text should contain '......' after splitting"
        parts = split_text.split("......")
        assert len(parts) == 2, "Split text should have two parts separated by '......'"
        assert len(parts[0].encode("utf-8")) >= 2 * len(
            parts[1].encode("utf-8")
        ), "The first part should be approximately twice as long as the second part."


# ===== 测试：空字符串 =====
@pytest.mark.parametrize("mock_platform", ["win32", "linux"], indirect=True)
def test_empty_text(mock_platform):
    """
    测试空字符串
    """
    text = ""
    split_text = split_filename(text, os_limit)
    assert split_text == "", "Empty text should remain unchanged."


# ===== 测试：边界情况（接近限制长度） =====
@pytest.mark.parametrize("mock_platform", ["win32", "linux"], indirect=True)
def test_borderline_text(mock_platform):
    """
    测试接近限制长度的文本
    """
    text = "a" * (os_limit[mock_platform] - 1)
    split_text = split_filename(text, os_limit)
    assert (
        len(split_text.encode("utf-8")) <= os_limit[mock_platform]
    ), f"Platform {mock_platform} exceeded OS limit for borderline case."
    assert text == split_text, "Borderline text should not be modified."


# ===== 测试：包含特殊字符 =====
@pytest.mark.parametrize("mock_platform", ["win32", "linux"], indirect=True)
def test_special_characters(mock_platform):
    """
    测试包含特殊字符的长文本
    """
    text = "特殊字符!@#$%^&*()_+-={}[]|\\:\";'<>?,./~`" * 10

    split_text = split_filename(text, os_limit)
    assert (
        len(split_text.encode("utf-8")) <= os_limit[mock_platform]
    ), f"Platform {mock_platform} exceeded OS limit with special characters."
    if len(text.encode("utf-8")) > os_limit[mock_platform]:
        assert (
            "......" in split_text
        ), "Long special-character text should contain '......' after splitting"

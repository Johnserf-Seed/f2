import pytest
from f2.apps.twitter.utils import extract_desc


@pytest.mark.parametrize(
    "text_raw, expected_desc",
    [
        ("xxx https://t.co/SfB6v3Kx1z", "xxx"),
        ("https://t.co/SfB6v3Kx1z", "https://t.co/SfB6v3Kx1z"),
        ("   ", ""),
    ],
)
def test_extract_desc(text_raw, expected_desc):
    """
    测试 extract_desc 函数是否正确提取文本中的描述部分。

    参数：
        text_raw (str): 输入的原始文本。
        expected_desc (str): 期望提取出的描述部分。
    """
    desc = extract_desc(text_raw)
    # 断言结果与期望一致
    assert (
        desc == expected_desc
    ), f"提取错误: 输入: {text_raw}, 实际: {desc}, 期望: {expected_desc}"

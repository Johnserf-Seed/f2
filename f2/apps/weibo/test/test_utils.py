import pytest
from f2.apps.weibo.utils import extract_desc


@pytest.mark.parametrize(
    "text_raw, expected_desc",
    [
        ("超大颗花生汤圆[舔屏] http://t.cn/A6nqzsFe", "超大颗花生汤圆[舔屏]"),
        ("分享视频 http://t.cn/A6nNyQyS ​​​", "分享视频"),
        ("香宝宝   http://t.cn/A6mwArY7 ​​​", "香宝宝"),
        (
            "  总有人类想要变成小猫咪^⌯𖥦⌯^ ੭   http://t.cn/A6n1zhGt ​​​",
            "总有人类想要变成小猫咪^⌯𖥦⌯^ ੭",
        ),
        ("过来挨踢[亲亲]      http://t.cn/A6ndh6PS ​​​", "过来挨踢[亲亲]"),
        ("单独的文案   ", "单独的文案"),  # 没有链接的情况
        ("http://t.cn/A6nqzsFe", "http://t.cn/A6nqzsFe"),  # 只有链接的情况
        ("   ", ""),  # 空字符串或空白内容
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

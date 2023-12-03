import pytest
from f2.apps.douyin.utils import extract_desc_from_share_desc


@pytest.mark.parametrize(
    "desc, share_desc, expected_output",
    [
        (
            "24小时内",
            "9.20 n@d.aa LWM:/ 03/14  24小时内，中东再次发生两件大事，哈马斯实现目标，美国战略受挫  https://v.douyin.com/idBFrT2u/ 复制此链接，打开Dou音搜索，直接观看视频！",
            "24小时内，中东再次发生两件大事，哈马斯实现目标，美国战略受挫",
        ),
        (
            "%",
            "9.20 n@d.aa LWM:/ 03/14  %  https://v.douyin.com/idBFrT2u/ 复制此链接，打开Dou音搜索，直接观看视频！",
            "%",
        ),
        (
            " ",
            "9.20 n@d.aa LWM:/ 03/14     https://v.douyin.com/idBFrT2u/ 复制此链接，打开Dou音搜索，直接观看视频！",
            " ",
        ),
        (
            "n@d.aa",
            "9.20 n@d.aa LWM:/ 03/14  n@d.aa   https://v.douyin.com/idBFrT2u/ 复制此链接，打开Dou音搜索，直接观看视频！",
            "n@d.aa",
        ),
    ],
)
def test_extract_desc_from_share_desc(desc, share_desc, expected_output):
    result = extract_desc_from_share_desc(desc, share_desc)
    assert result == expected_output

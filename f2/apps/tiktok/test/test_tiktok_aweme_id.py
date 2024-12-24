import pytest
from f2.apps.tiktok.utils import AwemeIdFetcher
from f2.utils.utils import extract_valid_urls

test_urls = [
    "https://www.tiktok.com/@justinbieber/video/7140296406429977898",
    "https://www.tiktok.com/@justinbieber/video/7140296406429977898/",
    "https://www.tiktok.com/@justinbieber/video/7140296406429977898?is_from_webapp=1&sender_device=pc&web_id=7451992228786750983",
    "https://www.tiktok.com/@justinbieber/video/7140296406429977898/?is_from_webapp=1&sender_device=pc&web_id=7451992228786750983",
    "https://vt.tiktok.com/ZS66e9D4C/",
    "https://vt.tiktok.com/ZS66e9D4C",
]

# 预期的 aweme_id 结果
expected_results = [
    "7140296406429977898",
    "7140296406429977898",
    "7140296406429977898",
    "7140296406429977898",
    "7140296406429977898",
    "7140296406429977898",
]


@pytest.mark.asyncio
async def test_get_aweme_id():
    """测试单个 URL 的 aweme_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 遍历测试每个 URL
    for url, expected_id in zip(urls, expected_results):
        result = await AwemeIdFetcher.get_aweme_id(url)
        assert (
            result == expected_id
        ), f"URL: {url} -> 预期: {expected_id}, 实际: {result}"


@pytest.mark.asyncio
async def test_get_all_aweme_id():
    """测试批量 URL 的 aweme_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 测试批量提取的结果
    results = await AwemeIdFetcher.get_all_aweme_id(urls)
    assert results == expected_results, f"预期: {expected_results}, 实际: {results}"

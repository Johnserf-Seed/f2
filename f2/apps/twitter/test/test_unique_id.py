import pytest
from f2.apps.twitter.utils import UniqueIdFetcher
from f2.exceptions.api_exceptions import (
    APINotFoundError,
)
from f2.utils.utils import extract_valid_urls


unique_id_test_urls = [
    "https://twitter.com/realDonaldTrump",
    "https://twitter.com/realDonaldTrump/",
    "https://twitter.com/realDonaldTrump/?test=123",
    "https://twitter.com/realDonaldTrump/%$#",
    "https://www.twitter.com/realDonaldTrump",
    "https://www.twitter.com/realDonaldTrump?test=123",
    "https://www.twitter.com/realDonaldTrump/",
    "https://www.twitter.com/realDonaldTrump/?test=123",
    "https://www.twitter.com/realDonaldTrump/%$#",
    "https://x.com/CaroylnG61544/followers",
    "https://x.com/CaroylnG61544/status/1440000000000000000",
    "https://twitter.com/CaroylnG61544/status/1440000000000000000/photo/1",
]

# 预期的 unique_id 结果
unique_id_expected_results = [
    "realDonaldTrump",
    "realDonaldTrump",
    "realDonaldTrump",
    "realDonaldTrump",
    "realDonaldTrump",
    "realDonaldTrump",
    "realDonaldTrump",
    "realDonaldTrump",
    "realDonaldTrump",
    "CaroylnG61544",
    "CaroylnG61544",
    "CaroylnG61544",
]


@pytest.mark.asyncio
async def test_get_unique_id():
    """测试单个 URL 的 unique_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(unique_id_test_urls)

    # 遍历测试每个 URL
    for url, expected_id in zip(urls, unique_id_expected_results):
        result = await UniqueIdFetcher.get_unique_id(url)
        assert (
            result == expected_id
        ), f"URL: {url} -> 预期: {expected_id}, 实陫: {result}"

    # 测试无效URL
    user_link = "twitter.com/realDonaldTrump"
    with pytest.raises(APINotFoundError):
        await UniqueIdFetcher.get_unique_id(user_link)


@pytest.mark.asyncio
async def test_get_all_unique_id():
    """测试批量 URL 的 unique_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(unique_id_test_urls)

    # 测试批量提取的结果
    results = await UniqueIdFetcher.get_all_unique_ids(urls)
    assert (
        results == unique_id_expected_results
    ), f"预期: {unique_id_expected_results}, 实际: {results}"

    # 测试无效URL
    test_urls = []
    with pytest.raises(APINotFoundError):
        await UniqueIdFetcher.get_all_unique_ids(test_urls)

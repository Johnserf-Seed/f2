import pytest
from f2.apps.twitter.utils import TweetIdFetcher
from f2.exceptions.api_exceptions import (
    APINotFoundError,
)
from f2.utils.utils import extract_valid_urls


test_urls = [
    "https://twitter.com/realDonaldTrump/status/1265255835124539392",
    "https://twitter.com/realDonaldTrump/status/1265255835124539392/",
    "https://twitter.com/realDonaldTrump/status/1265255835124539392/?test=123",
    "https://twitter.com/realDonaldTrump/status/1265255835124539392/%$#",
    "https://www.twitter.com/realDonaldTrump/status/1265255835124539392",
    "https://www.twitter.com/realDonaldTrump/status/1265255835124539392?test=123",
    "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/",
    "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/?test=123",
    "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/%$#",
    "https://t.co/1dBHtrG72J",
]

expected_results = [
    "1265255835124539392",
    "1265255835124539392",
    "1265255835124539392",
    "1265255835124539392",
    "1265255835124539392",
    "1265255835124539392",
    "1265255835124539392",
    "1265255835124539392",
    "1265255835124539392",
    "1777291676568166526",
]


@pytest.mark.asyncio
async def test_get_tweet_id():
    """测试单个 URL 的 tweet_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 遍历测试每个 URL
    for url, expected_id in zip(urls, expected_results):
        result = await TweetIdFetcher.get_tweet_id(url)
        assert (
            result == expected_id
        ), f"URL: {url} -> 预期: {expected_id}, 实际: {result}"

    # 测试无效的 URL
    tweet_link = "twitter.com/realDonaldTrump/status/1265255835124539392"
    with pytest.raises(APINotFoundError):
        await TweetIdFetcher.get_tweet_id(tweet_link)


@pytest.mark.asyncio
async def test_get_all_tweet_ids():
    """测试批量 URL 的 tweet_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 测试批量提取的结果
    result = await TweetIdFetcher.get_all_tweet_ids(urls)
    assert result == expected_results, f"预期: {expected_results}, 实陋: {result}"

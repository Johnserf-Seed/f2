import pytest
from f2.apps.weibo.utils import WeiboScreenNameFetcher
from f2.exceptions.api_exceptions import (
    APINotFoundError,
)
from f2.utils.utils import extract_valid_urls

screen_name_test_urls = [
    "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1",
    "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1/",
    "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1?test=123",
    "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1/?test=123",
    "https://weibo.com/n/自我充电功能丧失",
    "https://weibo.com/n/自我充电功能丧失/",
    "https://weibo.com/n/自我充电功能丧失?test=123",
    "https://weibo.com/n/自我充电功能丧失/?test=123",
]

# 预期的 screen_name 结果
screen_name_expected_results = [
    "自我充电功能丧失",
    "自我充电功能丧失",
    "自我充电功能丧失",
    "自我充电功能丧失",
    "自我充电功能丧失",
    "自我充电功能丧失",
    "自我充电功能丧失",
    "自我充电功能丧失",
]


@pytest.mark.asyncio
async def test_get_weibo_screen_name():
    """测试单个 URL 的 screen_name 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(screen_name_test_urls)

    # 遍历测试每个 URL
    for url, expected_name in zip(urls, screen_name_expected_results):
        result = await WeiboScreenNameFetcher.get_weibo_screen_name(url)
        assert (
            result == expected_name
        ), f"URL: {url} -> 预期: {expected_name}, 实际: {result}"

    # 测试无效URL
    weibo_name_url = ""
    with pytest.raises(ValueError):
        await WeiboScreenNameFetcher.get_weibo_screen_name(weibo_name_url)

    weibo_name_url = None
    with pytest.raises(ValueError):
        await WeiboScreenNameFetcher.get_weibo_screen_name(weibo_name_url)

    weibo_name_url = "weibo.com/n/自我充电功能丧失"
    with pytest.raises(APINotFoundError):
        await WeiboScreenNameFetcher.get_weibo_screen_name(weibo_name_url)

    weibo_name_url = "http://weibo.com/自我充电功能丧失"
    with pytest.raises(APINotFoundError):
        await WeiboScreenNameFetcher.get_weibo_screen_name(weibo_name_url)


@pytest.mark.asyncio
async def test_get_weibo_all_screen_name():
    """测试批量 URL 的 screen_name 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(screen_name_test_urls)

    # 测试批量提取的结果
    results = await WeiboScreenNameFetcher.get_all_weibo_screen_name(urls)
    assert (
        results == screen_name_expected_results
    ), f"预期: {screen_name_expected_results}, 实际: {results}"

    # 测试无效URL
    weibo_urls = [
        "weibo.com/n/自我充电功能丧失",
        "http://weibo.com/自我充电功能丧失",
        "https://weibo.com/O8DM0BLLm/?test=123",
        "https://weibo.com/userid/postid/",
    ]

    with pytest.raises(APINotFoundError):
        await WeiboScreenNameFetcher.get_all_weibo_screen_name(weibo_urls)

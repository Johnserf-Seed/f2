import pytest
from f2.apps.weibo.utils import WeiboUidFetcher
from f2.exceptions.api_exceptions import (
    APINotFoundError,
)
from f2.utils.utils import extract_valid_urls

weibo_uid_test_urls = [
    "https://weibo.com/u/2265830070",
    "https://weibo.com/u/2265830070?test=123",
    "https://weibo.com/u/2265830070/",
    "https://weibo.com/u/2265830070/?test=123",
    "https://weibo.com/2265830070",
    "https://weibo.com/2265830070/",
    "https://weibo.com/2265830070/?test=123",
    "https://weibo.com/2265830070/O8DM0BLLm",
    "https://weibo.com/2265830070/O8DM0BLLm/",
    "https://weibo.com/2265830070/O8DM0BLLm/?test=123",
    "https://weibo.com/2265830070/O8DM0BLLm/%$#",
    "https://m.weibo.cn/2265830070/5020595169001740",
    "https://m.weibo.cn/2265830070/5020595169001740?test=123",
    "https://m.weibo.cn/2265830070/5020595169001740/",
    "https://m.weibo.cn/2265830070/5020595169001740/?test=123",
    "https://weibo.cn/2265830070/5020595169001740",
    "https://weibo.cn/2265830070/5020595169001740?test=123",
    "https://weibo.cn/2265830070/5020595169001740/",
    "https://weibo.cn/2265830070/5020595169001740/?test=123",
    "https://weibo.com/2265830070/O8DM0BLLm/" + "a" * 2048,
]

# 预期的 weibo_uid 结果
weibo_uid_expected_results = [
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
    "2265830070",
]


@pytest.mark.asyncio
async def test_get_weibo_uid():
    """测试单个 URL 的 weibo_uid 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(weibo_uid_test_urls)

    # 遍历测试每个 URL
    for url, expected_uid in zip(urls, weibo_uid_expected_results):
        result = await WeiboUidFetcher.get_weibo_uid(url)
        assert (
            result == expected_uid
        ), f"URL: {url} -> 预期: {expected_uid}, 实际: {result}"

    # 测试无效URL
    weibo_link = "weibo.com/2265830070/O8DM0BLLm"
    with pytest.raises(APINotFoundError):
        await WeiboUidFetcher.get_weibo_uid(weibo_link)

    weibo_link = "https://weibo.com/O8DM0BLLm"
    with pytest.raises(APINotFoundError):
        await WeiboUidFetcher.get_weibo_uid(weibo_link)

    weibo_link = "https://weibo.com/O8DM0BLLm/"
    with pytest.raises(APINotFoundError):
        await WeiboUidFetcher.get_weibo_uid(weibo_link)

    weibo_link = "https://weibo.com/O8DM0BLLm/?test=123"
    with pytest.raises(APINotFoundError):
        await WeiboUidFetcher.get_weibo_uid(weibo_link)

    weibo_link = "https://weibo.com/userid/postid/"
    with pytest.raises(APINotFoundError):
        await WeiboUidFetcher.get_weibo_uid(weibo_link)

    weibo_link = ""
    with pytest.raises(ValueError):
        await WeiboUidFetcher.get_weibo_uid(weibo_link)

    weibo_link = None
    with pytest.raises(ValueError):
        await WeiboUidFetcher.get_weibo_uid(weibo_link)


@pytest.mark.asyncio
async def test_get_all_weibo_uid():
    """测试批量 URL 的 weibo_uid 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(weibo_uid_test_urls)

    # 测试批量提取的结果
    results = await WeiboUidFetcher.get_all_weibo_uid(urls)
    assert (
        results == weibo_uid_expected_results
    ), f"预期: {weibo_uid_expected_results}, 实际: {results}"

    # 测试无效URL
    weibo_links = [
        "weibo.com/O8DM0BLLm",
        "https://weibo.com/O8DM0BLLm",
        "https://weibo.com/O8DM0BLLm/",
        "https://weibo.com/O8DM0BLLm/?test=123",
        "https://weibo.com/userid/postid/",
    ]
    with pytest.raises(APINotFoundError):
        await WeiboUidFetcher.get_all_weibo_uid(weibo_links)

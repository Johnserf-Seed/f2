import pytest
from f2.apps.weibo.utils import WeiboIdFetcher
from f2.exceptions.api_exceptions import (
    APINotFoundError,
)
from f2.utils.utils import extract_valid_urls

weibo_id_test_urls = [
    "https://weibo.com/2265830070/O8DM0BLLm",
    "https://weibo.com/2265830070/O8DM0BLLm/",
    "https://weibo.com/2265830070/O8DM0BLLm/?test=123",
    "https://weibo.com/2265830070/O8DM0BLLm/%$#",
    "https://www.weibo.com/2265830070/5020595169001740",
    "https://www.weibo.com/2265830070/5020595169001740?test=123",
    "https://www.weibo.com/2265830070/5020595169001740/",
    "https://www.weibo.com/2265830070/5020595169001740/?test=123",
    "https://m.weibo.cn/2265830070/5020595169001740",
    "https://m.weibo.cn/2265830070/5020595169001740?test=123",
    "https://m.weibo.cn/2265830070/5020595169001740/",
    "https://m.weibo.cn/2265830070/5020595169001740/?test=123",
    "https://weibo.cn/2265830070/O8DM0BLLm/",
    "https://weibo.cn/2265830070/O8DM0BLLm/?test=123",
    "https://weibo.cn/2265830070/O8DM0BLLm",
    "https://weibo.cn/2265830070/O8DM0BLLm?test=123",
    "https://weibo.cn/status/5020595169001740",
    "https://weibo.cn/status/5020595169001740?test=123",
    "https://weibo.cn/status/5020595169001740/",
    "https://weibo.cn/status/5020595169001740/?test=123",
    "https://weibo.com/2265830070/O8DM0BLLm/" + "a" * 2048,
]

# 预期的 weibo_id 结果
weibo_id_expected_results = [
    "O8DM0BLLm",
    "O8DM0BLLm",
    "O8DM0BLLm",
    "O8DM0BLLm",
    "5020595169001740",
    "5020595169001740",
    "5020595169001740",
    "5020595169001740",
    "5020595169001740",
    "5020595169001740",
    "5020595169001740",
    "5020595169001740",
    "O8DM0BLLm",
    "O8DM0BLLm",
    "O8DM0BLLm",
    "O8DM0BLLm",
    "5020595169001740",
    "5020595169001740",
    "5020595169001740",
    "5020595169001740",
    "O8DM0BLLm",
]


@pytest.mark.asyncio
class TestWeiboIdFetcher:
    async def test_get_weibo_id(self):
        """测试单个 URL 的 weibo_id 提取功能"""

        # 提取有效URL
        urls = extract_valid_urls(weibo_id_test_urls)

        # 遍历测试每个 URL
        for url, expected_id in zip(urls, weibo_id_expected_results):
            result = await WeiboIdFetcher.get_weibo_id(url)
            assert (
                result == expected_id
            ), f"URL: {url} -> 预期: {expected_id}, 实际: {result}"

        # 测试无效URL
        weibo_link = "https://weibo.com/u/2265830070/O8DM0BLLm"
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)

        weibo_link = "https://weibo.com/u/2265830070/O8DM0BLLm?test=123"
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)

        weibo_link = "https://weibo.com/u/2265830070/O8DM0BLLm/"
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)

        weibo_link = "https://weibo.com/u/2265830070/O8DM0BLLm/?test=123"
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)

        weibo_link = "weibo.com/2265830070/O8DM0BLLm"
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)

        weibo_link = "https://weibo.com/2265830070"
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)

        weibo_link = "https://weibo.com/2265830070/"
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)

        weibo_link = "https://weibo.com/2265830070/?test=123"
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)

        weibo_link = "https://weibo.com/userid/postid/"
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)

        weibo_link = ""
        with pytest.raises(ValueError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)

        weibo_link = None
        with pytest.raises(ValueError):
            await WeiboIdFetcher.get_weibo_id(weibo_link)


@pytest.mark.asyncio
class TestWeiboAllIdFetcher:
    async def test_get_all_weibo_id(self):
        """测试批量 URL 的 weibo_id 提取功能"""

        # 提取有效URL
        urls = extract_valid_urls(weibo_id_test_urls)

        # 测试批量提取的结果
        results = await WeiboIdFetcher.get_all_weibo_id(urls)
        assert (
            results == weibo_id_expected_results
        ), f"预期: {weibo_id_expected_results}, 实陋: {results}"

        # 测试无效URL
        weibo_links = []
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_all_weibo_id(weibo_links)

        weibo_links = [
            "weibo.com/2265830070",
            "https://weibo.com/2265830070",
            "https://weibo.com/2265830070/",
            "https://weibo.com/2265830070/?test=123",
            "https://weibo.com/userid/postid/",
        ]
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_all_weibo_id(weibo_links)

import pytest
from f2.apps.twitter.utils import UniqueIdFetcher
from f2.exceptions.api_exceptions import (
    APINotFoundError,
)


@pytest.mark.asyncio
class TestUserIdFetcher:
    async def test_get_unique_id(self):
        user_link = "https://twitter.com/realDonaldTrump"
        unique_id = await UniqueIdFetcher.get_unique_id(user_link)
        assert unique_id == "realDonaldTrump"

        user_link = "https://twitter.com/realDonaldTrump/"
        unique_id = await UniqueIdFetcher.get_unique_id(user_link)
        assert unique_id == "realDonaldTrump"

        user_link = "https://twitter.com/realDonaldTrump/?test=123"
        unique_id = await UniqueIdFetcher.get_unique_id(user_link)
        assert unique_id == "realDonaldTrump"

        user_link = "https://twitter.com/realDonaldTrump/%$#"
        unique_id = await UniqueIdFetcher.get_unique_id(user_link)
        assert unique_id == "realDonaldTrump"

        user_link = "https://www.twitter.com/realDonaldTrump"
        unique_id = await UniqueIdFetcher.get_unique_id(user_link)
        assert unique_id == "realDonaldTrump"

        user_link = "https://www.twitter.com/realDonaldTrump?test=123"
        unique_id = await UniqueIdFetcher.get_unique_id(user_link)
        assert unique_id == "realDonaldTrump"

        user_link = "https://www.twitter.com/realDonaldTrump/"
        unique_id = await UniqueIdFetcher.get_unique_id(user_link)
        assert unique_id == "realDonaldTrump"

        user_link = "https://www.twitter.com/realDonaldTrump/?test=123"
        unique_id = await UniqueIdFetcher.get_unique_id(user_link)
        assert unique_id == "realDonaldTrump"

        user_link = "https://www.twitter.com/realDonaldTrump/%$#"
        unique_id = await UniqueIdFetcher.get_unique_id(user_link)
        assert unique_id == "realDonaldTrump"

        user_link = "twitter.com/realDonaldTrump"
        with pytest.raises(APINotFoundError):
            await UniqueIdFetcher.get_unique_id(user_link)


@pytest.mark.asyncio
class TestUserListIdFetcher:
    async def test_get_all_unique_id(self):

        test_urls = []
        with pytest.raises(APINotFoundError):
            await UniqueIdFetcher.get_all_unique_ids(test_urls)

        test_urls = [
            "https://x.com/CaroylnG61544",
            "https://x.com/CaroylnG61544/",
            "https://x.com/CaroylnG61544/followers",
            "https://x.com/CaroylnG61544/status/1440000000000000000",
            "https://twitter.com/CaroylnG61544/status/1440000000000000000/photo/1",
        ]

        # 预期的 unique_id 结果
        expected_results = [
            "CaroylnG61544",
            "CaroylnG61544",
            "CaroylnG61544",
            "CaroylnG61544",
            "CaroylnG61544",
        ]

        # 测试批量提取的结果
        results = await UniqueIdFetcher.get_all_unique_ids(test_urls)
        assert results == expected_results, f"预期: {expected_results}, 实际: {results}"

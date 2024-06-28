import pytest
from f2.apps.weibo.utils import WeiboIdFetcher
from f2.exceptions.api_exceptions import (
    APINotFoundError,
)


@pytest.mark.asyncio
class TestWeiboIdFetcher:
    async def test_get_weibo_id(self):
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

        weibo_link = "https://weibo.com/2265830070/O8DM0BLLm"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "O8DM0BLLm"

        weibo_link = "https://weibo.com/2265830070/O8DM0BLLm/"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "O8DM0BLLm"

        weibo_link = "https://weibo.com/2265830070/O8DM0BLLm/?test=123"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "O8DM0BLLm"

        weibo_link = "https://weibo.com/2265830070/O8DM0BLLm/%$#"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "O8DM0BLLm"

        weibo_link = "https://www.weibo.com/2265830070/5020595169001740"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://www.weibo.com/2265830070/5020595169001740?test=123"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://www.weibo.com/2265830070/5020595169001740/"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://www.weibo.com/2265830070/5020595169001740/?test=123"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://m.weibo.cn/2265830070/5020595169001740"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://m.weibo.cn/2265830070/5020595169001740?test=123"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://m.weibo.cn/2265830070/5020595169001740/"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://m.weibo.cn/2265830070/5020595169001740/?test=123"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://weibo.cn/2265830070/O8DM0BLLm/"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "O8DM0BLLm"

        weibo_link = "https://weibo.cn/2265830070/O8DM0BLLm/?test=123"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "O8DM0BLLm"

        weibo_link = "https://weibo.cn/2265830070/O8DM0BLLm"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "O8DM0BLLm"

        weibo_link = "https://weibo.cn/2265830070/O8DM0BLLm?test=123"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "O8DM0BLLm"

        weibo_link = "https://weibo.cn/status/5020595169001740"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://weibo.cn/status/5020595169001740?test=123"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://weibo.cn/status/5020595169001740/"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

        weibo_link = "https://weibo.cn/status/5020595169001740/?test=123"
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "5020595169001740"

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

        weibo_link = "https://weibo.com/2265830070/O8DM0BLLm/" + "a" * 2048
        weibo_id = await WeiboIdFetcher.get_weibo_id(weibo_link)
        assert weibo_id == "O8DM0BLLm"


@pytest.mark.asyncio
class TestWeiboAllIdFetcher:
    async def test_get_all_weibo_id(self):
        weibo_links = []
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_all_weibo_id(weibo_links)

        weibo_links = [
            "https://weibo.com/u/2265830070/O8DM0BLLm",
            "https://weibo.com/u/2265830070/O8DM0BLLm/",
            "https://weibo.com/u/2265830070/O8DM0BLLm/?test=123",
        ]
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_all_weibo_id(weibo_links)

        weibo_links = [
            "https://weibo.com/2265830070/O8DM0BLLm",
            "https://weibo.com/2265830070/O8DM0BLLm/",
            "https://weibo.com/2265830070/O8DM0BLLm/?test=123",
            "https://weibo.com/2265830070/O8DM0BLLm/%$#",
            "https://weibo.com/2265830070/O8DM0BLLm/" + "a" * 2048,
        ]
        weibo_ids = await WeiboIdFetcher.get_all_weibo_id(weibo_links)
        assert weibo_ids == [
            "O8DM0BLLm",
            "O8DM0BLLm",
            "O8DM0BLLm",
            "O8DM0BLLm",
            "O8DM0BLLm",
        ]

        weibo_links = [
            "https://www.weibo.com/2265830070/5020595169001740",
            "https://www.weibo.com/2265830070/5020595169001740/",
            "https://www.weibo.com/2265830070/5020595169001740/?test=123",
            "https://www.weibo.com/2265830070/5020595169001740/%$#",
            "https://www.weibo.com/2265830070/5020595169001740/" + "a" * 2048,
            "https://weibo.cn/status/5020595169001740",
            "https://weibo.cn/status/5020595169001740?test=123",
            "https://m.weibo.cn/status/5020595169001740/",
            "https://m.weibo.cn/status/5020595169001740/?test=123",
            "https://m.weibo.cn/status/5020595169001740/%$#",
            "https://m.weibo.cn/status/5020595169001740/" + "a" * 2048,
        ]
        weibo_ids = await WeiboIdFetcher.get_all_weibo_id(weibo_links)
        assert weibo_ids == [
            "5020595169001740",
            "5020595169001740",
            "5020595169001740",
            "5020595169001740",
            "5020595169001740",
            "5020595169001740",
            "5020595169001740",
            "5020595169001740",
            "5020595169001740",
            "5020595169001740",
            "5020595169001740",
        ]

        weibo_links = [
            "weibo.com/2265830070",
            "https://weibo.com/2265830070",
            "https://weibo.com/2265830070/",
            "https://weibo.com/2265830070/?test=123",
            "https://weibo.com/userid/postid/",
        ]
        with pytest.raises(APINotFoundError):
            await WeiboIdFetcher.get_all_weibo_id(weibo_links)

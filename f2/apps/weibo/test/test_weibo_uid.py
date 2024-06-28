import pytest
from f2.apps.weibo.utils import WeiboUidFetcher
from f2.exceptions.api_exceptions import (
    APINotFoundError,
)


@pytest.mark.asyncio
class TestWeiboUidFetcher:
    async def test_get_weibo_uid(self):
        weibo_id = "https://weibo.com/u/2265830070"
        weibo_uid = await WeiboUidFetcher.get_weibo_uid(weibo_id)
        assert weibo_uid == "2265830070"

        weibo_id = "https://weibo.com/u/2265830070?test=123"
        weibo_uid = await WeiboUidFetcher.get_weibo_uid(weibo_id)
        assert weibo_uid == "2265830070"

        weibo_id = "https://weibo.com/u/2265830070/"
        weibo_uid = await WeiboUidFetcher.get_weibo_uid(weibo_id)
        assert weibo_uid == "2265830070"

        weibo_id = "https://weibo.com/u/2265830070/?test=123"
        weibo_uid = await WeiboUidFetcher.get_weibo_uid(weibo_id)
        assert weibo_uid == "2265830070"

        weibo_link = "https://weibo.com/2265830070"
        weibo_uid = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_uid == "2265830070"

        weibo_link = "https://weibo.com/2265830070/"
        weibo_uid = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_uid == "2265830070"

        weibo_link = "https://weibo.com/2265830070/?test=123"
        weibo_uid = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_uid == "2265830070"

        weibo_link = "https://weibo.com/2265830070/O8DM0BLLm"
        weibo_uid = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_uid == "2265830070"

        weibo_link = "https://weibo.com/2265830070/O8DM0BLLm/"
        weibo_uid = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_uid == "2265830070"

        weibo_link = "https://weibo.com/2265830070/O8DM0BLLm/?test=123"
        weibo_uid = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_uid == "2265830070"

        weibo_link = "https://weibo.com/2265830070/O8DM0BLLm/%$#"
        weibo_id = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_id == "2265830070"

        weibo_link = "https://m.weibo.cn/2265830070/5020595169001740"
        weibo_id = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_id == "2265830070"

        weibo_link = "https://m.weibo.cn/2265830070/5020595169001740?test=123"
        weibo_id = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_id == "2265830070"

        weibo_link = "https://m.weibo.cn/2265830070/5020595169001740/"
        weibo_id = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_id == "2265830070"

        weibo_link = "https://m.weibo.cn/2265830070/5020595169001740/?test=123"
        weibo_id = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_id == "2265830070"

        weibo_link = "https://weibo.cn/2265830070/5020595169001740"
        weibo_id = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_id == "2265830070"

        weibo_link = "https://weibo.cn/2265830070/5020595169001740?test=123"
        weibo_id = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_id == "2265830070"

        weibo_link = "https://weibo.cn/2265830070/5020595169001740/"
        weibo_id = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_id == "2265830070"

        weibo_link = "https://weibo.cn/2265830070/5020595169001740/?test=123"
        weibo_id = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_id == "2265830070"

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

        weibo_link = "https://weibo.com/2265830070/O8DM0BLLm/" + "a" * 2048
        weibo_id = await WeiboUidFetcher.get_weibo_uid(weibo_link)
        assert weibo_id == "2265830070"


@pytest.mark.asyncio
class TestWeiboAllUidFetcher:
    async def test_get_all_weibo_uid(self):
        weibo_links = [
            "https://weibo.com/u/2265830070",
            "https://weibo.com/u/2265830070/",
            "https://weibo.com/u/2265830070/?test=123",
            "https://weibo.com/2265830070",
            "https://weibo.com/2265830070/",
            "https://weibo.com/2265830070/?test=123",
            "https://weibo.com/2265830070/O8DM0BLLm",
            "https://weibo.com/2265830070/O8DM0BLLm/",
            "https://weibo.com/2265830070/O8DM0BLLm/?test=123",
            "https://weibo.com/2265830070/O8DM0BLLm/%$#",
            "https://weibo.com/2265830070/O8DM0BLLm/" + "a" * 2048,
            "https://m.weibo.cn/2265830070/5020595169001740",
            "https://m.weibo.cn/2265830070/5020595169001740?test=123",
            "https://m.weibo.cn/2265830070/5020595169001740/",
            "https://m.weibo.cn/2265830070/5020595169001740/?test=123",
        ]
        weibo_uids = await WeiboUidFetcher.get_all_weibo_uid(weibo_links)
        assert weibo_uids == [
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

        weibo_links = [
            "weibo.com/O8DM0BLLm",
            "https://weibo.com/O8DM0BLLm",
            "https://weibo.com/O8DM0BLLm/",
            "https://weibo.com/O8DM0BLLm/?test=123",
            "https://weibo.com/userid/postid/",
        ]
        with pytest.raises(APINotFoundError):
            await WeiboUidFetcher.get_all_weibo_uid(weibo_links)

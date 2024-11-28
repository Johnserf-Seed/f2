import pytest
from f2.apps.weibo.utils import WeiboScreenNameFetcher
from f2.exceptions.api_exceptions import (
    APINotFoundError,
)


@pytest.mark.asyncio
class TestWeiboScreenNameFetcher:
    async def test_get_weibo_screen_name(self):
        weibo_name_url = "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1"
        weibo_screen_name = await WeiboScreenNameFetcher.get_weibo_screen_name(
            weibo_name_url
        )
        assert weibo_screen_name == "自我充电功能丧失"

        weibo_name_url = "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1/"
        weibo_screen_name = await WeiboScreenNameFetcher.get_weibo_screen_name(
            weibo_name_url
        )
        assert weibo_screen_name == "自我充电功能丧失"

        weibo_name_url = "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1?test=123"
        weibo_screen_name = await WeiboScreenNameFetcher.get_weibo_screen_name(
            weibo_name_url
        )
        assert weibo_screen_name == "自我充电功能丧失"

        weibo_name_url = "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1/?test=123"
        weibo_screen_name = await WeiboScreenNameFetcher.get_weibo_screen_name(
            weibo_name_url
        )
        assert weibo_screen_name == "自我充电功能丧失"

        weibo_name_url = "https://weibo.com/n/自我充电功能丧失"
        weibo_screen_name = await WeiboScreenNameFetcher.get_weibo_screen_name(
            weibo_name_url
        )
        assert weibo_screen_name == "自我充电功能丧失"

        weibo_name_url = "https://weibo.com/n/自我充电功能丧失/"
        weibo_screen_name = await WeiboScreenNameFetcher.get_weibo_screen_name(
            weibo_name_url
        )
        assert weibo_screen_name == "自我充电功能丧失"

        weibo_name_url = "https://weibo.com/n/自我充电功能丧失?test=123"
        weibo_screen_name = await WeiboScreenNameFetcher.get_weibo_screen_name(
            weibo_name_url
        )
        assert weibo_screen_name == "自我充电功能丧失"

        weibo_name_url = "https://weibo.com/n/自我充电功能丧失/?test=123"
        weibo_screen_name = await WeiboScreenNameFetcher.get_weibo_screen_name(
            weibo_name_url
        )
        assert weibo_screen_name == "自我充电功能丧失"

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

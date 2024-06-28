import pytest
from f2.apps.douyin.model import UserPost
from f2.apps.douyin.filter import UserPostFilter
from f2.apps.douyin.crawler import DouyinCrawler
from f2.utils.conf_manager import TestConfigManager


@pytest.fixture
def cookie_fixture():
    return TestConfigManager.get_test_config("douyin")


@pytest.mark.asyncio
async def test_crawler_fetcher(cookie_fixture):
    async with DouyinCrawler(cookie_fixture) as crawler:
        params = UserPost(
            max_cursor=0,
            count=1,
            sec_user_id="MS4wLjABAAAAu8qwDm1-muGuMhZZ-tVzyPVWlUxIbQRNJN_9k83OhWU",
        )
        response = await crawler.fetch_user_post(params)
        assert response, "Failed to fetch user post"

        video = UserPostFilter(response)
        video_id = video.aweme_id
        assert video_id, "Failed to extract video ID"

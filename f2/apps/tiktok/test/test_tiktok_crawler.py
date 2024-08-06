import pytest
from f2.apps.tiktok.model import UserPost
from f2.apps.tiktok.filter import UserPostFilter
from f2.apps.tiktok.crawler import TiktokCrawler
from f2.utils.conf_manager import TestConfigManager


@pytest.fixture
def cookie_fixture():
    return TestConfigManager.get_test_config("tiktok")


@pytest.mark.asyncio
async def test_crawler_by_secUid(cookie_fixture):
    async with TiktokCrawler(cookie_fixture) as crawler:
        params = UserPost(
            cursor=0,
            count=5,
            secUid="MS4wLjABAAAAREbjjYuEFoUJN86G9f2byGC_LSOTz4N7BGdreT_8Cro-NkzZYf_nxpDpLp9R6ElJ",
        )
        response = await crawler.fetch_user_post(params)
        assert response, "Failed to fetch user post"

        video = UserPostFilter(response)
        video_id = video.aweme_id
        assert video_id, "Failed to extract video ID"

import pytest
from f2.apps.douyin.model import UserPost
from f2.apps.douyin.filter import UserPostFilter
from f2.apps.douyin.crawler import DouyinCrawler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "cookie": "YOUR_COOKIE_HERE",
}


@pytest.mark.asyncio
async def test_crawler_fetcher():
    async with DouyinCrawler(kwargs) as crawler:
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

import asyncio
from f2.apps.douyin.model import UserPost
from f2.apps.douyin.filter import UserPostFilter
from f2.apps.douyin.crawler import DouyinCrawler

async def test_user_post_fetcher():
    async with DouyinCrawler() as crawler:
        params = UserPost(
            max_cursor = 0,
            count = 5,
            sec_user_id = "MS4wLjABAAAAu8qwDm1-muGuMhZZ-tVzyPVWlUxIbQRNJN_9k83OhWU"
        )
        response = await crawler.fetch_user_post(params)

        video = UserPostFilter(response)
        print(f'作者:{video.nickname[0]}, 所有作品id:{video.aweme_id}, 每个作品的码率{video.video_bit_rate}')

if __name__ == '__main__':
    asyncio.run(test_user_post_fetcher())
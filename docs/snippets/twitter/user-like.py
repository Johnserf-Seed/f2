import asyncio

from f2.apps.twitter.handler import TwitterHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.x.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
    # "X-Csrf-Token": "",
}


async def main():
    userId = "25073877"  # realDonaldTrump
    async for tweet_list in TwitterHandler(kwargs).fetch_like_tweet(
        userId=userId,
        page_counts=20,
        max_cursor="",
        max_counts=20,
    ):
        print("=================_to_raw================")
        print(tweet_list._to_raw())
        # print("=================_to_dict===============")
        # print(tweet_list._to_dict())
        # print("=================_to_list===============")
        # print(tweet_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())

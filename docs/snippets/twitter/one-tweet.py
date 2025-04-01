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
    tweet = await TwitterHandler(kwargs).fetch_one_tweet(tweet_id="1863009545858998512")

    print("=================_to_raw================")
    print(tweet._to_raw())
    # print("=================_to_dict================")
    # print(tweet._to_dict())


if __name__ == "__main__":
    asyncio.run(main())

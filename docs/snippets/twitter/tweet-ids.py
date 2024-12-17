# region single-tweet-id-snippet
import asyncio
from f2.apps.twitter.utils import TweetIdFetcher
from f2.log.logger import logger


async def main():
    tweet_link = "https://twitter.com/realDonaldTrump/status/1265255835124539392"
    tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
    logger.info(tweet_id)


if __name__ == "__main__":
    asyncio.run(main())

# endregion single-tweet-id-snippet

# region multi-tweet-id-snippet
import asyncio
from f2.apps.twitter.utils import TweetIdFetcher
from f2.log.logger import logger


async def main():
    test_urls = [
        "https://twitter.com/realDonaldTrump/status/1265255835124539392",
        "https://twitter.com/realDonaldTrump/status/1265255835124539392/",
        "https://twitter.com/realDonaldTrump/status/1265255835124539392/?test=123",
        "https://twitter.com/realDonaldTrump/status/1265255835124539392/%$#",
        "https://www.twitter.com/realDonaldTrump/status/1265255835124539392",
        "https://www.twitter.com/realDonaldTrump/status/1265255835124539392?test=123",
        "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/",
        "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/?test=123",
        "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/%$#",
        "https://t.co/1dBHtrG72J",
    ]
    tweet_ids = await TweetIdFetcher.get_all_tweet_ids(test_urls)
    logger.info(tweet_ids)


if __name__ == "__main__":
    asyncio.run(main())

# endregion multi-tweet-id-snippet

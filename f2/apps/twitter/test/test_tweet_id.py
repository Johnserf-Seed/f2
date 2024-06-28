import pytest
from f2.apps.twitter.utils import TweetIdFetcher
from f2.exceptions.api_exceptions import (
    APINotFoundError,
)


@pytest.mark.asyncio
class TestTweetIdFetcher:
    async def test_get_tweet_id(self):
        tweet_link = "https://twitter.com/realDonaldTrump/status/1265255835124539392"
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = "https://twitter.com/realDonaldTrump/status/1265255835124539392/"
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = (
            "https://twitter.com/realDonaldTrump/status/1265255835124539392/?test=123"
        )
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = (
            "https://twitter.com/realDonaldTrump/status/1265255835124539392/%$#"
        )
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = (
            "https://www.twitter.com/realDonaldTrump/status/1265255835124539392"
        )
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = "https://www.twitter.com/realDonaldTrump/status/1265255835124539392?test=123"
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = (
            "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/"
        )
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/?test=123"
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = (
            "https://www.twitter.com/realDonaldTrump/status/1265255835124539392/%$#"
        )
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1265255835124539392"

        tweet_link = "twitter.com/realDonaldTrump/status/1265255835124539392"
        with pytest.raises(APINotFoundError):
            await TweetIdFetcher.get_tweet_id(tweet_link)

        tweet_link = "https://t.co/1dBHtrG72J"
        tweet_id = await TweetIdFetcher.get_tweet_id(tweet_link)
        assert tweet_id == "1777291676568166526"

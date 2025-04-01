# region single-user-unique-id-snippet
import asyncio

from f2.apps.twitter.utils import UniqueIdFetcher
from f2.log.logger import logger


async def main():
    user_link = "https://twitter.com/realDonaldTrump"
    unique_id = await UniqueIdFetcher.get_unique_id(user_link)
    logger.info(unique_id)


if __name__ == "__main__":
    asyncio.run(main())

# endregion single-user-unique-id-snippet

# region multi-user-unique-id-snippet
import asyncio

from f2.apps.twitter.utils import UniqueIdFetcher
from f2.log.logger import logger


async def main():
    test_urls = [
        "https://twitter.com/realDonaldTrump",
        "https://twitter.com/realDonaldTrump/",
        "https://twitter.com/realDonaldTrump/?test=123",
        "https://twitter.com/realDonaldTrump/%$#",
        "https://www.twitter.com/realDonaldTrump",
        "https://www.twitter.com/realDonaldTrump?test=123",
        "https://www.twitter.com/realDonaldTrump/",
        "https://www.twitter.com/realDonaldTrump/?test=123",
        "https://www.twitter.com/realDonaldTrump/%$#",
    ]
    unique_ids = await UniqueIdFetcher.get_all_unique_ids(test_urls)
    logger.info(unique_ids)


if __name__ == "__main__":
    asyncio.run(main())

# endregion multi-user-unique-id-snippet

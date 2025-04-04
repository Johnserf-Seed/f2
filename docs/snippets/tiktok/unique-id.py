# region single-unique-id-snippet
import asyncio

from f2.apps.tiktok.utils import SecUserIdFetcher


async def main():
    raw_url = "https://www.tiktok.com/@vantoan___"
    # 对于单个URL
    return await SecUserIdFetcher.get_uniqueid(raw_url)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion single-unique-id-snippet


# region multi-unique-id-snippet
import asyncio

from f2.apps.tiktok.utils import SecUserIdFetcher
from f2.utils.string.formatter import extract_valid_urls


async def main():
    raw_urls = [
        "https://www.tiktok.com/@vantoan___/",
        "https://www.tiktok.com/@vantoan___?is_from_webapp=1&sender_device=pc",
        # "https://vt.tiktok.com/xxxxxxxxxx/"
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)

    # 对于URL列表
    return await SecUserIdFetcher.get_all_uniqueid(urls)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion multi-unique-id-snippet

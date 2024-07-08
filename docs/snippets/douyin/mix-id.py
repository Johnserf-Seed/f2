# region single-mix-id-snippet
import asyncio
from f2.apps.douyin.utils import MixIdFetcher


async def main():
    raw_url = "https://www.douyin.com/collection/7360898383181809676"
    return await MixIdFetcher.get_mix_id(raw_url)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion single-mix-id-snippet


# region multi-mix-id-snippet
import asyncio
from f2.apps.douyin.utils import MixIdFetcher
from f2.utils.utils import extract_valid_urls


async def main():
    raw_urls = [
        "https://www.douyin.com/collection/7360898383181809676",
        "https://www.douyin.com/collection/7270895771149404160",
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)

    # 对于URL列表
    return await MixIdFetcher.get_all_mix_id(urls)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion multi-mix-id-snippet

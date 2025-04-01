# region single-aweme-id-snippet
import asyncio

from f2.apps.tiktok.utils import AwemeIdFetcher


async def main():
    raw_url = "https://www.tiktok.com/@vantoan___/video/7283528426256911649"
    # 支持短链解析但其具有时效性，故不举例
    return await AwemeIdFetcher.get_aweme_id(raw_url)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion single-aweme-id-snippet


# region multi-aweme-id-snippet
import asyncio

from f2.apps.tiktok.utils import AwemeIdFetcher
from f2.utils.utils import extract_valid_urls


async def main():
    raw_urls = [
        "https://www.tiktok.com/@vantoan___/video/7316948869764484384",
        "https://www.tiktok.com/@vantoan___/video/7316948869764484384?is_from_webapp=1&sender_device=pc&web_id=7306060721837852167",
        # 支持短链解析但其具有时效性，故不举例
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)

    # 对于URL列表
    return await AwemeIdFetcher.get_all_aweme_id(urls)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion multi-aweme-id-snippet

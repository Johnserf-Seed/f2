# region single-user-id-snippet
import asyncio

from f2.apps.douyin.utils import SecUserIdFetcher


async def main():
    raw_url = "https://www.douyin.com/user/MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE?vid=7285950278132616463"
    # 对于单个URL
    return await SecUserIdFetcher.get_sec_user_id(raw_url)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion single-user-id-snippet


# region multi-user-id-snippet
import asyncio

from f2.apps.douyin.utils import SecUserIdFetcher
from f2.utils.utils import extract_valid_urls


async def main():
    raw_urls = [
        "https://www.douyin.com/user/MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE?vid=7285950278132616463",
        "https://www.douyin.com/user/MS4wLjABAAAAVsneOf144eGDFf8Xp9QNb1VW6ovXnNT5SqJBhJfe8KQBKWKDTWK5Hh-_i9mJzb8C",
        "长按复制此条消息，打开抖音搜索，查看TA的更多作品。 https://v.douyin.com/idFqvUms/",
        "https://v.douyin.com/idFqvUms/",
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)

    # 对于URL列表
    return await SecUserIdFetcher.get_all_sec_user_id(urls)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion multi-user-id-snippet

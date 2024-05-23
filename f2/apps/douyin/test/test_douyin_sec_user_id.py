import pytest
from f2.apps.douyin.utils import SecUserIdFetcher
from f2.utils.utils import extract_valid_urls


@pytest.mark.asyncio
async def test_sec_user_id_fetcher():
    raw_urls = [
        "https://www.douyin.com/user/MS4wLjABAAAAVsneOf144eGDFf8Xp9QNb1VW6ovXnNT5SqJBhJfe8KQBKWKDTWK5Hh-_i9mJzb8C?vid=7285950278132616463",
        "https://www.douyin.com/user/MS4wLjABAAAAVsneOf144eGDFf8Xp9QNb1VW6ovXnNT5SqJBhJfe8KQBKWKDTWK5Hh-_i9mJzb8C",
        "长按复制此条消息，打开抖音搜索，查看TA的更多作品。 https://v.douyin.com/idFqvUms/",
        "https://v.douyin.com/idFqvUms/",
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)

    # 对于单个URL
    single_result = await SecUserIdFetcher.get_sec_user_id(urls[0])
    assert single_result, "Failed to fetch sec_user_id for single URL"

    # 对于URL列表
    all_results = await SecUserIdFetcher.get_all_sec_user_id(urls)
    assert all_results and len(all_results) == len(
        urls
    ), "Failed to fetch sec_user_id for all URLs"

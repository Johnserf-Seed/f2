import pytest
from f2.apps.douyin.utils import SecUserIdFetcher
from f2.utils.utils import extract_valid_urls


@pytest.mark.asyncio
async def test_sec_user_id_fetcher():
    """测试 SecUserIdFetcher 工具"""
    raw_urls = [
        "https://www.douyin.com/user/MS4wLjABAAAAVsneOf144eGDFf8Xp9QNb1VW6ovXnNT5SqJBhJfe8KQBKWKDTWK5Hh-_i9mJzb8C?vid=7285950278132616463",
        "https://www.douyin.com/user/MS4wLjABAAAAVsneOf144eGDFf8Xp9QNb1VW6ovXnNT5SqJBhJfe8KQBKWKDTWK5Hh-_i9mJzb8C",
        "长按复制此条消息，打开抖音搜索，查看TA的更多作品。 https://v.douyin.com/idFqvUms/",
        "https://v.douyin.com/idFqvUms/",
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)
    assert urls, "URL 提取失败，未找到有效的 URL"

    # 测试单个 URL 提取 sec_user_id
    single_result = await SecUserIdFetcher.get_sec_user_id(urls[0])
    assert single_result, f"单个 URL 的 sec_user_id 提取失败: {urls[0]}"
    assert isinstance(
        single_result, str
    ), f"sec_user_id 类型错误，预期字符串，实际为: {type(single_result)}"

    # 测试多个 URL 提取 sec_user_id
    all_results = await SecUserIdFetcher.get_all_sec_user_id(urls)
    assert all_results, "批量 sec_user_id 提取失败"
    assert len(all_results) == len(
        urls
    ), f"结果数量与输入 URL 数量不匹配，预期 {len(urls)}，实际 {len(all_results)}"

    # 验证每个结果的格式和类型
    for url, result in zip(urls, all_results):
        if result:  # 检查非空结果
            assert isinstance(result, str), f"URL {url} 的 sec_user_id 类型错误"
        else:  # 对无效 URL 的处理
            assert "invalid" in url, f"URL {url} 预期无效，但返回了空值"

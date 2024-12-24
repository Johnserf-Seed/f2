import pytest
from f2.apps.tiktok.utils import SecUserIdFetcher
from f2.utils.utils import extract_valid_urls


test_urls = [
    "https://www.tiktok.com/@justinbieber",
    "https://www.tiktok.com/@justinbieber?is_from_webapp=1&sender_device=pc",
    "https://www.tiktok.com/@justinbieber?_t=8sUF3uPZ60n&_r=1",
    "https://www.tiktok.com/@justinbieber/video/7140296406429977898",
]

# 预期的 sec_user_id 结果
secuid_expected_results = [
    "MS4wLjABAAAAIDvnmw4IM9I6Jk7M0up6Fd4JC_OtGgVCwsy0vu51T9CGyxQwGLEmN_QZY1v2TYY5",
    "MS4wLjABAAAAIDvnmw4IM9I6Jk7M0up6Fd4JC_OtGgVCwsy0vu51T9CGyxQwGLEmN_QZY1v2TYY5",
    "MS4wLjABAAAAIDvnmw4IM9I6Jk7M0up6Fd4JC_OtGgVCwsy0vu51T9CGyxQwGLEmN_QZY1v2TYY5",
    "MS4wLjABAAAAIDvnmw4IM9I6Jk7M0up6Fd4JC_OtGgVCwsy0vu51T9CGyxQwGLEmN_QZY1v2TYY5",
]

# 预期的 unique_id 结果
unique_id_expected_results = [
    "justinbieber",
    "justinbieber",
    "justinbieber",
    "justinbieber",
]


@pytest.mark.asyncio
async def test_get_sec_user_id():
    """测试单个 URL 的 sec_user_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 遍历测试每个 URL
    for url, expected_id in zip(urls, secuid_expected_results):
        result = await SecUserIdFetcher.get_secuid(url)
        assert (
            result == expected_id
        ), f"URL: {url} -> 预期: {expected_id}, 实际: {result}"


@pytest.mark.asyncio
async def test_get_all_sec_user_id():
    """测试批量 URL 的 sec_user_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 测试批量提取的结果
    results = await SecUserIdFetcher.get_all_secuid(urls)
    assert (
        results == secuid_expected_results
    ), f"预期: {secuid_expected_results}, 实际: {results}"


@pytest.mark.asyncio
async def test_get_unique_id():
    """测试单个 URL 的 unique_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 遍历测试每个 URL
    for url, expected_id in zip(urls, unique_id_expected_results):
        result = await SecUserIdFetcher.get_uniqueid(url)
        assert (
            result == expected_id
        ), f"URL: {url} -> 预期: {expected_id}, 实际: {result}"


@pytest.mark.asyncio
async def test_get_all_unique_id():
    """测试批量 URL 的 unique_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 测试批量提取的结果
    results = await SecUserIdFetcher.get_all_uniqueid(urls)
    assert (
        results == unique_id_expected_results
    ), f"预期: {unique_id_expected_results}, 实际: {results}"

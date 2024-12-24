import pytest
from f2.apps.douyin.utils import WebCastIdFetcher
from f2.utils.utils import extract_valid_urls

test_urls = [
    "https://live.douyin.com/775841227732",
    "https://live.douyin.com/775841227732?room_id=7318296342189919011&enter_from_merge=web_share_link&enter_method=web_share_link&previous_page=app_code_link",
    'https://webcast.amemv.com/douyin/webcast/reflow/7318296342189919011?u_code=l1j9bkbd&did=MS4wLjABAAAAEs86TBQPNwAo-RGrcxWyCdwKhI66AK3Pqf3ieo6HaxI&iid=MS4wLjABAAAA0ptpM-zzoliLEeyvWOCUt-_dQza4uSjlIvbtIazXnCY&with_sec_did=1&use_link_command=1&ecom_share_track_params=&extra_params={"from_request_id":"20231230162057EC005772A8EAA0199906","im_channel_invite_id":"0"}&user_id=3644207898042206&liveId=7318296342189919011&from=share&style=share&enter_method=click_share&roomId=7318296342189919011&activity_info={}',
    "6i- Q@x.Sl 03/23 【醒子8ke的直播间】  点击打开👉https://v.douyin.com/i8tBR7hX/  或长按复制此条消息，打开抖音，看TA直播",
    "https://v.douyin.com/i8tBR7hX/",
]

expected_results = [
    "775841227732",
    "775841227732",
    "7318296342189919011",
    "7318296342189919011",
    "7318296342189919011",
]


# 通过 Pytest 提供的 pytest.mark.asyncio 装饰器标记异步测试
@pytest.mark.asyncio
async def test_get_webcast_id():
    """测试单个 URL 的 webcast_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 遍历测试每个 URL
    for url, expected_id in zip(urls, expected_results):

        result = await WebCastIdFetcher.get_webcast_id(url)
        assert (
            result == expected_id
        ), f"URL: {url} -> 预期: {expected_id}, 实际: {result}"


@pytest.mark.asyncio
async def test_get_all_webcast_id():
    """测试批量 URL 的 webcast_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 测试批量提取的结果
    result = await WebCastIdFetcher.get_all_webcast_id(urls)
    assert result == expected_results, f"预期: {expected_results}, 实际: {result}"

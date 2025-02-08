import pytest

from unittest.mock import AsyncMock, patch

from f2.apps.douyin.handler import DouyinHandler
from f2.apps.douyin.utils import WebCastIdFetcher
from f2.utils.conf_manager import TestConfigManager
from f2.utils.utils import extract_valid_urls


test_urls = [
    'https://webcast.amemv.com/douyin/webcast/reflow/7318296342189919011?u_code=l1j9bkbd&did=MS4wLjABAAAAEs86TBQPNwAo-RGrcxWyCdwKhI66AK3Pqf3ieo6HaxI&iid=MS4wLjABAAAA0ptpM-zzoliLEeyvWOCUt-_dQza4uSjlIvbtIazXnCY&with_sec_did=1&use_link_command=1&ecom_share_track_params=&extra_params={"from_request_id":"20231230162057EC005772A8EAA0199906","im_channel_invite_id":"0"}&user_id=3644207898042206&liveId=7318296342189919011&from=share&style=share&enter_method=click_share&roomId=7318296342189919011&activity_info={}',
    "6i- Q@x.Sl 03/23 【醒子8ke的直播间】  点击打开👉https://v.douyin.com/i8tBR7hX/  或长按复制此条消息，打开抖音，看TA直播",
    "https://v.douyin.com/i8tBR7hX/",
]

expected_results = [
    "7318296342189919011",
    "7318296342189919011",
    "7318296342189919011",
]


@pytest.fixture
def cookie_fixture():
    return TestConfigManager.get_test_config("douyin")


@pytest.mark.asyncio
async def test_fetch_user_live_videos_by_room_id(cookie_fixture):
    mock_room_id = "7318296342189919011"
    mock_response = AsyncMock()
    mock_response.room_id = mock_room_id

    with patch.object(
        DouyinHandler, "fetch_user_live_videos_by_room_id", return_value=mock_response
    ):
        result = await DouyinHandler(cookie_fixture).fetch_user_live_videos_by_room_id(
            mock_room_id
        )
        assert str(result.room_id) == mock_room_id


@pytest.mark.asyncio
async def test_get_room_id():
    """测试单个 URL 的 room_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 遍历测试每个 URL
    for url, expected_id in zip(urls, expected_results):

        result = await WebCastIdFetcher.get_room_id(url)
        assert (
            result == expected_id
        ), f"URL: {url} -> 预期: {expected_id}, 实际: {result}"


@pytest.mark.asyncio
async def test_get_all_room_id():
    """测试批量 URL 的 room_id 提取功能"""

    # 提取有效URL
    urls = extract_valid_urls(test_urls)

    # 测试批量提取的结果
    result = await WebCastIdFetcher.get_all_room_id(urls)
    assert result == expected_results, f"预期: {expected_results}, 实际: {result}"

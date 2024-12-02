import pytest
from f2.apps.douyin.handler import DouyinHandler
from f2.utils.conf_manager import TestConfigManager


@pytest.fixture
def cookie_fixture():
    return TestConfigManager.get_test_config("douyin")


@pytest.mark.asyncio
async def test_fetch_user_post_videos(cookie_fixture):
    async for aweme_data_list in DouyinHandler(cookie_fixture).fetch_user_post_videos(
        sec_user_id="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE",
        min_cursor=0,
        max_cursor=0,
        page_counts=1,
        max_counts=1,
    ):
        aweme_data_list

    assert aweme_data_list, f"Failed to fetch videos for user_sec_id: {aweme_data_list}"

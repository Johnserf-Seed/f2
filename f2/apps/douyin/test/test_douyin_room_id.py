import pytest
from f2.apps.douyin.handler import DouyinHandler
from f2.utils.conf_manager import TestConfigManager


@pytest.fixture
def cookie_fixture():
    return TestConfigManager.get_test_config("douyin")


@pytest.mark.asyncio
async def test_fetch_user_live_videos_by_room_id(cookie_fixture):
    result = await DouyinHandler(cookie_fixture).fetch_user_live_videos_by_room_id(
        "7318296342189919011"
    )

    assert "7318296342189919011" == str(result.room_id)

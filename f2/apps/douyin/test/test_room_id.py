import pytest
from f2.apps.douyin.handler import DouyinHandler
from f2.log.logger import logger

logger.setLevel("DEBUG")

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "cookie": "YOUR_COOKIE_HERE",
}


@pytest.mark.asyncio
async def test_fetch_user_live_videos_by_room_id():
    result = await DouyinHandler(kwargs).fetch_user_live_videos_by_room_id(
        "7318296342189919011"
    )

    assert isinstance(result, dict)
    assert "room_id" in result

import pytest
from f2.apps.douyin.handler import DouyinHandler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "cookie": "YOUR_COOKIE_HERE",
}
user_sec_id = "MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"


@pytest.mark.asyncio
async def test_fetch_user_post_videos():
    results = [
        aweme_data_list
        async for aweme_data_list in DouyinHandler(kwargs).fetch_user_post_videos(
            user_sec_id
        )
    ]

    assert results, f"Failed to fetch videos for user_sec_id: {user_sec_id}"

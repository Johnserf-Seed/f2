import pytest
from f2.apps.douyin.handler import fetch_user_post_videos


@pytest.mark.asyncio
async def test_fetch_user_post_videos():
    user_sec_id = "MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
    results = [
        aweme_data_list async for aweme_data_list in fetch_user_post_videos(user_sec_id)
    ]

    assert results, f"Failed to fetch videos for user with sec_id: {user_sec_id}"

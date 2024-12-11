import pytest
from f2.apps.weibo.handler import WeiboHandler
from f2.utils.conf_manager import TestConfigManager


@pytest.fixture
def kwargs_fixture():
    return TestConfigManager.get_test_config("weibo")


@pytest.mark.asyncio
async def test_fetch_user_info(kwargs_fixture):
    handler = WeiboHandler(kwargs_fixture)
    user_info = await handler.fetch_user_info(uid="2265830070")
    assert user_info is not None
    assert user_info.uid == "2265830070"


@pytest.mark.asyncio
async def test_fetch_user_detail(kwargs_fixture):
    handler = WeiboHandler(kwargs_fixture)
    user_detail = await handler.fetch_user_detail(uid="2265830070")

    assert user_detail is not None


@pytest.mark.asyncio
async def test_handle_one_weibo(kwargs_fixture):
    handler = WeiboHandler(kwargs_fixture)
    weibo = await handler.fetch_one_weibo(weibo_id="LvFY288c0")
    assert weibo is not None
    assert weibo.weibo_id == "4775494941938120"
    assert weibo.weibo_blog_id == "LvFY288c0"

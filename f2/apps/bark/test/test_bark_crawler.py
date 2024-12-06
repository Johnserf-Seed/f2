import pytest
from unittest.mock import AsyncMock, patch
from f2.apps.bark.filter import BarkNotificationFilter
from f2.apps.bark.model import BarkModel
from f2.utils.conf_manager import TestConfigManager


@pytest.fixture
def bark_fixture():
    """加载 Bark 配置"""
    return TestConfigManager.get_test_config("bark")


@pytest.mark.asyncio
@patch("f2.apps.bark.crawler.BarkCrawler.fetch_bark_notification")
async def test_send_notification_success(mock_fetch_bark_notification, bark_fixture):
    """测试 Bark 消息发送功能"""
    # 代理模拟响应
    mock_response = {
        "code": 200,
        "timestamp": "1733503095",
        "message": "Message sent successfully",
        "success": True,
    }

    # 确保配置加载成功
    assert bark_fixture is not None, "配置加载失败"

    # 模拟客户端
    mock_client = AsyncMock()
    mock_client.fetch_bark_notification = AsyncMock(return_value=mock_response)
    mock_fetch_bark_notification.return_value = mock_client

    # 定义测试参数
    test_params = {
        "title": "Test",
        "body": "This is a test message",
    }

    # 模拟发送消息
    bark = BarkNotificationFilter(
        await mock_client.fetch_bark_notification(BarkModel(**test_params))
    )

    # 断言：确保消息发送的响应正确
    assert bark is not None, "未收到任何响应"
    assert bark.code == 200, f"请求失败，状态码: {bark.code}"
    assert bark.message == "Message sent successfully", "消息发送失败"
    assert bark.timestamp == "2024-12-07 00-38-15", "无法收到正确的时间戳"


@pytest.mark.asyncio
@patch("f2.apps.bark.crawler.BarkCrawler.fetch_bark_notification")
async def test_send_notification_error(mock_fetch_bark_notification, bark_fixture):
    """测试 Bark 消息发送失败"""
    # 代理模拟响应
    mock_response = {
        "code": 400,
        "timestamp": "1733503095",
        "message": "Message sent failed",
        "success": False,
    }

    # 确保配置加载成功
    assert bark_fixture is not None, "配置加载失败"

    # 模拟客户端
    mock_client = AsyncMock()
    mock_client.fetch_bark_notification = AsyncMock(return_value=mock_response)
    mock_fetch_bark_notification.return_value = mock_client

    # 定义测试参数
    test_params = {
        "title": "Test",
        "body": "This is a test message",
    }

    # 模拟发送消息
    bark = BarkNotificationFilter(
        await mock_client.fetch_bark_notification(BarkModel(**test_params))
    )

    # 断言：确保消息发送的响应正确
    assert bark is not None, "未收到任何响应"
    assert bark.code == 400, f"请求失败，状态码: {bark.code}"
    assert bark.message == "Message sent failed", "消息发送失败"
    assert bark.timestamp == "2024-12-07 00-38-15", "无法收到正确的时间戳"

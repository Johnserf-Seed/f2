import pytest
from f2.apps.tiktok.utils import DeviceIdManager


@pytest.mark.asyncio
async def test_gen_device_id():
    device = await DeviceIdManager.gen_device_id()

    deviceId = device["deviceId"]
    assert deviceId is not None
    assert len(deviceId) == 19

    tt_chain_token = device["cookie"]
    assert tt_chain_token is not None
    assert len(tt_chain_token) == 39


@pytest.mark.asyncio
async def test_gen_device_id_with_full_cookie():
    device = await DeviceIdManager.gen_device_id(full_cookie=True)

    deviceId = device["deviceId"]
    assert deviceId is not None
    assert len(deviceId) == 19

    cookie = device["cookie"]
    assert cookie is not None
    assert len(cookie) == 224


@pytest.mark.asyncio
async def test_gen_device_ids():
    devices = await DeviceIdManager.gen_device_ids(3)

    assert "deviceId" in devices
    assert "cookie" in devices

    device_ids = devices["deviceId"]
    tt_chain_tokens = devices["cookie"]

    assert len(device_ids) == 3
    assert len(tt_chain_tokens) == 3

    for deviceId in device_ids:
        assert deviceId is not None
        assert len(deviceId) == 19

    for tt_chain_token in tt_chain_tokens:
        assert tt_chain_token is not None
        assert len(tt_chain_token) == 39


@pytest.mark.asyncio
async def test_gen_device_ids_with_full_cookie():
    devices = await DeviceIdManager.gen_device_ids(3, full_cookie=True)

    assert "deviceId" in devices
    assert "cookie" in devices

    device_ids = devices["deviceId"]
    cookies = devices["cookie"]

    assert len(device_ids) == 3
    assert len(cookies) == 3

    for deviceId in device_ids:
        assert deviceId is not None
        assert len(deviceId) == 19

    for tt_chain_token in cookies:
        assert tt_chain_token is not None
        assert len(tt_chain_token) == 224

import asyncio
from f2.apps.tiktok.utils import DeviceIdManager


async def main():
    device_id = await DeviceIdManager.gen_device_id()
    print(device_id)
    device_id = await DeviceIdManager.gen_device_id(full_cookie=True)
    print(device_id)
    device_ids = await DeviceIdManager.gen_device_ids(3)
    print(device_ids)
    device_ids = await DeviceIdManager.gen_device_ids(3, full_cookie=True)
    print(device_ids)


if __name__ == "__main__":
    asyncio.run(main())

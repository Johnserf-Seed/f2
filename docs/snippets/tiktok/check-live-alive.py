import asyncio
from f2.apps.tiktok.handler import TiktokHandler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {
        "http://": None,
        "https://": None,
    },
    "timeout": 10,
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    rooms = await TiktokHandler(kwargs).fetch_check_live_alive(
        room_ids="7381444193462078214,7381457815116466949,7381456855157721863,7381439549143026438"
    )

    print("=================_to_raw================")
    print(rooms._to_raw())
    print("=================_to_dict===============")
    print(rooms._to_dict())
    print("=================_to_list===============")
    print(rooms._to_list())


if __name__ == "__main__":
    asyncio.run(main())

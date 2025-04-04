import asyncio

from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    room_id = "7489225318173608756"
    anchor_id = "2471324991107884"
    sec_user_id = (
        "MS4wLjABAAAAlGkHulXq6FJ1T-kWn-GYpJ6KQPv4QvQi4s9DWXkP24pv5qJIopA4XI3RSB-0qSfH"
    )
    rank_type = "30"
    live = await DouyinHandler(kwargs).fetch_live_user_rank(
        room_id,
        anchor_id,
        sec_user_id,
        rank_type,
    )
    print("=================_to_raw================")
    print(live._to_raw())
    # print("=================_to_dict===============")
    # print(live._to_dict())
    # print("=================_to_list===============")
    # print(live._to_list())


if __name__ == "__main__":
    asyncio.run(main())

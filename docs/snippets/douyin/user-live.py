import asyncio
from f2.apps.douyin.handler import fetch_user_live_videos


async def main():
    print(await fetch_user_live_videos(webcast_id="775841227732"))


if __name__ == "__main__":
    asyncio.run(main())

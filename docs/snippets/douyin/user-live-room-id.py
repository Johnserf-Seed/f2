import asyncio
from f2.apps.douyin.handler import fetch_user_live_videos_by_room_id

async def main():
    print(await fetch_user_live_videos_by_room_id(room_id="7318296342189919011"))

if __name__ == "__main__":
    asyncio.run(main())
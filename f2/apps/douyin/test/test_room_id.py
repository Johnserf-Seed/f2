import asyncio
from f2.apps.douyin.handler import fetch_user_live_videos_by_room_id

from f2.log.logger import logger
logger.setLevel("DEBUG")

if __name__ == "__main__":
    asyncio.run(fetch_user_live_videos_by_room_id("7318296342189919011"))

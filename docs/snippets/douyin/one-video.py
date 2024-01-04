import asyncio
from f2.apps.douyin.handler import fetch_one_video


async def main():
    print(await fetch_one_video(aweme_id="7294994585925848359"))
    print("-------------------")
    print(await fetch_one_video(aweme_id="7305827432509082913"))


if __name__ == "__main__":
    asyncio.run(main())

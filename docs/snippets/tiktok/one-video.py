import asyncio
from f2.apps.tiktok.handler import fetch_one_video

async def main():
    print(await fetch_one_video(itemId="7095819783324601605"))
    print("-------------------")
    print(await fetch_one_video(itemId="7305827432509082913"))

if __name__ == "__main__":
    asyncio.run(main())

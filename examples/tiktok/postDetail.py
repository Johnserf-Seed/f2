import asyncio
from f2.apps.tiktok.handler import fetch_one_video


async def main():
    post = await fetch_one_video(itemId="7095819783324601605")
    print(post)
    print("-------------------")
    post = await fetch_one_video(itemId="7305827432509082913")
    print(post)


if __name__ == "__main__":
    asyncio.run(main())

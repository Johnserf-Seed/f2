import asyncio
from f2.apps.tiktok.handler import handler_user_profile


async def main():
    secUid = (
        "MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"
    )
    uniqueId = "vantoan___"
    print(await handler_user_profile(secUid=secUid))
    print("-------------------")
    print(await handler_user_profile(uniqueId=uniqueId))


if __name__ == "__main__":
    asyncio.run(main())

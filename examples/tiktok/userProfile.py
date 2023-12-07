import asyncio
from f2.apps.tiktok.handler import handler_user_profile


async def main():
    user = await handler_user_profile(
        secUid="MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"
    )
    print(user)
    print("-------------------")
    user = await handler_user_profile(uniqueId="sophia.ilysm")
    print(user)


if __name__ == "__main__":
    asyncio.run(main())

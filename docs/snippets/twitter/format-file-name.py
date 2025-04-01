import asyncio

from f2.apps.twitter.handler import TwitterHandler
from f2.apps.twitter.utils import format_file_name


async def main():
    # 文件名模板
    kwargs = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "Referer": "https://www.x.com/",
        },
        "naming": "{create}_{desc}_{tweet_id}",
        "cookie": "YOUR_COOKIE_HERE",
        # "X-Csrf-Token": "",
    }
    # 单作品的数据
    tweet_data = await TwitterHandler(kwargs).fetch_one_tweet(
        tweet_id="1863009545858998512"
    )
    # 格式化后的文件名
    print(format_file_name(kwargs.get("naming"), tweet_data._to_dict()) + "_tweet")

    # 文件名模板
    kwargs = {
        # ...
        "naming": "{create}_{desc}_{tweet_id}_{location}",
        # ...
    }
    # 用户自定义字段
    custom_fields = {"location": "New York"}
    # 格式化后的自定义文件名
    print(
        format_file_name(kwargs.get("naming"), tweet_data._to_dict(), custom_fields)
        + "_tweet"
    )


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from f2.apps.tiktok.handler import TiktokHandler
from f2.apps.tiktok.utils import format_file_name

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
    "naming": "{create}_{desc}_{aweme_id}",
}


async def main():
    # 单作品的数据
    aweme_data = await TiktokHandler(kwargs).fetch_one_video("7316948869764484384")
    # 格式化后的文件名
    print(format_file_name(kwargs.get("naming"), aweme_data._to_dict()) + "_video")

    # 用户自定义字段
    custom_fields = {"location": "New York"}
    # 格式化后的自定义文件名
    print((kwargs.get("naming"), aweme_data._to_dict(), custom_fields) + "_video")
    # 格式化后的自定义文件名，长度限制在100
    print(
        format_file_name(
            kwargs.get("naming"), aweme_data._to_dict(), custom_fields, 100
        )
        + "_video"
    )


if __name__ == "__main__":
    asyncio.run(main())

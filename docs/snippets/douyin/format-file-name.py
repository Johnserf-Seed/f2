import asyncio
from f2.apps.douyin.handler import DouyinHandler
from f2.apps.douyin.utils import format_file_name


async def main():
    # 文件名模板
    kwargs = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Referer": "https://www.douyin.com/",
        },
        "naming": "{create}_{desc}_{aweme_id}",
        "cookie": "YOUR_COOKIE_HERE",
    }
    # 单作品的数据
    aweme_data = await DouyinHandler(kwargs).fetch_one_video("7218193198328433954")
    # 格式化后的文件名
    print(format_file_name(kwargs.get("naming"), aweme_data._to_dict()) + "_video")

    # 文件名模板
    kwargs = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Referer": "https://www.douyin.com/",
        },
        "proxies": {"http": None, "https": None},
        "naming": "{create}_{desc}_{aweme_id}_{location}",
        "cookie": "",
    }
    # 用户自定义字段
    custom_fields = {"location": "New York"}
    # 格式化后的自定义文件名
    print(
        format_file_name(kwargs.get("naming"), aweme_data._to_dict(), custom_fields)
        + "_video"
    )
    # 格式化后的自定义文件名，长度限制在100
    print(
        format_file_name(
            kwargs.get("naming"), aweme_data._to_dict(), custom_fields, 100
        )
        + "_video"
    )


if __name__ == "__main__":
    asyncio.run(main())

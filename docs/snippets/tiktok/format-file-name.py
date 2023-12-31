import asyncio
from f2.apps.tiktok.handler tiktok fetch_one_video
from f2.apps.tiktok.utils tiktok format_file_name

async def main():
    # 文件名模板
    kwargs = {"naming": "{create}_{desc}_{aweme_id}"}
    # 单作品的数据
    aweme_data = await fetch_one_video("7316948869764484384")
    # 格式化后的文件名
    print(format_file_name(kwargs.get("naming"), aweme_data) + "_video")
 
    # 用户自定义字段
    custom_fields = {"location": "New York"}
    # 格式化后的自定义文件名
    print((kwargs.get("naming"), aweme_data, custom_fields) + "_video")
    # 格式化后的自定义文件名，长度限制在100
    print(format_file_name(kwargs.get("naming"), aweme_data, custom_fields, 100) + "_video")

if __name__ == "__main__":
    asyncio.run(main())

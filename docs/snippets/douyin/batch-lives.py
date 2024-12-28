import asyncio
import traceback

from f2.apps.douyin.handler import DouyinHandler
from f2.apps.douyin.db import AsyncUserDB
from f2.apps.douyin.dl import DouyinDownloader
from f2.utils.conf_manager import ConfigManager
from f2.cli.cli_console import RichConsoleManager
from f2.log.logger import logger

# 全局配置参数，保护敏感信息
kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    # 指定模式
    "mode": "live",
} | ConfigManager("conf/app.yaml").get_config("douyin")

# 实例化下载器和处理器
dydownloader = DouyinDownloader(kwargs)
dyhandler = DouyinHandler(kwargs)

# 批量采集的直播间ID，如果需要填写房间ID则使用fetch_user_live_videos_by_room_id方法
webcast_ids = [
    "10359270066",  # 清崽
    "205048140143",  # 偷星九月天
    "13819501559",  # QQ清
    "422057730070",  # 丫丫br
]


async def download_live_stream(
    webcast_id: str,
):
    """
    下载单个直播间的直播流，直到流断开

    Args:
        webcast_id (str): 直播间ID
    """
    try:
        live = await dyhandler.fetch_user_live_videos(webcast_id=webcast_id)

        if not live:
            logger.info(f"[bold yellow]无法获取直播间信息:[/bold yellow] {webcast_id}")
            return

        if live.live_status != 2:
            # 直播间未开播，跳过下载
            logger.info(
                f"[bold cyan]直播间ID：{webcast_id} 当前未开播，跳过...[/bold cyan]"
            )
            return

        async with AsyncUserDB("douyin_users.db") as audb:
            user_path = await dyhandler.get_or_add_user_data(
                kwargs, live.sec_user_id, audb
            )

        logger.debug(
            f"[bold green]开始下载直播间ID：{webcast_id} 的直播流...[/bold green]"
        )
        await dydownloader.create_stream_tasks(kwargs, live._to_dict(), user_path)
        logger.info(
            f"[bold green]直播间ID：{webcast_id} 直播流已结束，下载完成。[/bold green]"
        )

    except Exception as e:
        logger.error(f"[bold red]直播间ID：{webcast_id} 下载失败: {e}[/bold red]")


async def main():
    """
    主函数，批量启动直播下载任务
    """
    logger.info("[bold blue]开始批量下载多个直播间的直播流[/bold blue]")

    semaphore = asyncio.Semaphore(kwargs.get("max_tasks", 5))

    async def limited_download(webcast_id):
        async with semaphore:
            await download_live_stream(webcast_id)

    # 使用RichConsoleManager管理进度条
    with RichConsoleManager().progress:
        tasks = [limited_download(webcast_id) for webcast_id in webcast_ids]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[bold yellow]程序已手动停止[/bold yellow]")
    except Exception as e:
        logger.error(f"[bold red]程序运行时出现异常: {e}[/bold red]")
        logger.error(traceback.format_exc())

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
    "mode": "post",
} | ConfigManager("conf/app.yaml").get_config("douyin")

# 实例化下载器和处理器
dydownloader = DouyinDownloader(kwargs)
dyhandler = DouyinHandler(kwargs)

# 批量采集的用户ID
sec_user_ids = [
    "MS4wLjABAAAAMn__d0rqdcuqb1lVJKapsl-ssFNQnayKwd136gpbScI",  # 呆瓜小匪🍉
    "MS4wLjABAAAABsG6uyCohhTUpE4DmmD-c2EsdLeFIvJic8yxbXEze9g",  # 攒钱隆地雷
    "MS4wLjABAAAA070w5X9l5I82jsuGY6ntBMGlOYp8yzp4-rH8X1qCEPw",  # 小贝
    "MS4wLjABAAAAXAw5z6oNfNF1VCjmYRz1nwicQ0lLoTcOPuALhpPLKK8",  # 林语惊
    "MS4wLjABAAAAfQnGjmLfe2oJazbA_nO9EpA9zpieuegM5wxVMqXF6SE",  # 朱之琳
    "MS4wLjABAAAAPLFrUMv2S-AFNXRP2JMzvmS9_Ow39fVweFGKNxXHPys",  # 深海蜜柚
    "MS4wLjABAAAAOQ9BYHDT-BJr2yHwwNNvdNszXteeSzjuH5nifQOFvglpxMY3nP_qrzsIsXtEymCu",  # 聪明羊羊
    "MS4wLjABAAAAWaeKn3y5ZGRXElUi0iP0VcIbDH8WeZ5RmPeA9FnBZG-DYx5VTRIt-x7fXUsirIHf",  # 热锅铲女
    "MS4wLjABAAAAaa8Lsk2sIhdvQBXbnn_HT2FDGATjE0vHEDF5QjKsgYl5A30WE5ZDsMRemAObStYR",  # 蓝羊羊不懒
    "MS4wLjABAAAAEg6xF6p_5K4zBdvR0LgjMXYmY6XoOR0kIWr-EiV51Mv3ui8_d1JJhdHwSScBNO2J",  # bb猪
    "MS4wLjABAAAAejNXYKfKBp_9q4Hy9SHS1BndE_Jw50LbVs7zolIiVaFqzpl1EOunD4FApGocolKP",  # 闪光波克尔
    "MS4wLjABAAAA3CrLwX6x5aHKOdnRrEwRssgnFnmQRGf6CX3RWXc9HYEjysZ2vcy7Px0MngbLBLfc",  # 糖心蛋
    "MS4wLjABAAAAogz57t45g20LdsrkxEfvcoR7c701ow9FE7rBbFbYxUZETSzJBdgK__vIWmTHRLL4",  # 金铁兽
    "MS4wLjABAAAAj8_YMsUZglM9qYJXuZwrbT3gEpQqiW7aF6d4jpdFE1xGyDind6FkrRoUd2OjkOkF",  # 谁吃了我的火龙果
]


async def download_post(sec_user_id: str):
    """
    下载单个用户的所有作品

    Args:
        sec_user_id (str): 用户ID
    """

    try:
        logger.debug(
            f"[bold green]开始下载用户ID：{sec_user_id} 的作品...[/bold green]"
        )
        async for aweme_list in dyhandler.fetch_user_post_videos(
            sec_user_id=sec_user_id
        ):
            if not aweme_list:
                logger.info(
                    f"[bold yellow]无法获取用户作品信息:[/bold yellow] {sec_user_id}"
                )
                return

        async with AsyncUserDB("douyin_users.db", **kwargs) as audb:
            user_path = await dyhandler.get_or_add_user_data(kwargs, sec_user_id, audb)

        await dydownloader.create_download_tasks(
            kwargs, aweme_list._to_list(), user_path
        )

        logger.info(f"[bold green]用户ID：{sec_user_id} 作品下载完成。[/bold green]")
    except Exception as e:
        logger.error(f"[bold red]用户ID：{sec_user_id} 下载失败：{e}[/bold red]")


async def main():
    """
    主函数，批量启动作品下载任务
    """
    logger.info("[bold blue]开始批量下载多个用户的作品[/bold blue]")

    semaphore = asyncio.Semaphore(kwargs.get("max_tasks", 5))

    async def limited_download(sec_user_id):
        async with semaphore:
            # await download_post(sec_user_id) # [!code --]
            # 每小时检查一次作品更新状态 # [!code ++]
            while True:  # [!code ++]
                await download_post(sec_user_id)  # [!code ++]
                await asyncio.sleep(1 * 60 * 60)  # [!code ++]

    # 使用RichConsoleManager管理进度条
    with RichConsoleManager().progress:
        tasks = [
            asyncio.create_task(limited_download(sec_user_id))
            for sec_user_id in sec_user_ids
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[bold yellow]程序已手动停止[/bold yellow]")
    except Exception as e:
        logger.error(f"[bold red]程序运行时出现异常: {e}[/bold red]")
        logger.error(traceback.format_exc())

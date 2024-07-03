# path: f2/cli/cli_command.py

import f2
import click
import typing
import asyncio
import importlib
import traceback

from f2 import helps
from f2.apps import __apps__ as apps_module
from f2.exceptions import APIError
from f2.cli.cli_console import RichConsoleManager
from f2.utils._signal import SignalManager
from f2.utils.utils import get_latest_version
from f2.i18n.translator import _
from f2.log.logger import logger

from concurrent.futures import ThreadPoolExecutor

from rich.panel import Panel
from rich.console import Console


# 处理帮助信息
def handle_help(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    if not value or ctx.resilient_parsing:
        return
    helps.main()
    ctx.exit()


# 处理版本号
def handle_version(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    if not value or ctx.resilient_parsing:
        return

    click.echo(f"Version {f2.__version__}")
    ctx.exit()


# 处理debug
def handle_debug(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    if not value or ctx.resilient_parsing:
        return

    from rich.traceback import install

    install()

    logger.setLevel(value)
    logger.debug(_("调试模式：{0}").format(value))


# 版本检测
def handle_last_version(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    if not value or ctx.resilient_parsing:
        return

    asyncio.run(check_version())

    ctx.exit()


async def check_version():
    """用于检查F2的版本是否最新"""

    latest_version = await get_latest_version("f2")

    if latest_version:
        if f2.__version__ > latest_version:
            message = (
                f"您当前使用的版本 {f2.__version__} 可能已过时，请考虑及时升级到最新版本 {latest_version}，"
                "使用 pip install -U f2 更新"
            )
            Console().print(
                Panel(
                    message,
                    title="版本警告",
                    subtitle="请及时更新",
                    style="bold red",
                    border_style="red",
                )
            )
        elif f2.__version__ == latest_version:
            message = f"您当前使用的是最新版本：{f2.__version__}"
            Console().print(
                Panel(
                    message, title="版本检查", style="bold green", border_style="green"
                )
            )
    else:
        message = "无法获取最新版本信息"
        Console().print(
            Panel(
                message, title=_("网络超时"), style="bold yellow", border_style="yellow"
            )
        )


def run_async_in_thread(coro):
    """在单独的线程中运行异步任务"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()


# 应用映射
APP_MAPPINGS = {}
for attr in dir(apps_module):
    if attr.startswith("_") and not attr.startswith("__"):
        app_data = getattr(apps_module, attr)
        APP_MAPPINGS[app_data[0]] = app_data[1]

REVERSE_APP_MAPPINGS = {v: k for k, v in APP_MAPPINGS.items()}


class DynamicGroup(click.Group):
    def get_command(self, ctx: click.Context, cmd_name: str):
        app_name = (
            cmd_name
            if cmd_name in APP_MAPPINGS
            else REVERSE_APP_MAPPINGS.get(cmd_name, None)
        )
        if not app_name:
            ctx.fail(_("没有找到 {0} 应用").format(cmd_name))
        try:
            if app_name:
                # 使用线程池执行异步任务
                executor = ThreadPoolExecutor(max_workers=1)
                executor.submit(run_async_in_thread, check_version())

                # 动态导入app的cli模块
                module = importlib.import_module(f"f2.apps.{app_name}.cli")
                logger.info(_("应用：{0}").format(app_name))
                command = getattr(module, app_name)
                return command
        except (ImportError, AttributeError):
            logger.error(traceback.format_exc())
            return


@click.command(cls=DynamicGroup)
@click.option(
    "--help",
    "-h",
    "help",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=handle_help,
)
@click.option(
    "--version",
    "-v",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=handle_version,
)
@click.option(
    "--debug",
    "-d",
    type=click.Choice(["DEBUG", "INFO", "ERROR", "WARNING"]),
    is_eager=True,
    expose_value=False,
    callback=handle_debug,
)
@click.option(
    "--check-version",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=handle_last_version,
    help=_("检查F2版本"),
)
def main(**kwargs):
    pass


@click.pass_context
def set_cli_config(ctx, **kwargs):
    """
    设置CLI的配置参数, 使其可以在后续的命令或操作中使用
    (Set the conf of the CLI so that it can be used in subsequent commands)

    Args:
    - ctx: click的上下文对象
    - **kwargs: 关键字参数，代表CLI的各种设置选项
    """

    SignalManager().register_shutdown_signal()

    with RichConsoleManager().progress:
        try:
            asyncio.run(run_app(kwargs))
        except APIError as e:
            logger.error(e)


async def run_app(kwargs):
    app_name = kwargs["app_name"]
    app_module = importlib.import_module(f"f2.apps.{app_name}.handler")
    await app_module.main(kwargs)


if __name__ == "__main__":
    main()

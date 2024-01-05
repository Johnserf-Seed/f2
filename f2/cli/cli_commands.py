# path: f2/cli/cli_command.py

import click
import typing
import asyncio
import importlib

from f2 import helps
from f2.apps import __apps__ as apps_module
from f2.utils import __version__
from f2.exceptions import APIError
from f2.cli.cli_console import RichConsoleManager
from f2.utils._signal import SignalManager
from f2.i18n.translator import _
from f2.log.logger import logger


# 处理帮助信息
def handle_help(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    if not value or ctx.resilient_parsing:
        return
    helps.f2()
    ctx.exit()


# 处理版本号
def handle_version(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    if not value or ctx.resilient_parsing:
        return
    logger.debug(f"Version {__version__._version}")
    print(f"Version {__version__._version}")
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
    logger.setLevel("DEBUG")
    logger.debug("开启调试模式 (Debug on)")


# 应用映射
APP_MAPPINGS = {}
for attr in dir(apps_module):
    if attr.startswith("_") and not attr.startswith("__"):
        app_data = getattr(apps_module, attr)
        APP_MAPPINGS[app_data[0]] = app_data[1]

REVERSE_APP_MAPPINGS = {v: k for k, v in APP_MAPPINGS.items()}


class DynamicGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        app_name = (
            cmd_name
            if cmd_name in APP_MAPPINGS
            else REVERSE_APP_MAPPINGS.get(cmd_name, None)
        )
        if not app_name:
            return None
        try:
            if app_name:
                # 动态导入app的cli模块
                module = importlib.import_module(f"f2.apps.{app_name}.cli")
                logger.info("App: %s" % app_name)
                command = getattr(module, app_name)
                return command
        except (ImportError, AttributeError) as e:
            logger.error("Error: %s" % e)
            return None


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
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=handle_debug,
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
            logger.error(e.display_error())


async def run_app(kwargs):
    app_name = kwargs["app_name"]
    app_module = importlib.import_module(f"f2.apps.{app_name}.handler")
    await app_module.main(kwargs)


if __name__ == "__main__":
    main()

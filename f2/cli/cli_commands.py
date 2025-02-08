# path: f2/cli/cli_command.py

import f2
import click
import typing
import asyncio
import importlib
import traceback

from f2 import helps
from f2.apps import __apps__ as apps_module
from f2.cli.cli_console import RichConsoleManager
from f2.utils._signal import SignalManager
from f2.utils.utils import check_f2_version, check_python_version
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger


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

    asyncio.run(check_f2_version())

    ctx.exit()


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
    """
    DynamicGroup 类继承自 click.Group，提供动态加载和执行命令的功能。

    该类主要用于根据传入的命令名称动态导入和执行与之对应的应用 CLI 模块。

    类属性:
    - 无

    类方法:
    - get_command: 重写 click.Group 的 `get_command` 方法，根据传入的命令名称 `cmd_name` 查找并导入对应应用的 CLI 模块。
        执行异步检查任务并返回相关命令。如果发生错误，返回 None。

    异常处理:
    - 如果找不到命令对应的应用或在导入过程中发生错误，则会记录错误信息并返回 None。

    使用示例:
    ```python
        # 假设应用的命令是 "douyin"
        group = DynamicGroup()
        command = group.get_command(ctx, "douyin")
        if command:
            command()  # 执行对应的命令

        # 假设符合应用映射的命令是 "dy"
        command = group.get_command(ctx, "dy")
        if command:
            command()  # 执行对应的命令
    ```
    """

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
                asyncio.run(check_f2_version())
                # 动态导入app的cli模块
                module = importlib.import_module(f"f2.apps.{app_name}.cli")
                logger.info(_("应用：{0}").format(app_name))
                command = getattr(module, app_name)
                return command
        except (ImportError, AttributeError):
            trace_logger.error(traceback.format_exc())
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
    # 注册关闭信号
    SignalManager().register_shutdown_signal()
    # 检查Python版本是否符合要求
    check_python_version()


@click.pass_context
def set_cli_config(ctx: click.Context, **kwargs):
    """
    设置CLI的配置参数, 使其可以在后续的命令或操作中使用
    (Set the conf of the CLI so that it can be used in subsequent commands)

    Args:
        ctx: click的上下文对象
        **kwargs: 关键字参数，代表CLI的各种设置选项
    """

    with RichConsoleManager().progress:
        asyncio.run(run_app(kwargs))


async def run_app(kwargs):
    app_name = kwargs["app_name"]
    app_module = importlib.import_module(f"f2.apps.{app_name}.handler")
    await app_module.main(kwargs)


if __name__ == "__main__":
    main()

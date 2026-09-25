# path: f2/cli/cli_command.py

import asyncio
import importlib
import sys
import traceback
import typing

import click

import f2
from f2 import helps
from f2.apps import __apps__ as apps_module
from f2.cli.cli_console import RichConsoleManager
from f2.cli.wizard_command import config_wizard_command
from f2.exceptions import F2Error
from f2.i18n.translator import TranslationManager, _
from f2.log.logger import log_setup, logger, trace_logger
from f2.utils.core.run_report import collect_run_report
from f2.utils.core.signal import SignalManager
from f2.utils.version import check_f2_version, check_python_version


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


# 处理语言
def handler_language(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> typing.Any:
    """用于设置语言 (For setting the language)

    Args:
        ctx: click的上下文对象 (Click's context object)
        param: 提供的参数或选项 (The provided parameter or option)
        value: 参数或选项的值 (The value of the parameter or option)
    """

    if not value or ctx.resilient_parsing:
        return
    TranslationManager.get_instance().set_language(value)
    global _
    _ = TranslationManager.get_instance().gettext
    return value


# 版本检测
def handle_last_version(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    if not value or ctx.resilient_parsing:
        return

    # 强制检查版本，忽略配置文件中的设置
    asyncio.run(check_f2_version(force_check=True))
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

# 运行结束时最多列出的下载失败文件数
MAX_FAILED_DOWNLOADS_SHOWN = 10


NO_LOG_FILE_OPTION = "--no-log-file"
# 根命令中带值的选项，预扫描参数时要跳过它们的值
_ROOT_OPTIONS_WITH_VALUE = {"-d", "--debug", "-l", "--languages"}


def file_logging_disabled(args: typing.Sequence[str]) -> bool:
    """
    检查根命令参数里是否带有 --no-log-file，只看子命令之前的部分
    (Check whether the root command arguments contain --no-log-file)

    日志要在 click 解析参数之前初始化（-d/--debug 等选项的回调需要输出日志），
    所以不能等 click 解析完再决定是否写文件，只能先预扫描一遍参数（#293）。
    """
    skip_value = False
    for arg in args:
        if skip_value:
            skip_value = False
            continue
        if arg == NO_LOG_FILE_OPTION:
            return True
        if arg in _ROOT_OPTIONS_WITH_VALUE:
            skip_value = True
        elif not arg.startswith("-"):
            # 遇到子命令名，后面的参数属于应用命令
            return False
    return False


def setup_cli_logging(log_to_file: bool = True) -> None:
    """
    配置 CLI 日志：控制台输出，并按需写入 ./logs 目录（作为库导入 f2 时不会执行）
    (Configure CLI logging: console output plus optional log files under ./logs)

    Args:
        log_to_file (bool): 是否写入日志文件；为 False 时不创建 logs 目录，也不清理旧日志
    """

    log_path = "./logs" if log_to_file else None
    log_setup(log_to_console=True, log_name="f2", log_path=log_path)
    log_setup(
        log_to_console=False,
        log_name="f2-trace",
        lazy_file_creation=True,
        log_path=log_path,
    )


def report_f2_error(error: F2Error) -> None:
    """
    报告中止运行的 F2Error (Report the F2Error that aborted the run)

    异常在构造时不记录日志，这里统一输出一次：控制台一行错误原因加帮助链接，
    完整堆栈写入 f2-trace 日志。需要在 except 块中调用。
    """

    trace_logger.error(traceback.format_exc())
    logger.error(_("运行中止：{0}").format(error))
    logger.info(_("请前往QA文档 https://f2.wiki/faq 查看相关帮助"))


class DynamicGroup(click.Group):
    """
    DynamicGroup 类继承自 click.Group，提供动态加载和执行命令的功能。

    该类主要用于根据传入的命令名称动态导入和执行与之对应的应用 CLI 模块。

    类属性:
    - 无

    类方法:
    - main: 重写 click.Group 的 `main` 方法，在解析参数前配置 CLI 日志。
    - invoke: 重写 click.Group 的 `invoke` 方法，统一报告子命令抛出的 F2Error 并以退出码 1 结束。
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加内置命令
        self.add_command(config_wizard_command)

    def list_commands(self, ctx):
        """列出所有可用命令"""
        # 获取内置命令
        builtin_commands = list(self.commands.keys())

        # 获取应用命令
        app_commands = list(APP_MAPPINGS.keys()) + list(REVERSE_APP_MAPPINGS.keys())

        return sorted(builtin_commands + app_commands)

    def main(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        # 在解析参数前配置日志，保证 -d/--debug 等选项回调中的日志可正常输出；
        # 带有 --no-log-file 时只输出到控制台
        argv = kwargs.get("args", args[0] if args else None)
        argv = sys.argv[1:] if argv is None else list(argv)
        setup_cli_logging(log_to_file=not file_logging_disabled(argv))
        return super().main(*args, **kwargs)

    def invoke(self, ctx: click.Context) -> typing.Any:
        # 应用命令在开始下载前（例如读取配置时）抛出的 F2Error 也在这里统一报告，
        # 不再打印完整堆栈；下载过程中的异常由 set_cli_config 处理
        try:
            return super().invoke(ctx)
        except F2Error as e:
            report_f2_error(e)
            ctx.exit(1)

    def get_command(self, ctx: click.Context, cmd_name: str):
        # 首先检查是否是内置命令
        if cmd_name in self.commands:
            return self.commands[cmd_name]

        # 然后检查应用命令
        app_name = (
            cmd_name
            if cmd_name in APP_MAPPINGS
            else REVERSE_APP_MAPPINGS.get(cmd_name, None)
        )
        if not app_name:
            ctx.fail(_("没有找到 {0} 应用").format(cmd_name))
        try:
            if app_name:
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
    "--languages",
    "-l",
    type=click.Choice(["zh_CN", "en_US"]),
    is_eager=True,
    expose_value=False,
    help=_("显示语言。默认为 'zh_CN'，可选：'zh_CN'、'en_US'，不支持配置文件修改"),
    callback=handler_language,
)
@click.option(
    NO_LOG_FILE_OPTION,
    is_flag=True,
    expose_value=False,
    help=_("不写入日志文件，只在控制台输出，也不会创建 logs 目录"),
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

    # 创建守护线程，使其不会阻塞主程序退出
    import threading

    t = threading.Thread(
        target=lambda: run_version_check_thread(), daemon=True  # 设置为守护线程
    )
    t.start()


# 在单独线程中运行版本检查的安全包装函数
def run_version_check_thread():
    try:
        asyncio.run(check_f2_version())
    except Exception as e:
        # 避免线程崩溃，安静地处理异常
        logger.debug(_("版本检查线程异常: {0}").format(str(e)))
        pass


@click.pass_context
def set_cli_config(ctx: click.Context, **kwargs):
    """
    设置CLI的配置参数, 使其可以在后续的命令或操作中使用
    (Set the conf of the CLI so that it can be used in subsequent commands)

    Args:
        ctx: click的上下文对象
        **kwargs: 关键字参数，代表CLI的各种设置选项
    """

    with collect_run_report() as report, RichConsoleManager().progress:
        try:
            asyncio.run(run_app(kwargs))
        except F2Error as e:
            # 业务错误：堆栈只进 trace 日志，控制台给出一行结论并返回非零退出码
            report_f2_error(e)
            ctx.exit(1)

    # 有文件最终下载失败时同样返回非零退出码，便于脚本判断结果
    if not report.ok:
        failed = report.failed_downloads
        logger.error(_("有 {0} 个文件下载失败：").format(len(failed)))
        for path in failed[:MAX_FAILED_DOWNLOADS_SHOWN]:
            logger.error(f"  {path}")
        if len(failed) > MAX_FAILED_DOWNLOADS_SHOWN:
            logger.error(
                _("以及另外 {0} 个文件").format(
                    len(failed) - MAX_FAILED_DOWNLOADS_SHOWN
                )
            )
        ctx.exit(1)


async def run_app(kwargs):
    app_name = kwargs["app_name"]
    app_module = importlib.import_module(f"f2.apps.{app_name}.handler")
    await app_module.main(kwargs)


if __name__ == "__main__":
    main()

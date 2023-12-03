# path: f2/apps/douyin/cli.py

import f2
import click
import typing
import browser_cookie3
from f2 import helps
from f2.cli.cli_commands import set_cli_config
from f2.log.logger import logger
from f2.utils.utils import split_dict_cookie
from f2.utils.conf_manager import ConfigManager
from f2.i18n.translator import TranslationManager

# 先导入默认翻译函数，随后由cli配置去修改 (The default translation is imported first and then modified by the cli)
from f2.i18n.translator import _


def handle_help(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    """
    处理帮助信息 (Handle help messages)

    根据提供的值显示帮助信息或退出上下文
    (Display help messages based on the provided value or exit the context)

    Args:
        ctx: click的上下文对象 (Click's context object).
        param: 提供的参数或选项 (The provided parameter or option).
        value: 参数或选项的值 (The value of the parameter or option).
    """

    if not value or ctx.resilient_parsing:
        return
    helps.get_help("douyin")
    ctx.exit()


def handler_auto_cookie(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    """
    用于自动从浏览器获取cookie (Used to automatically get cookies from the browser)

    Args:
        ctx: click的上下文对象 (Click's context object)
        param: 提供的参数或选项 (The provided parameter or option)
        value: 参数或选项的值 (The value of the parameter or option)
    """
    if not value or ctx.resilient_parsing:
        return

    # 如果用户明确设置了 --cookie，那么跳过自动获取过程
    # (Skip the automatic acquisition process if the user explicitly sets --cookie)
    if ctx.params.get("cookie"):
        return

    # 根据浏览器选择获取cookie (Get cookies based on browser selection)
    if value != "none":
        try:
            cookie_value = split_dict_cookie(get_cookie_from_browser(value))
            manager = ConfigManager(ctx.params.get("config", "conf/conf.yaml"))
            manager.update_config_with_args("douyin", cookie=cookie_value)
        except PermissionError:
            message = _("请关闭所有已打开的浏览器重试, 并且你有适当的权限访问浏览器 !")
            logger.error(message)
            click.echo(message)
            ctx.abort()
        except Exception as e:
            message = _("自动获取Cookie失败: {0}".format(str(e)))
            logger.error(message)
            click.echo(message)
            ctx.abort()


def get_cookie_from_browser(browser_choice):
    """
    根据用户选择的浏览器获取douyin.com的cookie。

    Args:
        browser_choice (str): 用户选择的浏览器名称

    Returns:
        str: *.douyin.com的cookie值
    """

    BROWSER_FUNCTIONS = {
        "chrome": browser_cookie3.chrome,
        "firefox": browser_cookie3.firefox,
        "edge": browser_cookie3.edge,
        "opera": browser_cookie3.opera,
    }
    cj_function = BROWSER_FUNCTIONS.get(browser_choice)
    if not cj_function:
        raise ValueError(_("不支持的浏览器选项, 输入f2 dy --help查看更多帮助!"))

    cj = cj_function(domain_name="douyin.com")

    # cookie_value = next((c.value for c in cj if c.name == 'ttwid'), None)
    cookie_value = {c.name: c.value for c in cj if c.domain.endswith("douyin.com")}

    if not cookie_value:
        raise ValueError(_("无法从{0}浏览器中获取cookie").format(browser_choice))

    return cookie_value


def handler_language(ctx, param, value):
    """用于设置语言 (For setting the language)"""

    TranslationManager.get_instance().set_language(value)
    global _
    _ = TranslationManager.get_instance().gettext
    return value


def handler_naming(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
):
    """处理命名模式 (Handle naming patterns)

    Args:
        ctx (click.Context): click的上下文对象 (Click's context object)
        param (typing.Union[click.Option, click.Parameter]): 提供的参数或选项 (The provided parameter or option)
        value (typing.Any): 参数或选项的值 (The value of the parameter or option)

    Raises:
        click.BadParameter: 如果命名模式无效 (If the naming pattern is invalid)

    Returns:
        value: 参数或选项的值 (The value of the parameter or option)
    """

    # 允许的模式和分隔符 (Allowed patterns and separators)
    ALLOWED_PATTERNS = ["{nickname}", "{create}", "{aid}", "{desc}"]
    ALLOWED_SEPARATORS = ["-", "_"]

    temp_naming = value
    invalid_patterns = []

    # 检查提供的模式是否有效 (Check if provided patterns are valid)
    for pattern in ALLOWED_PATTERNS:
        if pattern in temp_naming:
            temp_naming = temp_naming.replace(pattern, "")

    # 此时，temp_naming应只包含分隔符 (Now, temp_naming should only contain separators)
    for char in temp_naming:
        if char not in ALLOWED_SEPARATORS:
            invalid_patterns.append(char)

    # 检查连续的无效模式或分隔符 (Check for consecutive invalid patterns or separators)
    for pattern in ALLOWED_PATTERNS:
        if (
            pattern + pattern in value
        ):  # 检查像"{aid}{aid}"这样的模式 (Check for patterns like "{aid}{aid}")
            invalid_patterns.append(pattern + pattern)
        for sep in ALLOWED_SEPARATORS:
            if (
                pattern + sep + pattern in value
            ):  # 检查像"{aid}-{aid}"这样的模式 (Check for patterns like "{aid}-{aid}")
                invalid_patterns.append(pattern + sep + pattern)

    if invalid_patterns:
        raise click.BadParameter(
            _("`{0}` 中的 `{1}` 不符合命名模式".format(value, "".join(invalid_patterns)))
        )

    return value


@click.command(name="douyin", help=_("抖音无水印解析"))
@click.option(
    "--config",
    "-c",
    type=click.Path(file_okay=True, dir_okay=False, readable=True),  # exists=True
    help=_("配置文件的路径，最高优先"),
)
@click.option("--url", "-u", type=str, help=_("需要解析的URL"), default="")
@click.option("--music", "-m", type=bool, default="yes", help=_("是否保存视频原声"))
@click.option("--cover", "-v", type=bool, default="yes", help=_("是否保存视频封面"))
@click.option("--desc", "-d", type=bool, default="yes", help=_("是否保存视频文案"))
@click.option("--path", "-p", type=str, default="Download", help=_("作品保存位置"))
@click.option("--folderize", "-f", type=bool, default="yes", help=_("是否将作品保存到单独的文件夹"))
@click.option(
    "--mode",
    "-M",
    type=click.Choice(
        ["one", "post", "like", "collect", "mix", "live", "feed", "search"]
    ),
    default="post",
    required=True,
    help=_(
        "下载模式：单个作品(one), 主页作品(post), 点赞作品(like), 收藏作品(collect), 合集作品(mix), 直播(live),  推荐作品(feed), 搜索作品(search)"
    ),
)
@click.option(
    "--naming",
    "-n",
    type=str,
    # default = '{nickname}_{create}_{aid}_{desc}'
    default="{create}_{desc}",
    help=_("全局作品文件命名方式"),
    callback=handler_naming,
)
# @click.confirmation_option(prompt='是否要使用命令行的参数更新配置文件?')
@click.option(
    "--auto-cookie",
    type=click.Choice(["none", "chrome", "firefox", "edge", "opera"]),
    default="none",
    help=_("是否自动从浏览器获取cookie，以及从哪个浏览器获取"),
    callback=handler_auto_cookie,
)
@click.option("--cookie", "-k", type=str, help=_("登录后的cookie"), default="")
@click.option("--interval", "-i", type=str, default="0", help=_("根据作品发布日期区间下载作品"))
@click.option("--timeout", "-e", type=int, default=10, help=_("网络请求超时等待时间"))
@click.option("--max_retries", "-r", type=int, default=5, help=_("网络请求超时重试数"))
@click.option("--max-connections", "-x", type=int, default=5, help=_("网络请求并发连接数"))
@click.option("--max-tasks", "-t", type=int, default=10, help=_("异步的任务数"))
@click.option("--max-counts", "-o", type=int, default=0, help=_("最大作品下载数"))
@click.option("--page-counts", "-s", type=int, default=20, help=_("每页作品数"))
@click.option("--update-config", type=bool, is_flag=True, help=_("使用命令行选项更新配置文件"))
@click.option("--init-config", type=str, help=_("初始化生成配置文件"))
@click.option(
    "--languages",
    "-l",
    type=click.Choice(["zh_CN", "en_US"]),
    default="zh_CN",
    help=_("语言设置"),
    callback=handler_language,
)
@click.option(
    "-h", is_flag=True, is_eager=True, expose_value=False, callback=handle_help
)
@click.pass_context
def douyin(ctx, config, init_config, update_config, **kwargs):
    # 如果用户想初始化新配置文件
    if init_config and not update_config:
        manager = ConfigManager("conf/app.yaml")
        manager.generate_config("douyin", init_config)
        return
    elif not init_config and not update_config:
        pass
    else:
        raise click.UsageError(_("不能同时初始化和更新配置文件"))

    # 如果用户想更新配置，但没有提供-c参数
    if update_config and not config:
        raise click.UsageError(_("要更新配置, 首先需要使用'-c'选项提供一个配置文件路径"))

    # 如果提供了自定义配置文件的路径，则加载配置
    if config:
        f2.APP_CONFIG_FILE_PATH = config
        manager = ConfigManager(config)

        # 提取特定应用的配置
        app_config = manager.get_config("douyin", {})

        # 合并配置文件的值到kwargs
        for key, value in app_config.items():
            # 在命令的参数列表中找到当前的键
            param = next((p for p in ctx.command.params if p.name == key), None)
            if param:
                default_value = param.default  # 获取默认值
                if ctx.params[key] == default_value:  # 如果命令行参数等于默认值
                    kwargs[key] = value  # 使用配置文件的值覆盖默认值

        # 如果指定了update_config，更新配置文件
        if update_config:
            manager.update_config_with_args("douyin", **kwargs)

    # 尝试从命令行参数或kwargs中获取URL
    if not kwargs.get("url"):
        handle_help(ctx, None, True)

    # 添加app_name到kwargs
    kwargs["app_name"] = "douyin"
    ctx.invoke(set_cli_config, **kwargs)

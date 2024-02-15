# path: f2/apps/douyin/cli.py

import f2
import click
import typing
import asyncio
import browser_cookie3

from pathlib import Path

from f2 import helps
from f2.cli.cli_commands import set_cli_config
from f2.log.logger import logger
from f2.utils.utils import split_dict_cookie, get_resource_path
from f2.utils.conf_manager import ConfigManager
from f2.i18n.translator import TranslationManager, _
from f2.apps.douyin.handler import handle_sso_login


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
    if ctx.params.get("cookie"):
        return

    # 根据浏览器选择获取cookie
    if value in ["chrome", "firefox", "edge", "opera"]:
        try:
            cookie_value = split_dict_cookie(get_cookie_from_browser(value))
            manager = ConfigManager(ctx.params.get("config", "conf/app.yaml"))
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


def get_cookie_from_browser(browser_choice: str):
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
        raise ValueError(_("无法从 {0} 浏览器中获取cookie").format(browser_choice))

    return cookie_value


def handler_language(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> typing.Any:
    """用于设置语言 (For setting the language)"""

    TranslationManager.get_instance().set_language(value)
    global _
    _ = TranslationManager.get_instance().gettext
    return value


def handler_naming(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> str:
    """处理命名模式 (Handle naming patterns)

    Args:
        ctx (click.Context): click的上下文对象 (Click's context object)
        param (typing.Union[click.Option, click.Parameter]): 提供的参数或选项 (The provided parameter or option)
        value (typing.Any): 参数或选项的值 (The value of the parameter or option)

    Raises:
        click.BadParameter: 如果命名模式无效 (If the naming pattern is invalid)

    Returns:
        value: 命名模式模板 (Naming pattern template)
    """
    # 避免和配置文件参数冲突
    if value is None:
        return

    # 允许的模式和分隔符
    ALLOWED_PATTERNS = ["{nickname}", "{create}", "{aid}", "{desc}"]
    ALLOWED_SEPARATORS = ["-", "_"]

    temp_naming = value
    invalid_patterns = []

    # 检查提供的模式是否有效
    for pattern in ALLOWED_PATTERNS:
        if pattern in temp_naming:
            temp_naming = temp_naming.replace(pattern, "")

    # 此时，temp_naming应只包含分隔符
    for char in temp_naming:
        if char not in ALLOWED_SEPARATORS:
            invalid_patterns.append(char)

    # 检查连续的无效模式或分隔符
    for pattern in ALLOWED_PATTERNS:
        # 检查像"{aid}{aid}"这样的模式
        if pattern + pattern in value:
            invalid_patterns.append(pattern + pattern)
        for sep in ALLOWED_SEPARATORS:
            # 检查像"{aid}-{aid}"这样的模式
            if pattern + sep + pattern in value:
                invalid_patterns.append(pattern + sep + pattern)

    if invalid_patterns:
        raise click.BadParameter(
            _(
                "`{0}` 中的 `{1}` 不符合命名模式".format(
                    value, "".join(invalid_patterns)
                )
            )
        )

    return value


def handler_sso_login(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    """处理SSO登录 (Handle SSO login)

    Args:
        ctx (click.Context): click的上下文对象 (Click's context object)
        param (typing.Union[click.Option, click.Parameter]): 提供的参数或选项 (The provided parameter or option)
        value (typing.Any): 参数或选项的值 (The value of the parameter or option)

    Raises:
        click.UsageError: 如果SSO登录失败 (If SSO login failed)

    Returns:
        更新配置文件 (Update the configuration file)
    """
    if not value or ctx.resilient_parsing:
        return

    if ctx.params.get("cookie"):
        return

    is_login, login_cookie = asyncio.run(handle_sso_login())

    if is_login:
        manager = ConfigManager(
            ctx.params.get("config", get_resource_path(f2.APP_CONFIG_FILE_PATH))
        )
        manager.update_config_with_args("douyin", cookie=login_cookie)
    else:
        raise click.UsageError(_("SSO登录失败，请重试！"))


def merge_config(main_conf, custom_conf, **kwargs):
    """
    合并配置参数，使 CLI 参数优先级高于自定义配置，自定义配置优先级高于主配置，最终生成完整配置参数字典。
    Args:
        main_conf (dict): 主配置参数字典
        custom_conf (dict): 自定义配置参数字典
        **kwargs: CLI 参数和其他额外的配置参数

    Returns:
        dict: 合并后的配置参数字典
    """
    # 合并主配置和自定义配置
    merged_conf = {}
    for key, value in main_conf.items():
        merged_conf[key] = value  # 将主配置复制到合并后的配置中
    for key, value in custom_conf.items():
        if value is not None and value != "":  # 只有值不为 None 和 空值，才进行合并
            merged_conf[key] = value  # 自定义配置参数会覆盖主配置中的同名参数

    # 合并 CLI 参数与合并后的配置，确保 CLI 参数的优先级最高
    for key, value in kwargs.items():
        if key not in merged_conf:  # 如果合并后的配置中没有这个键，则直接添加
            merged_conf[key] = value
        elif value is not None and value != "":  # 如果值不为 None 和 空值，则进行合并
            merged_conf[key] = value  # CLI 参数会覆盖自定义配置和主配置中的同名参数

    return merged_conf


@click.command(name="douyin", help=_("抖音无水印解析"))
@click.option(
    "--config",
    "-c",
    type=click.Path(file_okay=True, dir_okay=False, readable=True),  # exists=True
    help=_("配置文件的路径，最低优先"),
)
@click.option(
    "--url",
    "-u",
    type=str,
    # default="",
    help=_(
        "根据模式提供相应的链接。例如：主页、点赞、收藏作品填入主页链接，单作品填入作品链接，合辑与直播同上"
    ),
)
@click.option(
    "--music",
    "-m",
    type=bool,
    # default="yes",
    help=_("是否保存视频原声。可选：'yes'、'no'"),
)
@click.option(
    "--cover",
    "-v",
    type=bool,
    # default="yes",
    help=_("是否保存视频封面。可选：'yes'、'no'"),
)
@click.option(
    "--desc",
    "-d",
    type=bool,
    # default="yes",
    help=_("是否保存视频文案。可选：'yes'、'no'"),
)
@click.option(
    "--path",
    "-p",
    type=str,
    # default="Download",
    help=_("作品保存位置，支持绝对与相对路径。"),
)
@click.option(
    "--folderize",
    "-f",
    type=bool,
    # default="yes",
    help=_("是否将作品保存到单独的文件夹。可选：'yes'、'no'"),
)
@click.option(
    "--mode",
    "-M",
    type=click.Choice(["one", "post", "like", "collect", "mix", "live"]),
    # default="post",
    # required=True,
    help=_(
        "下载模式：单个作品(one)，主页作品(post)，点赞作品(like)，收藏作品(collect)，合辑(mix)，直播(live)"
    ),
)
@click.option(
    "--naming",
    "-n",
    type=str,
    # default="{create}_{desc}",
    help=_("全局作品文件命名方式，前往文档查看更多帮助"),
    callback=handler_naming,
)
@click.option(
    "--cookie",
    "-k",
    type=str,
    # default="",
    help=_("登录后的cookie，如果使用未登录的cookie，则无法持久稳定下载作品"),
)
@click.option(
    "--interval",
    "-i",
    type=str,
    # default="all",
    help=_("下载日期区间发布的作品，格式：2022-01-01|2023-01-01，'all' 为下载所有作品"),
)
@click.option(
    "--timeout",
    "-e",
    type=int,
    # default=10,
    help=_("网络请求超时时间。"),
)
@click.option(
    "--max_retries",
    "-r",
    type=int,
    # default=5,
    help=_("网络请求超时重试数。"),
)
@click.option(
    "--max-connections",
    "-x",
    type=int,
    # default=5,
    help=_("网络请求并发连接数。"),
)
@click.option(
    "--max-tasks",
    "-t",
    type=int,
    # default=10,
    help=_("异步的任务数。"),
)
@click.option(
    "--max-counts",
    "-o",
    type=int,
    # default=0,
    help=_("最大作品下载数。0 表示无限制"),
)
@click.option(
    "--page-counts",
    "-s",
    type=int,
    # default=20,
    help=_("从接口每页可获取作品数，不建议超过20。"),
)
@click.option(
    "--languages",
    "-l",
    type=click.Choice(["zh_CN", "en_US"]),
    default="zh_CN",
    help=_("显示语言。默认为 'zh_CN'。可选：'zh_CN'、'en_US'。不支持配置文件修改。"),
    callback=handler_language,
)
@click.option(
    "--proxies",
    "-P",
    type=str,
    nargs=2,
    help=_(
        "代理服务器，最多 2 个参数，http与https。空格区分 2 个参数 http://x.x.x.x https://x.x.x.x"
    ),
)
@click.option(
    "--update-config",
    type=bool,
    is_flag=True,
    help=_("使用命令行选项更新配置文件。需要先使用'-c'选项提供一个配置文件路径"),
)
@click.option(
    "--init-config", type=str, help=_("初始化配置文件。不能同时初始化和更新配置文件")
)
@click.option(
    "--auto-cookie",
    type=click.Choice(["none", "chrome", "firefox", "edge", "opera"]),
    # default="none",
    help=_(
        "自动从浏览器获取[yellow]cookie[/yellow]。可选项：chrome、firefox、edge、opera。使用该命令前请确保关闭所选的浏览器"
    ),
    callback=handler_auto_cookie,
)
@click.option(
    "--sso-login",
    is_flag=True,
    help=_("使用SSO扫码登录获取[yellow]cookie[/yellow]，保存低频主配置文件"),
    callback=handler_sso_login,
)
@click.option(
    "-h",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    help=_("显示富文本帮助"),
    callback=handle_help,
)
@click.pass_context
def douyin(ctx, config, init_config, update_config, **kwargs):
    ##################
    # f2 存在2个主配置文件，分别是app低频配置(app.yaml)和f2低频配置(conf.yaml)
    # app低频配置存放app相关的参数
    # f2低频配置存放计算值所需的参数

    # 其中cli参数具有最高优先，cli >= 自定义 >= 低频
    # 在f2低频配置中设置代理参数
    # 在app低频配置中设置好重试次数，超时时间，下载路径，下载线程，cookie等低频的参数
    # 在自定义配置中可以设置不同用户的高频参数，如用户主页，原声下载，封面下载，文案下载，下载模式等
    # cli参数为配置文件的热修改，可以随时修改每一个参数。
    ##################

    # 读取低频主配置文件
    main_manager = ConfigManager(f2.APP_CONFIG_FILE_PATH)
    main_conf_path = get_resource_path(f2.APP_CONFIG_FILE_PATH)
    main_conf = main_manager.get_config("douyin")

    # 读取f2低频配置文件
    f2_manager = ConfigManager(f2.F2_CONFIG_FILE_PATH)

    f2_conf = f2_manager.get_config("f2").get("douyin")
    f2_proxies = f2_conf.get("proxies")

    # 更新主配置文件中的代理参数
    main_conf["proxies"] = {
        "http": f2_proxies.get("http"),
        "https": f2_proxies.get("https"),
    }

    # 更新主配置文件中的headers参数
    kwargs.setdefault("headers", {})
    kwargs["headers"]["User-Agent"] = f2_conf["headers"].get("User-Agent", "")
    kwargs["headers"]["Referer"] = f2_conf["headers"].get("Referer", "")

    # 如果初始化配置文件，则与更新配置文件互斥
    if init_config and not update_config:
        main_manager.generate_config("douyin", init_config)
        # return
    elif init_config:
        raise click.UsageError(_("不能同时初始化和更新配置文件"))
    # 如果没有初始化配置文件，但是更新配置文件，则需要提供配置文件路径
    elif update_config and not config:
        raise click.UsageError(
            _("要更新配置, 首先需要使用'-c'选项提供一个自定义配置文件路径")
        )

    # 读取自定义配置文件
    if config:
        custom_manager = ConfigManager(config)
    else:
        custom_manager = main_manager
        config = main_conf_path

    custom_conf = custom_manager.get_config("douyin")

    if update_config:  # 如果指定了 update_config，更新配置文件
        update_manger = ConfigManager(config)
        update_manger.update_config_with_args("douyin", **kwargs)

    # 将kwargs["proxies"]中的tuple转换为dict
    if kwargs.get("proxies"):
        kwargs["proxies"] = {
            "http": kwargs["proxies"][0],
            "https": kwargs["proxies"][1],
        }

    # 从低频配置开始到高频配置再到cli参数，逐级覆盖，如果键值不存在使用父级的键值
    kwargs = merge_config(main_conf, custom_conf, **kwargs)

    logger.info(_("主配置路径： {0}".format(main_conf_path)))
    logger.info(_("自定义配置路径： {0}".format(Path.cwd() / config)))
    logger.debug(_("主配置参数：{0}".format(main_conf)))
    logger.debug(_("自定义配置参数：{0}".format(custom_conf)))
    logger.debug(_("CLI参数：{0}".format(kwargs)))

    # 尝试从命令行参数或kwargs中获取URL
    if not kwargs.get("url"):
        logger.error("缺乏URL参数，详情看命令帮助")
        handle_help(ctx, None, True)

    # 添加app_name到kwargs
    kwargs["app_name"] = "douyin"
    ctx.invoke(set_cli_config, **kwargs)

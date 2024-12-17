# path: f2/apps/bark/cli.py

import f2
import click
import typing

from pathlib import Path

from f2 import helps
from f2.cli.cli_commands import set_cli_config
from f2.log.logger import logger
from f2.utils.utils import merge_config, get_resource_path, check_proxy_avail
from f2.utils.conf_manager import ConfigManager
from f2.i18n.translator import TranslationManager, _
from f2.apps.bark.utils import ClientConfManager


def handler_help(
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
    helps.get_help("bark")
    ctx.exit()


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


def validate_key_length(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> typing.Any:
    """验证API 密钥长度 (Validate the length of the api key)

    Args:
        ctx: click的上下文对象 (Click's context object)
        param: 提供的参数或选项 (The provided parameter or option)
        value: 参数或选项的值 (The value of the parameter or option)
    """

    if value and len(value) != 22:
        raise click.BadParameter(_("API 密钥长度应该为22位"))
    return value


def validate_device_token_length(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> typing.Any:
    """验证设备密钥长度 (Validate the length of the device key)

    Args:
        ctx: click的上下文对象 (Click's context object)
        param: 提供的参数或选项 (The provided parameter or option)
        value: 参数或选项的值 (The value of the parameter or option)
    """

    if value and len(value) != 64:
        raise click.BadParameter(_("设备密钥长度应该为64位"))
    return value


def validate_proxies(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> typing.Any:
    """验证代理参数 (Validate proxy parameters)

    Args:
        ctx: click的上下文对象 (Click's context object)
        param: 提供的参数或选项 (The provided parameter or option)
        value: 参数或选项的值 (The value of the parameter or option)
    """

    if value:
        # 校验代理参数是否合法的代理参数
        if not all([value[0].startswith("http://"), value[1].startswith("http://")]):
            raise click.BadParameter(
                _(
                    "代理参数应该以'http://'和'http://'开头，在大多数情况下，https:// 应使用 http:// 方案"
                )
            )
        # 校验代理服务器是否可用
        if not check_proxy_avail(
            http_proxy=value[0],
            https_proxy=value[1],
            test_url="https://bark.day.app/",
        ):
            raise click.BadParameter(_("代理服务器不可用"))

    return value


@click.command(name="bark", help=_("Bark 是一个iOS端的通知推送工具"))
@click.option(
    "--config",
    "-c",
    type=click.Path(file_okay=True, dir_okay=False, readable=True),  # exists=True
    help=_("配置文件路径，最低优先"),
)
@click.option(
    "--key",
    "-k",
    type=str,
    help=_("Bark 的 API Key"),
    callback=validate_key_length,
)
@click.option(
    "--token",
    "-d",
    type=str,
    help=_("Bark 的 Device Token"),
    callback=validate_device_token_length,
)
@click.option(
    "--mode",
    "-M",
    type=click.Choice(f2.BARK_LIST),
    # default="get",
    # required=True,
    help=_(
        "选择发送模式，get：使用 GET 请求发送通知，post：使用 POST 请求发送通知，cipher：加密发送通知，默认为 get"
    ),
)
@click.option(
    "--title",
    "-t",
    type=str,
    help=_("推送的标题"),
)
@click.option(
    "--body",
    "-b",
    type=str,
    help=_("推送的内容"),
)
@click.option(
    "--call",
    "-cl",
    type=bool,
    # default=False,
    help=_("是否持续响铃，默认关闭"),
)
@click.option(
    "--level",
    "-l",
    type=click.Choice(["active", "timeSensitive", "passive", "critical"]),
    # default="active",
    help=_(
        "推送级别。active：默认，timeSensitive：时效性通知，passive：被动通知，critical：紧急通知"
    ),
)
@click.option(
    "--volume",
    "-v",
    type=int,
    # default=5,
    help=_("推送音量，范围 0-10"),
)
@click.option(
    "--badge",
    "-bd",
    type=int,
    # default=1,
    help=_("推送的角标数量"),
)
@click.option(
    "--autoCopy",
    "-ac",
    type=bool,
    # default=True,
    help=_("是否自动复制推送内容（iOS 14.5 及以上需手动长按复制）"),
)
@click.option(
    "--copy",
    "-cp",
    type=str,
    help=_("指定要复制的内容，若未指定则复制整个推送内容"),
)
@click.option(
    "--sound",
    "-s",
    type=str,
    # default="birdsong",
    help=_("推送铃声，可选项请查看 APP 设置"),
)
@click.option(
    "--icon",
    "-i",
    type=str,
    help=_("推送图标 URL，相同的图标 URL 仅下载一次"),
)
@click.option(
    "--group",
    "-g",
    type=str,
    # default="默认",
    help=_("推送分组，通知中心将按分组显示推送"),
)
@click.option(
    "--isArchive",
    "-a",
    type=bool,
    # default=True,
    help=_("是否保存推送，默认保存"),
)
@click.option(
    "--url",
    "-u",
    type=str,
    help=_("点击推送时跳转的 URL，支持 URL Scheme 和 Universal Link"),
)
@click.option(
    "--proxies",
    "-P",
    type=str,
    nargs=2,
    help=_(
        "代理服务器，最多 2 个参数，http://与https://。空格区分 2 个参数 http://x.x.x.x http://x.x.x.x (没有拼写错误，某些情况下，https:// 应使用 http:// 方案)"
    ),
    callback=validate_proxies,
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
    "-h",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    help=_("显示富文本帮助"),
    callback=handler_help,
)
@click.pass_context
def bark(
    ctx: click.Context,
    config: str,
    init_config: str,
    update_config: bool,
    **kwargs,
):
    ##################
    # f2 存在2个主配置文件，分别是app低频配置(app.yaml)和f2低频配置(conf.yaml)
    # app低频配置存放app相关的参数
    # f2低频配置存放计算值所需的参数

    # 其中cli参数具有最高优先，cli >= 自定义 >= 低频
    # 在f2低频配置中设置代理参数
    # 在app低频配置中设置好后端接口的url，加密参数等
    # 在自定义配置中可以设置不同用户的高频参数，如用户主页，原声下载，封面下载，文案下载，下载模式等
    # cli参数为配置文件的热修改，可以随时修改每一个参数。
    ##################

    # 读取低频主配置文件
    main_manager = ConfigManager(f2.APP_CONFIG_FILE_PATH)
    main_conf_path = get_resource_path(f2.APP_CONFIG_FILE_PATH)
    main_conf = main_manager.get_config("bark")

    # 更新主配置文件中的代理参数
    main_conf["proxies"] = ClientConfManager.proxies()
    main_conf["encryption"] = ClientConfManager.encryption()

    # 更新主配置文件中的headers参数
    kwargs.setdefault("headers", {})
    kwargs["headers"]["User-Agent"] = ClientConfManager.user_agent()
    kwargs["headers"]["Referer"] = ClientConfManager.referer()

    # 如果初始化配置文件，则与更新配置文件互斥
    if init_config and not update_config:
        main_manager.generate_config("bark", init_config)
        return
    elif init_config:
        raise click.UsageError(_("不能同时初始化和更新配置文件"))
    # 如果没有初始化配置文件，但是更新配置文件，则需要提供配置文件路径
    elif update_config and not config:
        raise click.UsageError(
            _("要更新配置，首先需要使用'-c'选项提供一个自定义配置文件路径")
        )

    # 读取自定义配置文件
    if config:
        custom_manager = ConfigManager(config)
    else:
        custom_manager = main_manager
        config = main_conf_path

    custom_conf = custom_manager.get_config("bark")

    if update_config:  # 如果指定了 update_config，更新配置文件
        update_manger = ConfigManager(config)
        update_manger.update_config_with_args("bark", **kwargs)
        return

    # 将kwargs["proxies"]中的tuple转换为dict
    if kwargs.get("proxies"):
        kwargs["proxies"] = {
            "http://": kwargs["proxies"][0],
            "https://": kwargs["proxies"][1],
        }

    # 从低频配置开始到高频配置再到cli参数，逐级覆盖，如果键值不存在使用父级的键值
    kwargs = merge_config(main_conf, custom_conf, **kwargs)

    # 从配置文件中获取 key、token，如果命令行没有传入 key、token
    key = kwargs.get("key") or main_conf.get("key")
    token = kwargs.get("token") or main_conf.get("token")

    # 验证 key 和 token 的长度（无论从命令行还是配置文件获取）
    try:
        validate_key_length(ctx, None, key)
        validate_device_token_length(ctx, None, token)
    except click.BadParameter as e:
        logger.error(str(e))
        ctx.exit(1)

    kwargs["key"] = key
    kwargs["token"] = token

    logger.debug(_("API密钥：{0}").format(kwargs.get("key")))
    logger.debug(_("设备密钥：{0}").format(kwargs.get("token")))
    logger.info(_("主配置路径：{0}").format(main_conf_path))
    logger.info(_("自定义配置路径：{0}").format(Path.cwd() / config))
    logger.debug(_("主配置参数：{0}").format(main_conf))
    logger.debug(_("自定义配置参数：{0}").format(custom_conf))
    logger.debug(_("CLI参数：{0}").format(kwargs))

    # 尝试从命令行参数或kwargs中获取body，mode
    missing_params = [param for param in ["body", "mode"] if not kwargs.get(param)]

    if missing_params:
        logger.error(
            _(
                "Bark CLI 缺乏必要参数：[cyan]{0}[/cyan]。详情请查看帮助，[yellow]f2 bark -h/--help[/yellow]"
            ).format("，".join(missing_params))
        )
        handler_help(ctx, None, True)

    # 添加app_name到kwargs
    kwargs["app_name"] = "bark"
    ctx.invoke(set_cli_config, **kwargs)

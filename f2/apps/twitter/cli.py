# path: f2/apps/twitter/cli.py

import traceback
import typing
from pathlib import Path

import click

import f2
from f2 import helps
from f2.apps.twitter.utils import ClientConfManager
from f2.cli.cli_commands import set_cli_config
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.config.conf_manager import ConfigManager
from f2.utils.config.merge import merge_config
from f2.utils.core.adapters import adapt_validation_call
from f2.utils.file.path import get_resource_path
from f2.utils.http.browser import get_cookie_from_browser
from f2.utils.http.cookie import split_dict_cookie
from f2.utils.http.proxy import check_proxy_avail
from f2.utils.string.validator import check_invalid_naming


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

    helps.get_help("twitter")
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
    # 如果用户没有提供值或者设置了 resilient_parsing 或者设置了 --cookie，那么跳过自动获取过程
    if not value or ctx.resilient_parsing or ctx.params.get("cookie"):
        return

    # 根据浏览器选择获取cookie
    try:
        cookie_value = split_dict_cookie(get_cookie_from_browser(value, "twitter.com"))

        if not cookie_value:
            raise ValueError(_("无法从 {0} 浏览器中获取cookie").format(value))

        # 如果没有提供配置文件，那么使用高频配置文件
        manager = ConfigManager(
            ctx.params.get("config", get_resource_path(f2.APP_CONFIG_FILE_PATH))
        )
        manager.update_config_with_args("twitter", cookie=cookie_value)
    except PermissionError:
        logger.error(
            _("请结束所有浏览器相关的进程，并确保你有管理员的权限访问浏览器后重试！")
        )
        ctx.abort()
    except Exception as e:
        trace_logger.error(traceback.format_exc())
        logger.error(_("自动获取Cookie失败：{0}").format(str(e)))
        ctx.abort()
    finally:
        ctx.exit(0)


def handler_naming(
    ctx: click.Context,
    param: typing.Union[click.Option, click.Parameter],
    value: typing.Any,
) -> None:
    """
    处理命名选项 (Handle naming options)

    Args:
        ctx: click的上下文对象 (Click's context object)
        param: 提供的参数或选项 (The provided parameter or option)
        value: 参数或选项的值 (The value of the parameter or option)
    """

    # 避免和配置文件参数冲突
    if not value or ctx.resilient_parsing:
        return

    # 允许的模式和分隔符
    ALLOWED_PATTERNS = ["{nickname}", "{create}", "{tweet_id}", "{desc}", "{uid}"]
    ALLOWED_SEPARATORS = ["-", "_"]

    # 检查命名是否符合命名规范
    invalid_patterns = check_invalid_naming(value, ALLOWED_PATTERNS, ALLOWED_SEPARATORS)

    if invalid_patterns:
        raise click.BadParameter(
            _("`{0}` 中的 `{1}` 不符合命名模式").format(
                value, "".join(invalid_patterns)
            )
        )

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
        # 解析代理类型和地址
        proxy_type, proxy_address = value

        # 验证代理类型是否支持
        if proxy_type not in ("http", "https", "socks4", "socks5"):
            raise click.BadParameter(
                _("代理类型不支持，请使用http、https、socks4或socks5")
            )

        # 验证代理地址格式
        if ":" not in proxy_address:
            raise click.BadParameter(_("代理地址格式错误，正确格式为: host:port"))

        # 构建代理URL
        proxy_url = f"{proxy_type}://{proxy_address}"

        # 校验代理服务器是否可用
        if not check_proxy_avail(
            proxy_url,
            test_url="https://www.x.com/",
        ):
            raise click.BadParameter(_("代理服务器不可用"))

        # 返回新的代理配置格式
        return {
            "type": proxy_type,
            f"{proxy_type}://": proxy_url,
            # 兼容旧格式
            "http": proxy_url,
            "https": proxy_url,
        }

    return value


@click.command(name="twitter", help=_("推文下载器"))
@click.option(
    "-c",
    "--config",
    type=click.Path(file_okay=True, dir_okay=False, readable=True),
    help=_("配置文件的路径，最低优先"),
)
@click.option(
    "--url",
    "-u",
    type=str,
    help=_("根据模式提供相应的链接"),
)
@click.option(
    "--path",
    "-p",
    type=str,
    help=_("作品保存位置，支持绝对与相对路径"),
)
@click.option(
    "--folderize",
    "-f",
    type=bool,
    help=_("是否将作品保存到单独的文件夹"),
)
@click.option(
    "--mode",
    "-M",
    type=click.Choice(f2.TWITTER_MODE_LIST),
    help=_(
        "下载模式：单个推文[one]、用户推文[post]、喜欢推文[like]、用户收藏[bookmark]"
    ),
)
@click.option(
    "--naming",
    "-n",
    type=str,
    help=_("全局推文文件命名方式，前往文档查看更多帮助"),
    callback=handler_naming,
)
@click.option(
    "--cookie",
    "-k",
    type=str,
    help=_("登录后的[yellow]cookie[/yellow]"),
)
@click.option(
    "--timeout",
    "-e",
    type=int,
    help=_("网络请求超时时间"),
)
@click.option(
    "--max_retries",
    "-r",
    type=int,
    help=_("网络请求超时重试数"),
)
@click.option(
    "--max-connections",
    "-x",
    type=int,
    help=_("网络请求并发连接数"),
)
@click.option(
    "--max-tasks",
    "-t",
    type=int,
    help=_("异步的任务数"),
)
@click.option(
    "--max-counts",
    "-o",
    type=int,
    help=_("最大推文下载数。0 表示无限制"),
)
@click.option(
    "--page-counts",
    "-s",
    type=int,
    help=_("从接口每页可获取推文数，不建议超过 20"),
)
@click.option(
    "--proxies",
    "-P",
    type=str,
    nargs=2,
    help=_(
        "配置代理服务器，支持最多两个参数。格式：类型 地址，例如："
        "socks5 127.0.0.1:1080"
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
    "--auto-cookie",
    type=click.Choice(f2.BROWSER_LIST),
    help=_("自动从浏览器获取cookie，使用该命令前请确保关闭所选的浏览器"),
    callback=handler_auto_cookie,
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
def twitter(
    ctx: click.Context,
    config: str,
    init_config: str,
    update_config: bool,
    **kwargs,
) -> None:
    # 读取低频主配置文件
    main_manager = ConfigManager(f2.APP_CONFIG_FILE_PATH)
    main_conf_path = get_resource_path(f2.APP_CONFIG_FILE_PATH)
    main_conf = main_manager.get_config("twitter")

    # 更新主配置文件中的代理参数
    main_conf["proxies"] = ClientConfManager.proxies()

    # 更新主配置文件中的headers参数
    kwargs.setdefault("headers", {})
    kwargs["headers"]["User-Agent"] = ClientConfManager.user_agent()
    kwargs["headers"]["Referer"] = ClientConfManager.referer()
    kwargs["headers"]["Authorization"] = ClientConfManager.authorization()
    kwargs["headers"]["X-Csrf-Token"] = ClientConfManager.x_csrf_token()

    # 如果初始化配置文件，则与更新配置文件互斥
    if init_config and not update_config:
        main_manager.generate_config("twitter", init_config)
        return
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
        config = str(main_conf_path)

    custom_conf = custom_manager.get_config("twitter")

    if update_config:  # 如果指定了 update_config，更新配置文件
        update_manger = ConfigManager(config)
        update_manger.update_config_with_args("twitter", **kwargs)
        return

    # 检查 kwargs["proxies"] 的类型
    if kwargs.get("proxies"):
        # 如果 proxies 是字典（来自 validate_proxies 回调），直接使用
        if isinstance(kwargs["proxies"], dict):
            pass
        # 如果 proxies 是元组（理论上不应该发生，但作为后备处理兼容旧版）
        elif (
            isinstance(kwargs["proxies"], (tuple, list)) and len(kwargs["proxies"]) >= 2
        ):
            proxy_url = kwargs["proxies"][1]  # 第二个元素是地址
            proxy_type = kwargs["proxies"][0]  # 第一个元素是类型
            kwargs["proxies"] = {
                "type": proxy_type,
                f"{proxy_type}://": f"{proxy_type}://{proxy_url}",
                "http": (
                    f"{proxy_type}://{proxy_url}" if proxy_type == "http" else None
                ),
                "https": (
                    f"{proxy_type}://{proxy_url}" if proxy_type == "https" else None
                ),
            }

    # 从低频配置开始到高频配置再到cli参数，逐级覆盖，如果键值不存在使用父级的键值
    kwargs = merge_config(main_conf, custom_conf, **kwargs)

    # 添加代理验证逻辑
    proxy_config = kwargs.get("proxies", {})
    if proxy_config and isinstance(proxy_config, dict):
        # 检查是否有有效的代理配置
        proxy_type = proxy_config.get("type")
        proxy_host = proxy_config.get("host")
        proxy_port = proxy_config.get("port")

        # 如果有完整的代理配置，则进行验证
        if proxy_type and proxy_host and proxy_port:
            from f2.utils.http.proxy import check_proxy_avail

            logger.debug(_("检测到代理配置，正在验证代理可用性..."))

            # 构建代理配置进行测试
            if not check_proxy_avail(proxy_config):
                logger.error(_("代理服务器不可用，请检查代理配置"))
                # 可以选择是否继续执行或退出
                # ctx.abort()  # 如果要在代理失败时退出
            else:
                logger.info(_("代理服务器验证成功"))

    logger.info(_("模式：{0}").format(kwargs.get("mode")))
    logger.info(_("主配置路径：{0}").format(main_conf_path))
    logger.info(_("自定义配置路径：{0}").format(Path.cwd() / config))
    logger.debug(_("主配置参数：{0}").format(main_conf))
    logger.debug(_("自定义配置参数：{0}").format(custom_conf))
    logger.debug(_("CLI参数：{0}").format(kwargs))

    # 尝试从命令行参数或kwargs中获取url和mode
    missing_params = [param for param in ["url", "mode"] if not kwargs.get(param)]

    if missing_params:
        logger.error(
            _(
                "Twitter CLI 缺乏必要参数：[cyan]{0}[/cyan]。详情请查看帮助，[yellow]f2 twitter -h/--help[/yellow]"
            ).format("，".join(missing_params))
        )
        adapt_validation_call(handler_help, ctx, True)

    # 添加app_name到kwargs
    kwargs["app_name"] = "twitter"
    ctx.invoke(set_cli_config, **kwargs)

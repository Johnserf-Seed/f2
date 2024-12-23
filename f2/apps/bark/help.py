# path: f2/apps/bark/help.py

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from f2.i18n.translator import _


def help() -> None:
    # 真彩
    console = Console(color_system="truecolor")
    table = Table(highlight=True, box=None, show_header=False)
    table.add_column("OPTIONS", no_wrap=True, justify="left", style="bold")
    table.add_column("Type", no_wrap=True, justify="left", style="bold")
    table.add_column("Description", no_wrap=True)

    options = [
        ("-c --config", "[dark_cyan]Path", _("配置文件的路径，[red]最低优先[/red]")),
        ("-k --key", "[dark_cyan]str", _("Bark 的 API Key")),
        ("-d --token", "[dark_cyan]str", _("Bark 的 Device Token")),
        (
            "-M --mode",
            "[dark_cyan]Choice",
            _(
                "选择发送模式，get：使用 GET 请求发送通知，post：使用 POST 请求发送通知，cipher：加密发送通知，默认为 get"
            ),
        ),
        ("-t --title", "[dark_cyan]str", _("推送的标题")),
        ("-b --body", "[dark_cyan]str", _("推送的内容")),
        ("-cl --call", "[dark_cyan]Bool", _("是否持续响铃，默认关闭")),
        (
            "-l --level",
            "[dark_cyan]Choice",
            _(
                "推送级别。active：默认，timeSensitive：时效性通知，passive：被动通知，critical：紧急通知"
            ),
        ),
        ("-v --volume", "[dark_cyan]str", _("推送音量，范围 0-10")),
        ("-bd --badge", "[dark_cyan]str", _("推送的角标数量")),
        (
            "-ac --autoCopy",
            "[dark_cyan]Bool",
            _("是否自动复制推送内容（iOS 14.5 及以上需手动长按复制）"),
        ),
        (
            "-cp --copy",
            "[dark_cyan]Bool",
            _("指定要复制的内容，若未指定则复制整个推送内容"),
        ),
        ("-s --sound", "[dark_cyan]str", _("推送铃声，可选项请查看 APP 设置")),
        ("-i --icon", "[dark_cyan]str", _("推送图标 URL，相同的图标 URL 仅下载一次")),
        ("-g --group", "[dark_cyan]str", _("推送分组，通知中心将按分组显示推送")),
        ("-a --isArchive", "[dark_cyan]Bool", _("是否保存推送，默认保存")),
        (
            "-u --url",
            "[dark_cyan]str",
            _("点击推送时跳转的 URL，支持 URL Scheme 和 Universal Link"),
        ),
        (
            "-P --proxies",
            "[dark_cyan]str",
            _(
                "代理服务器，空格区分 2 个参数 http://x.x.x.x:xxxx http://x.x.x.x:xxxx (某些情况下，https:// 应使用 http:// 方案)"
            ),
        ),
        (
            "--update-config",
            "[dark_cyan]Bool",
            _("使用命令行选项更新配置文件。需要先使用'-c'选项提供一个配置文件路径"),
        ),
        (
            "--init-config",
            "[dark_cyan]Bool",
            _("初始化配置文件。不能同时初始化和更新配置文件"),
        ),
        ("--help", "[dark_cyan]Flag", _("显示经典帮助信息")),
        ("-h", "[dark_cyan]Bool", _("显示富文本帮助")),
        (
            "",
            "",
            _(
                "更加详细的参数说明请点击[link=https://f2.wiki/site-config][dark_violet]前往文档[/dark_violet][/]查看"
            ),
        ),
    ]

    for option in options:
        table.add_row(*option)

    console.print(Panel(table, border_style="bold", title="[Bark]", title_align="left"))

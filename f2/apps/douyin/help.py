# path: f2/apps/douyin/help.py

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
        (
            "-u --url",
            "[dark_cyan]str",
            _(
                "根据模式提供相应的链接。例如：主页、点赞、收藏作品填入主页链接，单作品填入作品链接，合集与直播同上"
            ),
        ),
        ("-m --music", "[dark_cyan]Bool", _("是否保存视频原声")),
        ("-v --cover", "[dark_cyan]Bool", _("是否保存视频封面")),
        ("-d --desc", "[dark_cyan]Bool", _("是否保存视频文案")),
        ("-p --path", "[dark_cyan]str", _("作品保存位置，支持绝对与相对路径。")),
        (
            "-f --folderize",
            "[dark_cyan]Bool",
            _("是否将作品保存到单独的文件夹"),
        ),
        (
            "-M --mode",
            "[dark_cyan]Choice",
            _(
                "下载模式：单个作品(one)，主页作品(post)，点赞作品(like)，收藏作品(collection)，收藏夹作品(collects)，合集(mix)，直播(live)"
            ),
        ),
        (
            "-n --naming",
            "[dark_cyan]str",
            _("全局作品文件命名方式，前往文档查看更多帮助"),
        ),
        (
            "-k --cookie",
            "[dark_cyan]str",
            _(
                "登录后的[yellow]cookie[/yellow]，如果使用未登录的[yellow]cookie[/yellow]，则无法持久稳定下载作品"
            ),
        ),
        (
            "-i --interval",
            "[dark_cyan]str",
            _(
                "下载日期区间发布的作品，格式：YYYY-MM-DD|YYYY-MM-DD，'all' 为下载所有作品"
            ),
        ),
        ("-e --timeout", "[dark_cyan]int", _("网络请求超时时间")),
        ("-r --max-retries", "[dark_cyan]int", _("网络请求超时重试数")),
        ("-x --max-connections", "[dark_cyan]int", _("网络请求并发连接数")),
        ("-t --max-tasks", "[dark_cyan]int", _("异步的任务数")),
        ("-o --max-counts", "[dark_cyan]int", _("最大作品下载数。0 表示无限制")),
        (
            "-s --page-counts",
            "[dark_cyan]int",
            _("从接口每页可获取作品数，不建议超过 20"),
        ),
        (
            "-l --languages",
            "[dark_cyan]Choice",
            _("显示语言。默认为 'zh_CN'。可选：'zh_CN'、'en_US'"),
        ),
        (
            "-P --proxies",
            "[dark_cyan]str",
            _(
                "配置代理服务器，支持最多两个参数，分别对应 http:// 和 https:// 协议。如果代理不支持出口 HTTPS，请使用：http://x.x.x.x http://x.x.x.x"
            ),
        ),
        ("-L --lyric", "[dark_cyan]Bool", _("是否保存视频歌词")),
        (
            "--update-config",
            "[dark_cyan]Flag",
            _("使用命令行选项更新配置文件。需要先使用'-c'选项提供一个配置文件路径"),
        ),
        (
            "--init-config",
            "[dark_cyan]Flag",
            _("初始化配置文件。不能同时初始化和更新配置文件"),
        ),
        (
            "--auto-cookie",
            "[dark_cyan]Choice",
            _(
                "自动从浏览器获取[yellow]cookie[/yellow]，使用该命令前请确保关闭所选的浏览器"
            ),
        ),
        (
            "--sso-login",
            "[dark_cyan]Flag",
            _(
                "使用SSO扫码登录获取[yellow]cookie[/yellow]，保存低频主配置文件[red]（暂时弃用）[/red]"
            ),
        ),
        ("--help", "[dark_cyan]Flag", _("显示经典帮助信息")),
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

    console.print(
        Panel(table, border_style="bold", title="[DouYin]", title_align="left")
    )

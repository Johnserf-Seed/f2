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
        ("-c --config", "[dark_cyan]Path", _("配置文件的路径，[red]最高优先[/red]")),
        (
            "-u --url",
            "[dark_cyan]str",
            _("根据模式提供相应的链接。例如：主页、点赞、收藏作品填入主页链接，单作品填入作品链接，合辑与直播同上"),
        ),
        ("-m --music", "[dark_cyan]Choice", _("是否保存视频原声。默认为 'yes'，可选：'yes'、'no'")),
        ("-v --cover", "[dark_cyan]Choice", _("是否保存视频封面。默认为 'yes'，可选：'yes'、'no'")),
        ("-d --desc", "[dark_cyan]Choice", _("是否保存视频文案。默认为 'yes'，可选：'yes'、'no'")),
        ("-p --path", "[dark_cyan]str", _("作品保存位置，默认为 'Download'")),
        (
            "-f --folderize",
            "[dark_cyan]Choice",
            _("是否将作品保存到单独的文件夹，默认为 'yes'。可选：'yes'、'no'"),
        ),
        (
            "-M --mode",
            "[dark_cyan]Choice",
            _("下载模式：主页作品(post)，点赞作品(like)，收藏作品(collect)，合辑(mix)，直播(live)"),
        ),
        ("-n --naming", "[dark_cyan]str", _("全局作品文件命名方式，前往文档查看更多帮助")),
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
            _("下载日期区间发布的作品，格式：2022-01-01|2023-01-01，默认为 'all'下载所有作品"),
        ),
        ("-e --timeout", "[dark_cyan]int", _("网络请求超时时间。默认为 10")),
        ("-r --max-retries", "[dark_cyan]int", _("网络请求超时重试数。默认为 5")),
        ("-x --max-connections", "[dark_cyan]int", _("网络请求并发连接数。默认为 5")),
        ("-t --max-tasks", "[dark_cyan]int", _("异步的任务数。默认为 10")),
        ("-o --max-counts", "[dark_cyan]int", _("最大作品下载数。默认为 0，表示无限制")),
        ("-s --page-counts", "[dark_cyan]int", _("每页作品数。默认为 20")),
        ("-l --languages", "[dark_cyan]Choice", _("显示语言。默认为 'zh_CN'。可选：'zh_CN'、'en'")),
        (
            "--update-config",
            "[dark_cyan]Flag",
            _("使用命令行选项更新配置文件。需要先使用'-c'选项提供一个配置文件路径"),
        ),
        ("--init-config", "[dark_cyan]Flag", _("初始化配置文件。不能同时初始化和更新配置文件")),
        (
            "--auto-cookie",
            "[dark_cyan]Choice",
            _(
                "自动从浏览器获取[yellow]cookie[/yellow]。可选项：chrome、firefox、edge（默认）、opera。使用该命令前请确保关闭所选的浏览器"
            ),
        ),
        (
            "-",
            "[dark_cyan]-",
            _(
                "更加详细的参数说明请点击[link=https://johnserf-seed.github.io/f2/site-config.html][dark_violet]前往文档[/dark_violet][/]查看"
            ),
        ),
    ]

    for option in options:
        table.add_row(*option)

    console.print(
        Panel(table, border_style="bold", title="[DouYin]", title_align="left")
    )

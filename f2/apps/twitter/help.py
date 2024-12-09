# path: f2/apps/twitter/help.py

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
        ("-u --url", "[dark_cyan]str", _("除了单个推文外，其他URL都需要用户主页URL")),
        ("-p --path", "[dark_cyan]str", _("推文保存位置，默认为 'Download'")),
        (
            "-f --folderize",
            "[dark_cyan]Choice",
            _("是否将推文保存到单独的文件夹，默认为 'yes'"),
        ),
        (
            "-M --mode",
            "[dark_cyan]Choice",
            _(
                "下载模式：单个推文(one)、用户推文(post)、喜欢推文(like)、用户收藏(bookmark)"
            ),
        ),
        ("-n --naming", "[dark_cyan]str", _("全局推文文件命名方式")),
        (
            "--auto-cookie",
            "[dark_cyan]Choice",
            _(
                "自动从浏览器获取[yellow]cookie[/yellow]，使用该命令前请确保关闭所选的浏览器"
            ),
        ),
        ("-k --cookie", "[dark_cyan]str", _("登录后的cookie")),
        ("-e --timeout", "[dark_cyan]int", _("网络请求超时时间，默认为 10")),
        ("-r --max-retries", "[dark_cyan]int", _("网络请求超时重试数，默认为 5")),
        ("-x --max-connections", "[dark_cyan]int", _("网络请求并发连接数，默认为 5")),
        ("-t --max-tasks", "[dark_cyan]int", _("异步的任务数，默认为 10")),
        ("-o --max-counts", "[dark_cyan]int", _("最大推文下载数 默认为 0，表示无限制")),
        ("-s --page-counts", "[dark_cyan]int", _("每页推文数，默认为 20个推文/页")),
        ("-l --languages", "[dark_cyan]Choice", _("语言设置，默认为 'zh_CN'")),
        (
            "-P --proxies",
            "[dark_cyan]str",
            _(
                "配置代理服务器，支持最多两个参数，分别对应 http:// 和 https:// 协议。如果代理不支持出口 HTTPS，请使用：http://x.x.x.x http://x.x.x.x"
            ),
        ),
        ("--update-config", "[dark_cyan]Flag", _("使用命令行选项更新配置文件")),
        ("--init-config", "[dark_cyan]Flag", _("初始化配置文件")),
    ]

    for option in options:
        table.add_row(*option)

    console.print(
        Panel(table, border_style="bold", title="[Twitter]", title_align="left")
    )

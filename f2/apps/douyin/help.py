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
        ("-c --config", "[dark_cyan]Path", _("配置文件的路径，最高优先")),
        ("-u --url", "[dark_cyan]str", _("除了单个作品外，其他URL都需要用户主页URL")),
        ("-m --music", "[dark_cyan]Choice", _("是否保存视频原声，默认为 'yes'")),
        ("-v --cover", "[dark_cyan]Choice", _("是否保存视频封面，默认为 'yes'")),
        ("-d --desc", "[dark_cyan]Choice", _("是否保存视频文案，默认为 'yes'")),
        ("-p --path", "[dark_cyan]str", _("作品保存位置，默认为 'Download'")),
        ("-f --folderize", "[dark_cyan]Choice", _("是否将作品保存到单独的文件夹，默认为 'yes'")),
        (
            "-M --mode",
            "[dark_cyan]Choice",
            _(
                "下载模式：主页作品(post), 点赞作品(like), 收藏作品(collect), 合辑(mix), 直播(live), 推荐作品(feed), 搜索作品(search)"
            ),
        ),
        ("-n --naming", "[dark_cyan]str", _("全局作品文件命名方式")),
        ("--auto-cookie", "[dark_cyan]Choice", _("是否自动从浏览器获取cookie，以及从哪个浏览器获取")),
        ("-k --cookie", "[dark_cyan]str", _("登录后的cookie")),
        ("-i --interval", "[dark_cyan]str", _("根据作品发布日期区间下载作品，默认为 '0'")),
        ("-e --timeout", "[dark_cyan]int", _("网络请求超时时间，默认为 10")),
        ("-r --max-retries", "[dark_cyan]int", _("网络请求超时重试数，默认为 5")),
        ("-x --max-connections", "[dark_cyan]int", _("网络请求并发连接数，默认为 5")),
        ("-t --max-tasks", "[dark_cyan]int", _("异步的任务数，默认为 10")),
        ("-o --max-counts", "[dark_cyan]int", _("最大作品下载数 默认为 0，表示无限制")),
        ("-s --page-counts", "[dark_cyan]int", _("每页作品数，默认为 20个作品/页")),
        ("-l --languages", "[dark_cyan]Choice", _("语言设置，默认为 'zh_CN'")),
        ("--update-config", "[dark_cyan]Flag", _("使用命令行选项更新配置文件")),
        ("--init-config", "[dark_cyan]Flag", _("初始化配置文件")),
    ]

    for option in options:
        table.add_row(*option)

    console.print(
        Panel(table, border_style="bold", title="[DouYin]", title_align="left")
    )

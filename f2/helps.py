#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description:helps.py
@Date       :2023/02/06 17:36:41
@Author     :JohnserfSeed
@version    :0.0.1
@License    :Apache License 2.0
@Github     :https://github.com/johnserf-seed
@Mail       :johnserf-seed@foxmail.com
-------------------------------------------------
Change Log  :
2023/02/06 17:36:41 - create output help
-------------------------------------------------
"""

import importlib

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from f2.i18n.translator import _
from f2.utils import __version__


def get_help(app_name: str) -> None:
    try:
        module = importlib.import_module(f"f2.apps.{app_name}")
        if hasattr(module, "help"):
            module.help()
        else:
            print(_("在 {0} 应用里没有找到帮助文件").format(app_name))
    except ImportError:
        print(_("没有找到 {0} 应用").format(app_name))


def f2() -> None:
    # 真彩
    console = Console(color_system="truecolor")
    console.print(
        f"\n:rocket: [bold]f2 {__version__._version} :rocket:", justify="center"
    )
    console.print(f"\n[i]{__version__._description_cn}", justify="center")
    console.print(f"[i]{__version__._description_en}", justify="center")
    console.print(f"[i]GitHub {__version__._repourl}\n", justify="center")

    table = Table.grid(padding=1, pad_edge=True, expand=True)
    table.add_column("Website", no_wrap=True, justify="left", style="bold")
    table.add_column("Description", no_wrap=True, justify="left", style="bold")

    # 分割
    # console.rule("[b]已适配[/b]", align="center")
    # table.add_row(
    #     _("抖音"), _("  单个作品，主页作品，点赞作品，收藏作品，合辑作品，图文，原声。后续更新：推荐作品，朋友作品，好友作品，搜索作品")
    # )
    # table.add_row(
    #     _("TikTok"), _("  单个作品，主页作品，点赞作品，收藏作品，播放列表（合辑）作品，原声。后续更新：推荐作品，朋友作品，好友作品，搜索作品")
    # )
    # # 待适配
    # console.print(table)
    # 分割
    # console.rule()

    # 使用方法
    table = Table.grid(padding=1, pad_edge=True)
    table.add_column("Usage", no_wrap=True, justify="left", style="bold")
    table.add_row("[b]f2[/b] [magenta]<apps> [/magenta][cyan][MODE]")
    table.add_row(_("例： f2 dy -h 来获取douyin的下载参数帮助"))
    console.print(
        Panel(table, border_style="bold", title="使用方法 | Usage", title_align="left")
    )

    table = Table.grid(padding=1, pad_edge=True, expand=True)
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Parameter", no_wrap=True, justify="left", style="bold")
    table.add_column("Description", no_wrap=True, style="bold")
    table.add_column("Status", no_wrap=True, justify="left", style="bold")

    table.add_row(_("weibo 或 wb"), _("- 获取微博"))
    table.add_row(_("douyin 或 dy"), _("- 单个作品，主页作品，点赞作品，收藏作品，合辑作品，图文，原声。"), _("✔"))
    table.add_row(_("tiktok 或 tk"), _("- 单个作品，主页作品，点赞作品，收藏作品，播放列表（合辑）作品，原声。"), _("✔"))
    table.add_row(_("instagram 或 ig"), _("- 获取ig的作品"))
    table.add_row(_("twitch 或 tv"), _("- 获取Twitch直播"))
    table.add_row(_("twitter 或 x"), _("- 获取Twitter作品"))
    table.add_row(_("youtube 或 ytb"), _("- 获取YouTube的作品"))
    table.add_row(_("bilibili 或 bili"), _("- 获取BiliBili的作品"))
    table.add_row(_("neteasy_music 或 nem"), _("- 获取网易云音乐作品"))
    table.add_row(_("little_red_book 或 lrb"), _("- 获取小红书的作品"))
    table.add_row("\n")
    table.add_row("f2 -d <apps>", _("- 输出该app的debug信息到/logs 提交Issue时请附带该文件并删除敏感信息"))
    table.add_row(
        "Issues?", "[link=https://github.com/Johnserf-Seed/f2/issues]Click Here[/]"
    )
    console.print(
        Panel(
            table,
            border_style="bold",
            title="<apps>",
            title_align="left",
            subtitle=_("欢迎提交PR适配更多网站"),
        )
    )

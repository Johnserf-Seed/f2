# path: f2/utils/version.py

import asyncio
import sys
import traceback
from typing import Optional

import httpx
from packaging.version import InvalidVersion, Version
from rich.console import Console
from rich.panel import Panel

import f2
from f2.i18n.translator import _
from f2.log.logger import logger
from f2.utils.config.conf_manager import ConfigManager


async def get_latest_version(package_name: str) -> Optional[str]:
    """
    获取Python包的最新版本号

    Args:
        package_name (str): Python包名

    Returns:
        Optional[str]: Python包的最新版本号，获取失败时返回None
    """
    async with httpx.AsyncClient(
        timeout=5.0,
        transport=httpx.AsyncHTTPTransport(retries=5),
    ) as aclient:
        try:
            response = await aclient.get(f"{f2.PYPI_URL}/{package_name}/json")
            response.raise_for_status()
            package_data = response.json()
            latest_version = package_data["info"]["version"]
            return latest_version
        except asyncio.CancelledError:
            logger.warning(_("取消检查更新"))
            return None
        except (httpx.HTTPStatusError, httpx.RequestError, KeyError):
            logger.debug(traceback.format_exc())
            return None


def is_outdated(current: str, latest: str) -> Optional[bool]:
    """
    按 PEP 440 规则比较版本号 (Compare versions according to PEP 440)

    Args:
        current (str): 当前版本号
        latest (str): 最新版本号

    Returns:
        Optional[bool]: 当前版本落后返回 True，不落后返回 False，任一版本号无法解析返回 None
    """
    try:
        return Version(current) < Version(latest)
    except InvalidVersion:
        logger.debug(_("无法比较版本号：{0} 与 {1}").format(current, latest))
        return None


async def check_f2_version(force_check: bool = False) -> None:
    """
    检查F2的版本是否最新

    Args:
        force_check (bool): 是否强制检查，忽略配置文件中的设置
    """
    # 如果不是强制检查，则读取配置文件中的check_update设置
    if not force_check:
        config_manager = ConfigManager()
        check_update = config_manager.config.get("f2", {}).get("check_update", False)

        # 如果配置文件中设置为不显示更新，则直接返回
        if not check_update:
            return

    latest_version = await get_latest_version("f2")
    console = Console()

    if latest_version:
        outdated = is_outdated(f2.__version__, latest_version)
        if outdated:
            message = _(
                "您当前使用的版本 {0} 可能已过时，请考虑及时升级到最新版本 {1}，"
                "使用 pip install -U f2 更新"
            ).format(f2.__version__, latest_version)
            console.print(
                Panel(
                    message,
                    title=_("F2 低版本警告"),
                    subtitle=_("请及时更新"),
                    style="bold red",
                    border_style="red",
                )
            )
        elif outdated is False:
            message = _("您当前使用的是最新版本：{0}").format(f2.__version__)
            console.print(
                Panel(
                    message,
                    title=_("F2 版本检查"),
                    style="bold green",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    _("无法比较版本号：{0} 与 {1}").format(
                        f2.__version__, latest_version
                    ),
                    title=_("F2 版本检查"),
                    style="bold yellow",
                    border_style="yellow",
                )
            )
    else:
        message = _("无法获取最新版本信息")
        console.print(
            Panel(
                message,
                title=_("F2 版本检查网络超时"),
                style="bold yellow",
                border_style="yellow",
            )
        )


def check_python_version(min_version: tuple = (3, 10)) -> None:
    """
    检查当前 Python 版本是否满足最低要求

    Args:
        min_version (tuple, optional): 最低 Python 版本要求，默认为 (3, 10)

    Raises:
        SystemExit: 当 Python 版本不满足最低要求时，退出程序
    """

    console = Console()
    if sys.version_info < min_version:
        message = _("当前 Python 版本：{0} 不满足最低要求：{1}").format(
            sys.version.split()[0], ".".join(map(str, min_version))
        )
        panel = Panel(
            f"[bold red]{message}[/bold red]",
            title=_("[bold red]Python 版本错误[/bold red]"),
            border_style="red",
        )
        console.print(panel)
        sys.exit(1)

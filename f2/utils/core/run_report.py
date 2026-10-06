# path: f2/utils/core/run_report.py

import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Iterator, List, Optional, Protocol

from f2.i18n.translator import _


class Notifier(Protocol):
    """发送通知的对象，如 Bark (A notification sender such as Bark)"""

    async def send(self, title: str, body: str, **options: Any) -> Any: ...


class NullNotifier:
    """没有开启通知时使用，什么也不做 (Used when notifications are off; does nothing)"""

    async def send(self, title: str, body: str, **options: Any) -> None:
        return None


@dataclass
class Notification:
    """
    一条通知 (A notification)

    属性:
    - title (str): 标题。
    - body (str): 正文。
    - group (Optional[str]): 通知分组，如 DouYin。
    """

    title: str
    body: str
    group: Optional[str] = None


def format_duration(seconds: float) -> str:
    """把秒数写成“1 小时 2 分 3 秒”的形式 (Format seconds as hours, minutes and seconds)"""
    seconds = int(round(seconds))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return _("{0} 小时 {1} 分 {2} 秒").format(hours, minutes, seconds)
    if minutes:
        return _("{0} 分 {1} 秒").format(minutes, seconds)
    return _("{0} 秒").format(seconds)


@dataclass
class RunReport:
    """
    一次 CLI 运行的结果汇总 (Summary of a single CLI run)

    下载器把完成、跳过与最终失败的文件记在这里，各模式把通知文案记在这里；
    CLI 在运行结束后据此决定退出码，并发送一条运行结果通知。
    作为库使用时默认没有活动的汇总对象，记录操作不产生任何效果，也不会发送通知。

    属性:
    - failed_downloads (List[str]): 所有链接都下载失败的文件路径。
    - completed_downloads (int): 下载完成的文件数。
    - skipped_downloads (int): 已存在而跳过的文件数。
    - notifications (List[Notification]): 各模式记录的通知文案，运行结束时随结果一起发送。
    - notifier (Notifier): 发送通知的对象，没有开启通知时什么也不做。
    """

    failed_downloads: List[str] = field(default_factory=list)
    completed_downloads: int = 0
    skipped_downloads: int = 0
    notifications: List[Notification] = field(default_factory=list)
    notifier: Notifier = field(default_factory=NullNotifier)
    started_at: float = field(default_factory=time.monotonic)

    @property
    def ok(self) -> bool:
        """本次运行是否没有失败的下载 (Whether no download failed)"""
        return not self.failed_downloads

    def summary(self) -> str:
        """文件下载结果与用时的一行摘要 (One-line summary of downloads and duration)"""
        return _("文件：完成 {0} 个，跳过 {1} 个，失败 {2} 个；用时 {3}").format(
            self.completed_downloads,
            self.skipped_downloads,
            len(self.failed_downloads),
            format_duration(time.monotonic() - self.started_at),
        )

    def final_notification(
        self, default_title: str, error: Optional[BaseException] = None
    ) -> Optional[Notification]:
        """
        运行结束时发送的通知 (The notification sent when the run ends)

        各模式记录的文案加上下载结果摘要；中途出错时注明原因。既没有下载文件、
        也没有记录文案且没有出错时返回 None，避免如定时检查直播时每次都推送。

        Args:
            default_title (str): 没有记录文案时使用的标题
            error (BaseException): 中止运行的错误

        Returns:
            Optional[Notification]: 要发送的通知，不需要发送时为 None
        """
        has_activity = (
            self.notifications
            or self.completed_downloads
            or self.skipped_downloads
            or self.failed_downloads
        )
        if not has_activity and error is None:
            return None

        title, group = default_title, None
        parts: List[str] = []
        if self.notifications:
            title, group = self.notifications[0].title, self.notifications[0].group
            for notification in self.notifications:
                body = notification.body.strip()
                if body and body not in parts:
                    parts.append(body)
        if error is not None:
            title = _("{0}（运行中止）").format(title)
            parts.append(_("原因：{0}").format(error))
        parts.append(self.summary())
        return Notification(title, "\n\n".join(parts), group)


_current_report: ContextVar[Optional[RunReport]] = ContextVar(
    "f2_run_report", default=None
)


@contextmanager
def collect_run_report(notifier: Optional[Notifier] = None) -> Iterator[RunReport]:
    """
    在上下文内收集运行结果 (Collect run results within the context)

    上下文变量会随 asyncio.run 与其中创建的任务一起传递，
    因此下载任务里的记录都会汇总到同一个对象上。

    Args:
        notifier (Notifier): 发送通知的对象，默认不发送

    Yields:
        RunReport: 本次运行的结果汇总
    """

    report = RunReport(notifier=notifier or NullNotifier())
    token = _current_report.set(report)
    try:
        yield report
    finally:
        _current_report.reset(token)


def current_run_report() -> Optional[RunReport]:
    """返回当前活动的运行结果汇总，没有时返回 None (Return the active report or None)"""
    return _current_report.get()


def record_failed_download(path: str) -> None:
    """
    记录一个最终下载失败的文件 (Record a file whose download finally failed)

    Args:
        path (str): 文件保存路径
    """

    report = _current_report.get()
    if report is not None:
        report.failed_downloads.append(str(path))


def record_completed_download() -> None:
    """记录一个下载完成的文件 (Record a completed download)"""
    report = _current_report.get()
    if report is not None:
        report.completed_downloads += 1


def record_skipped_download() -> None:
    """记录一个已存在而跳过的文件 (Record a download skipped because it exists)"""
    report = _current_report.get()
    if report is not None:
        report.skipped_downloads += 1


def notifications_enabled() -> bool:
    """
    当前运行是否会发送通知 (Whether the current run sends notifications)

    为假时不必为通知文案额外请求数据（如点赞列表中没有的作者昵称）。
    """
    report = _current_report.get()
    return report is not None and not isinstance(report.notifier, NullNotifier)


def record_notification(title: str, body: str, group: Optional[str] = None) -> None:
    """
    记录本次运行的通知文案，运行结束时随下载结果一起发送
    (Record notification text that is sent with the results when the run ends)

    此前各模式在获取数据时就发送通知，早于下载完成；作为库调用时也会发送。

    Args:
        title (str): 标题
        body (str): 正文
        group (str): 通知分组，如 DouYin
    """
    report = _current_report.get()
    if report is not None:
        report.notifications.append(Notification(title, body, group))


async def notify_now(title: str, body: str, group: Optional[str] = None) -> None:
    """
    立即发送一条通知，如开播提醒 (Send a notification right away, e.g. a live reminder)

    没有活动的运行（作为库使用）时不发送。

    Args:
        title (str): 标题
        body (str): 正文
        group (str): 通知分组，如 DouYin
    """
    report = _current_report.get()
    if report is not None:
        options = {"group": group} if group else {}
        await report.notifier.send(title, body, **options)

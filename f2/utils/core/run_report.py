# path: f2/utils/core/run_report.py

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Iterator, List, Optional


@dataclass
class RunReport:
    """
    一次 CLI 运行的结果汇总 (Summary of a single CLI run)

    下载器把最终失败的文件记在这里，CLI 在运行结束后据此决定退出码。
    作为库使用时默认没有活动的汇总对象，记录操作不产生任何效果。

    属性:
    - failed_downloads (List[str]): 所有链接都下载失败的文件路径。
    """

    failed_downloads: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """本次运行是否没有失败的下载 (Whether no download failed)"""
        return not self.failed_downloads


_current_report: ContextVar[Optional[RunReport]] = ContextVar(
    "f2_run_report", default=None
)


@contextmanager
def collect_run_report() -> Iterator[RunReport]:
    """
    在上下文内收集运行结果 (Collect run results within the context)

    上下文变量会随 asyncio.run 与其中创建的任务一起传递，
    因此下载任务里的记录都会汇总到同一个对象上。

    Yields:
        RunReport: 本次运行的结果汇总
    """

    report = RunReport()
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

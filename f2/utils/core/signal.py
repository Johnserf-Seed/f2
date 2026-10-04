# path: f2/utils/core/signal.py

import asyncio
import signal
import sys
from asyncio import CancelledError
from types import FrameType

from f2.cli.cli_console import RichConsoleManager
from f2.utils.core.singleton import Singleton


class SignalManager(metaclass=Singleton):
    """
    信号管理器 (Signal Manager)

    该类用于处理和管理程序运行期间接收到的信号，尤其是用于捕获中断信号（如 SIGINT 和 SIGTERM）以优雅地关闭程序。

    它提供了一种机制来管理程序关闭时的清理操作和取消所有正在运行的 asyncio 任务。

    类属性:
    - _shutdown_event (asyncio.Event): 一个事件对象，用于标记程序是否接收到关闭信号。

    类方法:
    - __init__: 初始化 SignalManager 实例，并创建一个 shutdown_event。
    - shutdown_event: 提供对 shutdown_event 的只读访问，用于检查程序是否收到关闭信号。
    - _handle_signal: 内部方法，用于处理接收到的信号，停止 asyncio 事件循环，并退出程序。
    - register_shutdown_signal: 注册 SIGINT 和 SIGTERM 信号处理程序，捕获关闭信号并触发清理操作。
    - is_shutdown_signaled: 检查是否接收到关闭信号。

    使用示例:
    ```python
        # 创建 SignalManager 实例并注册信号处理程序
        signal_manager = SignalManager()
        signal_manager.register_shutdown_signal()

        # 在程序中的其他部分，可以使用以下方式检查是否接收到关闭信号
        if SignalManager.is_shutdown_signaled():
            # 执行关闭操作
            print("Shutting down gracefully...")
    ```

    异常处理:
    - 收到信号后退出程序，退出码为 128 + 信号编号（SIGINT 为 130，SIGTERM 为 143）。
    """

    def __init__(self):
        self._shutdown_event = asyncio.Event()

    @property
    def shutdown_event(self):
        """提供对shutdown_event的只读访问"""
        return self._shutdown_event

    def _handle_signal(self, received_signal: int, frame: FrameType | None) -> None:
        """内部处理接收到的信号"""
        self._shutdown_event.set()

        # 取消所有运行中的asyncio任务
        loop = asyncio.get_running_loop()  # 避免DeprecationWarning

        try:
            if loop.is_running():
                for task in asyncio.all_tasks(loop):
                    task.cancel()
                # 等待所有任务被取消并处理异常
                # 注意：不再使用 async/await，所以这里不使用 asyncio.gather
                for task in asyncio.all_tasks(loop):
                    try:
                        task.result()  # 获取任务的结果，以便抛出异常
                    except Exception:
                        pass
        except (
            Exception,
            CancelledError,
            KeyboardInterrupt,
            SystemExit,
        ):
            pass
        finally:
            # 结束前的输出
            RichConsoleManager().rich_console.print(
                "\n[bold yellow]exiting f2...[/bold yellow]"
            )
            # 按 shell 的惯例以 128 + 信号编号退出（Ctrl+C 为 130），脚本可以判断运行被中断；
            # 此前 is_test 的判断写反了，正常运行时总是以 0 退出
            sys.exit(128 + received_signal)

    def register_shutdown_signal(self):
        """注册一个处理程序来捕获关闭信号"""
        signal.signal(signal.SIGINT, self._handle_signal)
        # 捕获SIGTERM信号，确保更好的跨平台兼容性
        signal.signal(signal.SIGTERM, self._handle_signal)

    @classmethod
    def is_shutdown_signaled(cls):
        """检查是否接收到了关闭信号"""
        instance = cls()  # 获取单例实例
        return instance.shutdown_event.is_set()

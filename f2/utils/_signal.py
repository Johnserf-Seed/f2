import sys
import signal
import asyncio

from asyncio import CancelledError

from f2.utils._singleton import Singleton
from f2.cli.cli_console import RichConsoleManager


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
    - 捕获异常并在需要时处理取消的 asyncio 任务。
    - 在收到关闭信号时，取消所有正在运行的 asyncio 任务，并退出程序。
    """

    def __init__(self):
        self._shutdown_event = asyncio.Event()

    @property
    def shutdown_event(self):
        """提供对shutdown_event的只读访问"""
        return self._shutdown_event

    def _handle_signal(self, received_signal: signal.Signals, frame: object) -> None:
        """内部处理接收到的信号"""
        self._shutdown_event.set()
        RichConsoleManager().rich_console.print("\nexiting f2...")

        # 取消所有运行中的asyncio任务
        loop = asyncio.get_event_loop()
        try:
            if loop.is_running():
                for task in asyncio.all_tasks(loop):
                    task.cancel()
                loop.stop()
        except (Exception, CancelledError) as e:
            pass

        # 执行资源清理操作
        sys.exit(0)

    def register_shutdown_signal(self):
        """注册一个处理程序来捕获关闭信号"""
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(
            signal.SIGTERM, self._handle_signal
        )  # 捕获SIGTERM信号，确保更好的跨平台兼容性

    @classmethod
    def is_shutdown_signaled(cls):
        """检查是否接收到了关闭信号"""
        instance = cls()  # 获取单例实例
        return instance.shutdown_event.is_set()


# 当需要的时候，就注册这个关闭信号
# signal_manager = SignalManager()
# signal_manager.register_shutdown_signal()

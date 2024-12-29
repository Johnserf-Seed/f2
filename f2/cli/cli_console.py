# path: f2/cli/cli_console.py

from asyncio import Lock
from typing import Optional, Dict
from rich.prompt import Prompt
from rich.console import Console
from rich.spinner import Spinner
from rich.progress import (
    Progress as RichProgress,
    TaskID,
    Task,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    DownloadColumn,
    TransferSpeedColumn,
    ProgressColumn,
    # TimeElapsedColumn,
)

from f2.utils._singleton import Singleton


class CustomSpinnerColumn(ProgressColumn):
    """
    CustomSpinnerColumn 类用于创建和管理自定义的进度指示器列。通过此类，可以为不同的状态（如等待、开始、下载、暂停等）配置不同的旋转动画。

    该类继承自 ProgressColumn，利用 rich 库中的 Spinner 来实现多种旋转动画效果。

    类属性:
    - DEFAULT_SPINNERS: 默认的各个状态对应的旋转动画类型。
    - spinners: 用于存储不同状态的 Spinner 对象。

    类方法:
    - __init__: 初始化 CustomSpinnerColumn 实例，根据传入的 spinner_styles 配置不同状态的旋转动画。
    - render: 渲染当前任务的进度指示器，根据任务状态（state）选择合适的旋转动画并返回其渲染结果。

    使用示例:
    ```python
        # 自定义不同状态的旋转动画
        custom_spinner_column = CustomSpinnerColumn(
            spinner_styles={
                "waiting": "dots8",
                "starting": "arrow",
                "downloading": "moon",
                "paused": "smiley",
                "error": "star2",
                "completed": "hearts",
            }
        )

        # 渲染自定义的进度指示器
        custom_spinner_column.render(task)
    ```
    """

    DEFAULT_SPINNERS = {
        "waiting": "dots8",
        "starting": "arrow",
        "downloading": "moon",
        "paused": "smiley",
        "error": "star2",
        "completed": "hearts",
    }

    def __init__(
        self,
        spinner_styles: Optional[Dict[str, str]] = None,
        style: str = "progress.spinner",
        speed: float = 1.0,
    ):
        spinner_styles = spinner_styles or {}
        spinner_names = {
            state: spinner_styles.get(state, default)
            for state, default in self.DEFAULT_SPINNERS.items()
        }
        self.spinners = {
            state: Spinner(spinner_name, style=style, speed=speed)
            for state, spinner_name in spinner_names.items()
        }
        super().__init__()

    def render(self, task: Task):
        t = task.get_time()
        state = task.fields.get("state", "starting")
        spinner = self.spinners.get(state, self.spinners["starting"])
        return spinner.render(t)


class ProgressManager:
    """
    ProgressManager 类用于管理进度条和任务的显示，允许在控制台中显示多个并行任务的进度信息。

    该类封装了 rich 库的进度条功能，支持自定义进度列、自定义spinner列、任务更新、任务启动和停止等操作。

    类属性:
    - DEFAULT_COLUMNS: 默认的进度条列，包括spinner列、描述列、进度条列等。
    - _progress: rich 库中的 Progress 实例，负责绘制进度条。
    - _progress_lock: 用于同步进度条更新的锁。
    - _active_tasks: 存储正在进行中的任务 ID。

    方法:
    - __init__: 初始化 ProgressManager 实例，允许传入自定义列、进度条宽度等参数。
    - start: 启动进度条显示。
    - start_task: 启动一个具体任务的进度显示。
    - stop: 停止进度条显示。
    - stop_task: 停止一个具体任务的进度显示。
    - add_task: 异步添加一个新任务到进度条管理器中。
    - update: 异步更新任务的进度、描述、状态等信息。
    - __enter__: 启动进度条并支持使用 `with` 语法块。
    - __exit__: 停止进度条，确保任务完成。

    使用示例:
    ```python
        # 创建并启动进度管理器
        progress_manager = ProgressManager()
        progress_manager.start()

        # 添加任务并更新进度
        task_id = await progress_manager.add_task("任务描述", total=100)
        await progress_manager.update(task_id, completed=50)

        # 停止任务
        await progress_manager.stop_task(task_id)
    ```
    """

    DEFAULT_COLUMNS = {
        "spinner": CustomSpinnerColumn(),
        "description": TextColumn(
            "{task.description}[bold blue]{task.fields[filename]}"
        ),
        "bar": BarColumn(bar_width=None),
        "percentage": TextColumn("[progress.percentage]{task.percentage:>4.2f}%"),
        "•": "•",
        "filesize": DownloadColumn(),
        "speed": TransferSpeedColumn(),
        "ETA": "[bold blue]ETA",
        "remaining": TimeRemainingColumn(),
    }

    def __init__(
        self,
        spinner_column: CustomSpinnerColumn = None,
        custom_columns: Optional[Dict[str, ProgressColumn]] = None,
        bar_width: Optional[int] = None,
        expand: bool = False,
    ):
        chosen_columns_dict = custom_columns or self.DEFAULT_COLUMNS.copy()
        if spinner_column:
            chosen_columns_dict = {"spinner": spinner_column, **chosen_columns_dict}
        if "bar" in chosen_columns_dict and isinstance(
            chosen_columns_dict["bar"], BarColumn
        ):
            bar_column = chosen_columns_dict["bar"]
            bar_column.bar_width = bar_width or 40
        self._progress = RichProgress(
            *chosen_columns_dict.values(), transient=False, expand=expand
        )
        self._progress_lock = Lock()
        self._active_tasks = set()

    def start(self):
        self._progress.start()

    def start_task(self, task_id):
        self._progress.start_task(task_id)

    def stop(self):
        self._progress.stop()

    def stop_task(self, task_id):
        self._progress.stop_task(task_id)

    @property
    def tasks(self):
        return self._progress.tasks

    async def add_task(
        self,
        description: str,
        start: bool = True,
        total: Optional[float] = None,
        completed: int = 0,
        visible: bool = True,
        state: str = "starting",
        filename: str = "",
    ) -> TaskID:
        async with self._progress_lock:
            task_id = self._progress.add_task(
                description=description,
                start=start,
                total=total,
                completed=completed,
                visible=visible,
                filename=filename,
                state=state,
            )
            self._active_tasks.add(task_id)
        return task_id

    async def update(
        self,
        task_id: TaskID,
        total: Optional[float] = None,
        completed: Optional[float] = None,
        advance: Optional[float] = None,
        description: Optional[str] = None,
        visible: bool = True,
        refresh: bool = False,
        filename=None,
        state: Optional[str] = None,
    ) -> None:
        async with self._progress_lock:
            update_params = {
                key: value
                for key, value in [
                    ("advance", advance),
                    ("description", description),
                    ("state", state),
                    ("filename", filename),
                ]
                if value
            }

            self._progress.update(
                task_id,
                total=total,
                completed=completed,
                visible=visible,
                refresh=refresh,
                **update_params,
            )

            if self._progress.tasks[task_id].finished and task_id in self._active_tasks:
                self._active_tasks.remove(task_id)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class RichConsoleManager(metaclass=Singleton):
    """
    RichConsoleManager 类用于管理进度条和日志输出的控制台，封装了 rich 库中的控制台和进度条功能。

    想要激活进度条，只需使用 with 语句包裹需要显示进度的代码块即可。

    该类利用 Singleton 模式保证只有一个实例，并提供便捷的方法来访问控制台、进度管理器和日志输出。

    类属性:
    - _progress_manager: ProgressManager 实例，用于管理进度条。
    - exception_console: 用于输出异常信息的 Console 实例。
    - rich_console: 主控制台的 Console 实例。
    - rich_prompt: 用于接收用户输入的 Prompt 实例。

    方法:
    - __init__: 初始化 RichConsoleManager 实例，并创建 ProgressManager。
    - progress: 返回 ProgressManager 实例，管理进度条。
    - exception_console: 返回用于输出异常信息的控制台实例。
    - rich_console: 返回主控制台实例，用于显示日志和信息。
    - rich_prompt: 返回用于提示用户输入的 Prompt 实例。

    使用示例:
    ```python
        # 创建 RichConsoleManager 实例
        console_manager = RichConsoleManager()

        # 使用进度条
        with RichConsoleManager.progress:
            task_id = await console_manager.progress.add_task("下载中", total=100)
            await console_manager.progress.update(task_id, completed=50)

        # 输出异常信息
        console_manager.exception_console.print("[bold red]发生错误！[/bold red]")
    ```
    """

    def __init__(self):
        self._progress_manager = ProgressManager()

    @property
    def progress(self) -> ProgressManager:
        return self._progress_manager

    @property
    def exception_console(self) -> Console:
        return Console()

    @property
    def rich_console(self) -> Console:
        return Console()

    @property
    def rich_prompt(self) -> Prompt:
        return Prompt()

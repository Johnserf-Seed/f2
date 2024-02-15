# path: tests/test_cli_console.py

import pytest
import time
from f2.cli.cli_console import CustomSpinnerColumn, ProgressManager
from rich.spinner import Spinner


def test_custom_spinner_column():
    # 使用默认样式初始化
    default_column = CustomSpinnerColumn()
    for state in CustomSpinnerColumn.DEFAULT_SPINNERS:
        assert state in default_column.spinners
        assert isinstance(default_column.spinners[state], Spinner)

    # 使用自定义样式初始化
    custom_spinners = {
        "waiting": "dots2",
        "downloading": "moon",
    }
    custom_column = CustomSpinnerColumn(spinner_styles=custom_spinners)
    for state in custom_spinners:
        assert isinstance(custom_column.spinners[state], Spinner)


async def simulate_progress(progress_manager: ProgressManager):
    progress_manager.start()

    task_id = await progress_manager.add_task("Demo Task", state="waiting", total=100)
    for _ in range(10):
        time.sleep(0.1)
        if _ == 5:
            await progress_manager.update(
                task_id,
                description="[  Demo  ]:",
                filename="test download task",
                state="downloading",
            )
        await progress_manager.update(task_id, advance=10)

    progress_manager.stop()


@pytest.mark.asyncio
async def test_custom_progress():
    my_spinners = {
        "waiting": "dots2",
        "downloading": "moon",
        "starting": "point",
        "paused": "dots8",
        "error": "star2",
    }
    custom_spinner_column = CustomSpinnerColumn(spinner_styles=my_spinners)
    progress_manager_custom = ProgressManager(spinner_column=custom_spinner_column)
    await simulate_progress(progress_manager_custom)

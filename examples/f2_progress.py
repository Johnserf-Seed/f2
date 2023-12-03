import time
from f2.cli.cli_console import RichConsoleManager, CustomSpinnerColumn, ProgressManager
from f2.cli.cli_console import TextColumn, BarColumn, TimeElapsedColumn


if __name__ == "__main__":

    def simulate_progress(progress_manager):
        # 启动进度条
        progress_manager.start()

        # 添加一个任务
        task_id = progress_manager.add_task(
            "Demo Task: waiting", total=200, state="waiting"
        )
        for _ in range(20):
            time.sleep(0.1)
            if _ == 4:  # 模拟开始下载
                progress_manager.update(
                    task_id, description="Demo Task: starting", state="starting"
                )
            elif _ == 8:  # 模拟下载中
                progress_manager.update(
                    task_id, description="Demo Task: downloading", state="downloading"
                )
            elif _ == 12:  # 模拟暂停
                progress_manager.update(
                    task_id, description="Demo Task: paused", state="paused"
                )
                time.sleep(1)  # 暂停一会儿
                progress_manager.update(
                    task_id, description="Demo Task: downloading", state="downloading"
                )
            elif _ == 16:  # 模拟出错
                progress_manager.update(
                    task_id, description="Demo Task: error", state="error"
                )
                time.sleep(0.5)
                progress_manager.update(
                    task_id, description="Demo Task: completed", state="completed"
                )

            progress_manager.update(task_id, advance=10)

        # 停止进度条
        progress_manager.stop()

    print("Showing default progress:")
    progress_manager_default = ProgressManager()
    simulate_progress(progress_manager_default)

    print("\nShowing custom progress:")
    my_spinners = {
        "waiting": "dots12",
        "downloading": "earth",
    }
    custom_spinner_column = CustomSpinnerColumn(spinner_styles=my_spinners, speed=0.5)
    progress_manager_custom = ProgressManager(spinner_column=custom_spinner_column)
    simulate_progress(progress_manager_custom)

    print("\nShowing custom 2 progress:")
    custom_columns = {
        "description": TextColumn("{task.description}"),
        "bar": BarColumn(
            complete_style="bright_magenta black", finished_style="bright_white green"
        ),
        "custom_percentage": TextColumn(
            "[progress.custom_percentage]{task.percentage:>2.0f}%", style="bright_cyan"
        ),
        "elapsed": TimeElapsedColumn(),
    }
    progress_manager_custom2 = ProgressManager(
        spinner_column=custom_spinner_column,
        custom_columns=custom_columns,
        expand=False,
    )
    simulate_progress(progress_manager_custom2)

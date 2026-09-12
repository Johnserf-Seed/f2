# path: f2/utils/core/decorators.py

from collections import defaultdict
from typing import Callable, DefaultDict, Dict

# 按应用分开保存的模式表：{应用名: {模式名: 处理函数}}
# 同一进程里导入多个应用（如同时用 douyin 与 tiktok）时，各自的 post/one 等模式互不覆盖
_mode_registry: DefaultDict[str, Dict[str, Callable]] = defaultdict(dict)


def app_name_of(module_name: str) -> str:
    """
    从模块名推断应用名 (Infer the app name from a module name)

    "f2.apps.douyin.handler" -> "douyin"；不在 f2.apps 下的模块返回模块名本身。
    """

    parts = module_name.split(".")
    if len(parts) >= 3 and parts[:2] == ["f2", "apps"]:
        return parts[2]
    return module_name


def mode_handler(mode_name: str) -> Callable:
    """
    把处理函数注册为所在应用的某个模式 (Register a function as a mode handler of its app)

    Args:
        mode_name (str): 模式名，如 "post"、"one"

    使用示例:
    ```python
        @mode_handler("post")
        async def handle_user_post(handler: DouyinHandler) -> None: ...
    ```
    """

    def decorator(function: Callable) -> Callable:
        _mode_registry[app_name_of(function.__module__)][mode_name] = function
        return function

    return decorator


def get_mode_handlers(module_or_app: str) -> Dict[str, Callable]:
    """
    获取某个应用注册的全部模式 (Mode handlers registered by an app)

    Args:
        module_or_app (str): 应用名（"douyin"）或应用内的模块名（通常传 __name__）

    Returns:
        Dict[str, Callable]: {模式名: 处理函数}，未注册任何模式时为空字典
    """

    return _mode_registry[app_name_of(module_or_app)]

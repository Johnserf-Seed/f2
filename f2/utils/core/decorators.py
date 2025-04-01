# path: f2/utils/core/decorators.py

from typing import Callable, Dict

mode_function_map: Dict[str, Callable] = {}


def mode_handler(mode_name: str) -> Callable:
    def decorator(function: Callable) -> Callable:
        mode_function_map[mode_name] = function
        return function

    return decorator

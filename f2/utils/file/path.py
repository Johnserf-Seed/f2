# path: f2/utils/file/path.py

from pathlib import Path
from typing import Union

import importlib_resources


def get_resource_path(filepath: str) -> Path:
    """
    获取资源文件的路径 (Get the path of the resource file)

    Args:
        filepath: str: 文件路径 (file path)
    """
    return importlib_resources.files("f2") / filepath


def ensure_path(path: Union[str, Path]) -> Path:
    """确保路径是一个Path对象 (Ensure the path is a Path object)"""
    return Path(path) if isinstance(path, str) else path

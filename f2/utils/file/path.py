# path: f2/utils/file/path.py

import ntpath
import sys
from importlib.resources import files
from pathlib import Path
from typing import Union

# Windows 未开启长路径支持时，目录路径最多 247 个字符，文件路径最多 259 个字符
WINDOWS_MAX_DIR_PATH = 247


def get_resource_path(filepath: str) -> Path:
    """
    获取资源文件的路径 (Get the path of the resource file)

    Args:
        filepath: str: 文件路径 (file path)
    """
    return Path(str(files("f2") / filepath))


def ensure_path(path: Union[str, Path]) -> Path:
    """确保路径是一个Path对象 (Ensure the path is a Path object)"""
    return Path(path) if isinstance(path, str) else path


def extended_length_path(path: str) -> str:
    r"""
    把 Windows 绝对路径转换为扩展长度路径 (Convert an absolute Windows path to the extended-length form)

    普通路径加上 \\?\ 前缀，UNC 路径 \\server\share 转换为 \\?\UNC\server\share；
    已经是扩展长度或设备路径时原样返回。扩展长度路径不会再被规范化，调用前需转换为绝对路径。
    """
    if path.startswith(("\\\\?\\", "\\\\.\\")):
        return path
    if path.startswith("\\\\"):
        return "\\\\?\\UNC\\" + path[2:]
    return "\\\\?\\" + path


def long_path(path: Union[str, Path]) -> Path:
    """
    Windows 下路径较长时改用扩展长度路径 (Use an extended-length path for long Windows paths)

    Windows 默认只允许 260 个字符以内的路径，超出时即使文件名本身合法也无法创建。
    扩展长度路径不依赖系统是否开启了长路径支持；其他平台与较短的路径原样返回。
    """
    path = ensure_path(path)
    if sys.platform != "win32":
        return path
    absolute = ntpath.abspath(path)
    if len(absolute) <= WINDOWS_MAX_DIR_PATH:
        return path
    return Path(extended_length_path(absolute))

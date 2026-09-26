# path: f2/utils/file/path.py

import ntpath
import sys
from importlib.resources import files
from pathlib import Path
from typing import Union

from f2.i18n.translator import _
from f2.log.logger import logger

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


def get_user_folder_path(
    kwargs: dict, app_name: str, folder_name: Union[str, int]
) -> Path:
    """
    获取用户目录的绝对路径，不创建目录
    (Get the absolute path of a user folder without creating it)

    Args:
        kwargs (dict): 配置参数，使用其中的 path 与 mode (Conf parameters, path and mode are used)
        app_name (str): 应用名，如 douyin (App name, e.g. douyin)
        folder_name (Union[str, int]): 用户目录名，如用户昵称 (User folder name, e.g. user nickname)

    Returns:
        Path: 用户目录的绝对路径，即 path/应用名/mode/用户目录名
        (Absolute path of the user folder, i.e. path/app_name/mode/folder_name)

    Note:
        如果未在配置文件中指定路径，则默认为 "Download"。支持绝对与相对路径。
        (If the path is not specified in the conf file, it defaults to "Download".
        Absolute and relative paths are supported.)

    Raises:
        TypeError: 如果 kwargs 不是字典格式，将引发 TypeError。
        (If kwargs is not in dict format, TypeError will be raised.)
    """

    # 确定函数参数是否正确
    if not isinstance(kwargs, dict):
        raise TypeError("kwargs 参数必须是字典")

    # 创建基础路径
    base_path = Path(kwargs.get("path", "Download"))

    # 添加应用名、下载模式和用户目录名
    user_path = (
        base_path
        / app_name
        / kwargs.get("mode", "PLEASE_SETUP_MODE")
        / str(folder_name)
    )

    # 获取绝对路径
    return user_path.resolve()


def _is_same_folder(path: Path, other: Path) -> bool:
    try:
        return path.samefile(other)
    except OSError:
        return False


def migrate_user_folder(old_path: Path, new_path: Path) -> Path:
    """
    用户改名后，把旧名称的用户目录重命名为新名称
    (Rename the user folder of the old name to the new name after the user changes it)

    Args:
        old_path (Path): 旧名称的用户目录 (User folder of the old name)
        new_path (Path): 新名称的用户目录，与旧目录在同一父目录下
        (User folder of the new name, in the same parent folder as the old one)

    Returns:
        Path: 之后使用的用户目录，只有重命名失败时才是旧目录，不存在时由调用方创建
        (The user folder to use from now on, the old one only if renaming failed;
        the caller creates it if it does not exist)

    Note:
        旧目录不存在时什么都不做；新目录已存在时两个目录都保持不变，不会覆盖或合并。
        (Nothing is done if the old folder does not exist. If the new folder already
        exists, both folders are left as they are and nothing is overwritten or merged.)
    """

    # 只重命名同一父目录下的目录，名称异常（如 ".."）时不移动任何目录
    if (
        str(old_path) == str(new_path)
        or old_path.parent != new_path.parent
        or not old_path.is_dir()
    ):
        return new_path

    # 路径中可能有方括号等字符，日志不按 rich 标记解析
    no_markup = {"markup": False}

    # 不区分大小写的文件系统上只改了大小写时，新旧路径是同一个目录，照常重命名
    if new_path.exists() and not _is_same_folder(old_path, new_path):
        logger.warning(
            _(
                "用户名称已变化，但新旧用户目录同时存在，不会自动合并：继续使用 {0}，旧目录 {1} 保持不变，可手动合并"
            ).format(new_path, old_path),
            extra=no_markup,
        )
        return new_path

    try:
        old_path.rename(new_path)
    except OSError as e:
        logger.warning(
            _("无法将用户目录 {0} 重命名为 {1}：{2}，本次继续使用旧目录").format(
                old_path, new_path.name, e
            ),
            extra=no_markup,
        )
        return old_path

    logger.info(
        _("用户名称已变化，已将用户目录 {0} 重命名为 {1}").format(
            old_path, new_path.name
        ),
        extra=no_markup,
    )
    return new_path

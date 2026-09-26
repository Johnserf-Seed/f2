# path: f2/utils/file/path.py

import ntpath
import os
import sys
from importlib.resources import files
from pathlib import Path
from typing import List, Optional, Union

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


def _app_folder_path(kwargs: dict, app_name: str) -> Path:
    # 确定函数参数是否正确
    if not isinstance(kwargs, dict):
        raise TypeError("kwargs 参数必须是字典")

    # 创建基础路径并添加应用名
    return (Path(kwargs.get("path", "Download")) / app_name).resolve()


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

    # 添加下载模式和用户目录名
    user_path = (
        _app_folder_path(kwargs, app_name)
        / kwargs.get("mode", "PLEASE_SETUP_MODE")
        / str(folder_name)
    )

    # 获取绝对路径
    return user_path.resolve()


def _mode_folder_paths(kwargs: dict, app_name: str) -> List[Path]:
    # 应用目录下已有的各下载模式目录，应用目录不存在或无法读取时为空
    try:
        return sorted(
            path.resolve()
            for path in _app_folder_path(kwargs, app_name).iterdir()
            if path.is_dir()
        )
    except OSError:
        return []


def _is_same_folder(path: Path, other: Path) -> bool:
    try:
        return path.samefile(other)
    except OSError:
        return False


def _has_exact_name(path: Path) -> bool:
    # 不区分大小写的文件系统上 exists() 也不区分大小写，按目录项的原名判断
    try:
        return path.name in os.listdir(path.parent)
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

    if new_path.exists():
        # 不区分大小写的文件系统上只改了大小写时，新旧路径是同一个目录：
        # 目录名已经是新名称就不用再改，否则照常重命名
        if _is_same_folder(old_path, new_path):
            if _has_exact_name(new_path):
                return new_path
        else:
            logger.warning(
                _(
                    "用户名称已变化，但新旧用户目录同时存在，不会自动合并：继续使用 {0}，旧目录 {1} 保持不变，手动合并并删除旧目录后不再提示"
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


def migrate_user_folders(
    kwargs: dict,
    app_name: str,
    old_name: Union[str, int],
    new_name: Union[str, int],
) -> Path:
    """
    用户改名后，把各下载模式下旧名称的用户目录都重命名为新名称
    (Rename the user folders of the old name to the new name in every download mode
    after the user changes it)

    Args:
        kwargs (dict): 配置参数，使用其中的 path 与 mode (Conf parameters, path and mode are used)
        app_name (str): 应用名，如 douyin (App name, e.g. douyin)
        old_name (Union[str, int]): 旧的用户目录名 (Old user folder name)
        new_name (Union[str, int]): 新的用户目录名 (New user folder name)

    Returns:
        Path: 当前下载模式使用的用户目录，只有它重命名失败时才是旧目录，不存在时由调用方创建
        (The user folder to use in the current download mode, the old one only if
        renaming it failed; the caller creates it if it does not exist)

    Note:
        处理 path/应用名 下的每个下载模式目录，每个目录都按 migrate_user_folder 的规则重命名。
        (Every download mode folder under path/app_name is renamed by the rules of
        migrate_user_folder.)
    """

    # 先处理当前下载模式，本次下载使用它的结果
    new_path = get_user_folder_path(kwargs, app_name, new_name)
    user_path = migrate_user_folder(
        get_user_folder_path(kwargs, app_name, old_name), new_path
    )

    # 再处理其他下载模式，以后用这些模式下载时目录已是新名称
    for mode_path in _mode_folder_paths(kwargs, app_name):
        if mode_path != new_path.parent:
            migrate_user_folder(
                (mode_path / str(old_name)).resolve(),
                (mode_path / str(new_name)).resolve(),
            )

    return user_path


def is_user_folder_migrated(
    kwargs: dict,
    app_name: str,
    old_name: Optional[Union[str, int]],
    new_name: Optional[Union[str, int]],
) -> bool:
    """
    用户名称已变化，且各下载模式下都已没有待重命名的旧名称目录
    (The user's name has changed and no folder of the old name is left to rename in
    any download mode)

    Args:
        kwargs (dict): 配置参数，使用其中的 path 与 mode (Conf parameters, path and mode are used)
        app_name (str): 应用名，如 douyin (App name, e.g. douyin)
        old_name (Optional[Union[str, int]]): 本地记录中的名称 (Name in the local record)
        new_name (Optional[Union[str, int]]): 当前名称 (Current name)

    Returns:
        bool: 为 True 时可以把本地记录中的名称更新为新名称；名称没有变化，或者还有旧目录
        （新旧目录同时存在、重命名失败）时为 False，下次运行时继续处理
        (True when the name in the local record can be updated to the new one; False
        if the name has not changed or an old folder is left because both folders
        exist or renaming failed, so that the next run handles it again)
    """

    if not old_name or not new_name or str(old_name) == str(new_name):
        return False

    mode_paths = set(_mode_folder_paths(kwargs, app_name))
    mode_paths.add(get_user_folder_path(kwargs, app_name, new_name).parent)

    for mode_path in mode_paths:
        old_path = (mode_path / str(old_name)).resolve()
        new_path = (mode_path / str(new_name)).resolve()

        # 名称异常（如 ".."）的目录不会被重命名，不必等待
        if old_path.parent != new_path.parent or not old_path.is_dir():
            continue

        # 只改了大小写且已重命名时，旧路径在不区分大小写的文件系统上仍然存在
        if not (_is_same_folder(old_path, new_path) and _has_exact_name(new_path)):
            return False

    return True

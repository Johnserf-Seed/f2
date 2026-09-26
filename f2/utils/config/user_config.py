# path: f2/utils/config/user_config.py

"""
用户级 F2 配置 (User-level F2 configuration)

site-packages 中的 conf.yaml 保存默认值。只需修改部分设置时，可以把它们写进下面的文件，
按优先级从低到高依次覆盖默认值（#377）：

1. 用户目录：~/.f2/conf.yaml
2. 项目目录：运行 F2 时所在目录下的 conf.yaml
3. 环境变量 F2_CONFIG 指定的文件

本模块只依赖标准库与 ruamel.yaml，不导入翻译、日志等模块，避免循环导入。
"""

import copy
import os
from pathlib import Path
from typing import Any, List, Optional

from ruamel.yaml import YAML  # type: ignore[import-untyped]

USER_CONFIG_ENV = "F2_CONFIG"
USER_CONFIG_NAME = "conf.yaml"


class NotAMappingError(ValueError):
    """配置文件的顶层不是键值映射 (The top level of the config file is not a mapping)"""


def user_config_dir() -> Path:
    """用户目录下存放 F2 配置的文件夹 (~/.f2)"""
    return Path.home() / ".f2"


def _resolve(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def user_config_paths(exclude: Optional[Path] = None) -> List[Path]:
    """
    按优先级从低到高返回需要叠加的用户配置文件 (User config files, lowest priority first)

    用户目录与项目目录中的文件存在时才返回；环境变量指定的文件总是返回，
    不存在时由读取方报错，避免拼写错误被悄悄忽略。

    Args:
        exclude (Optional[Path]): 需要排除的文件，通常是默认配置文件本身

    Returns:
        List[Path]: 用户配置文件路径
    """
    candidates: List[Path] = [user_config_dir() / USER_CONFIG_NAME]
    try:
        candidates.append(Path.cwd() / USER_CONFIG_NAME)
    except OSError:  # 当前目录已被删除
        pass
    candidates = [path for path in candidates if path.is_file()]

    env_path = os.environ.get(USER_CONFIG_ENV)
    if env_path:
        candidates.append(Path(env_path).expanduser())

    excluded = _resolve(exclude) if exclude is not None else None
    paths: List[Path] = []
    seen = set()
    for path in candidates:
        resolved = _resolve(path)
        if resolved == excluded or resolved in seen:
            continue
        seen.add(resolved)
        paths.append(path)
    return paths


def read_yaml_mapping(path: Path) -> dict:
    """
    读取 YAML 文件，顶层必须是键值映射，空文件视为空映射 (Read a YAML mapping)

    Raises:
        NotAMappingError: 顶层不是键值映射
    """
    with open(path, "r", encoding="utf-8") as file:
        data = YAML().load(file)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise NotAMappingError(str(path))
    return data


def deep_merge(base: Any, override: Any) -> Any:
    """
    返回 base 被 override 覆盖后的新对象，不修改传入的对象 (Deep-merge override into base)

    两边都是字典时逐键递归合并，否则直接取 override（列表等整体替换）。
    """
    if isinstance(base, dict) and isinstance(override, dict):
        merged = copy.deepcopy(base)
        for key, value in override.items():
            if key in merged:
                merged[key] = deep_merge(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged
    return copy.deepcopy(override)

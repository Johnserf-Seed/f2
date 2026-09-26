# path: f2/utils/config/conf_manager.py

import copy
import os
import shutil
from pathlib import Path
from typing import Any, Dict

import click
from ruamel.yaml import YAML  # type: ignore[import-untyped]
from ruamel.yaml.comments import CommentedMap  # type: ignore[import-untyped]

import f2
from f2.exceptions.conf_exceptions import ConfError
from f2.exceptions.file_exceptions import (
    FileNotFound,
    FilePermissionError,
)
from f2.i18n.translator import _
from f2.log.logger import logger
from f2.utils.config.user_config import (
    USER_CONFIG_ENV,
    NotAMappingError,
    deep_merge,
    read_yaml_mapping,
    user_config_paths,
)
from f2.utils.file.path import get_resource_path

# 用户级 conf.yaml 的合并结果，按文件路径与修改时间缓存：同一进程只读取、只提示一次
_USER_OVERRIDES_CACHE: Dict[tuple, Any] = {}


def _file_signature(path: Path) -> tuple:
    try:
        stat = path.stat()
        return (str(path.resolve()), stat.st_mtime_ns, stat.st_size)
    except OSError:
        return (str(path), None, None)


def describe_yaml_error(error: Exception) -> str:
    """
    把读取 YAML 时的错误整理成一行 (Describe a YAML loading error in one line)

    语法错误给出问题与出错的行列号；文件不是 UTF-8 编码时直接说明，
    常见于用记事本以 ANSI（GBK）编码保存的配置文件。
    """
    if isinstance(error, UnicodeDecodeError):
        return _("文件不是 UTF-8 编码，请另存为 UTF-8 后重试")
    problem = getattr(error, "problem", None)
    mark = getattr(error, "problem_mark", None)
    if problem and mark is not None:
        return _("{0}（第 {1} 行第 {2} 列）").format(
            problem, mark.line + 1, mark.column + 1
        )
    return " ".join(str(error).split())


def merge_missing_keys(target: dict, defaults: dict) -> int:
    """
    把 defaults 里 target 缺少的键补进 target，嵌套的字典会递归补充，已有的值保持不变
    (Copy keys that are missing from target out of defaults, recursively, without
    touching existing values)

    Args:
        target (dict): 要补充的配置，会被原地修改
        defaults (dict): 默认配置

    Returns:
        int: 补充的键数量
    """
    added = 0
    for key, value in defaults.items():
        if key not in target:
            target[key] = copy.deepcopy(value)
            added += 1
        elif isinstance(target[key], dict) and isinstance(value, dict):
            added += merge_missing_keys(target[key], value)
    return added


class ConfigManager:
    """
    配置管理器 (Configuration Manager)

    该类用于加载、管理和更新应用的配置文件。通过提供的路径读取配置，支持配置文件的备份、更新和保存功能。
    它还可以生成默认配置文件，处理与配置相关的错误，并使用字典格式来组织配置数据。
    使用ruamel.yaml库保留YAML文件的注释、格式和顺序。

    类属性:
    - filepath (Path): 配置文件的路径。
    - config (dict): 存储的配置数据，以字典形式表示。
    - yaml (YAML): ruamel.yaml实例，用于处理YAML文件。

    类方法:
    - __init__: 初始化配置管理器，加载配置文件。
    - _replace_none: 递归地将字典或列表中的 None 值替换为默认值。
    - load_config: 加载配置文件，处理文件读取和解析错误。
    - get_config: 获取指定应用名称的配置数据。
    - save_config: 将配置数据保存到文件。
    - backup_config: 在更新配置前备份当前配置文件。
    - generate_config: 根据应用名称生成并保存特定配置文件。
    - update_config_with_args: 使用命令行参数更新配置文件。

    异常处理:
    - FileNotFound: 如果配置文件不存在，抛出文件未找到异常。
    - FilePermissionError: 如果配置文件路径没有读写权限，抛出权限异常。
    - yaml.YAMLError: 如果配置文件解析出错，抛出解析错误异常。

    使用示例:
    ```python
        # 创建 ConfigManager 实例并加载配置
        config_manager = ConfigManager(filepath='conf/conf.yaml')
        config = config_manager.get_config('f2')
        print(config)

        # 更新配置并保存
        config_manager.update_config_with_args('f2', new_key='new_value')
    ```
    """

    # 如果不传入应用配置路径，则返回项目配置 (If the application conf path is not passed in, the project conf is returned)
    def __init__(self, filepath: str = f2.F2_CONFIG_FILE_PATH):
        if Path(filepath).exists():
            self.filepath = Path(filepath)
        else:
            self.filepath = Path(get_resource_path(filepath))

        # 配置ruamel.yaml
        self.yaml = YAML()
        self.yaml.preserve_quotes = True  # 保留引号
        self.yaml.width = 160  # 行宽
        self.yaml.indent(mapping=2, sequence=4, offset=2)  # 设置缩进

        self.config = self.load_config()
        # 只有 F2 配置文件（conf.yaml）支持用户级覆盖，应用配置请用 -c 指定自定义配置文件
        self._overrides = (
            self._load_user_overrides() if filepath == f2.F2_CONFIG_FILE_PATH else {}
        )

    def _replace_none(self, data, default=""):
        """
        替换字典中的 None 值为默认值 (Replace None values in the dict with a default value)

        Args:
            data: dict | list: 配置数据 (Configuration data)
            default: any: 默认值 (Default value to replace None)

        Returns:
            dict | list: 处理后的数据 (Processed data)
        """
        if isinstance(data, dict):
            return {
                k: (default if v is None else self._replace_none(v, default))
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [
                (default if item is None else self._replace_none(item, default))
                for item in data
            ]
        return data

    def load_config(self) -> dict:
        """从文件中加载配置 (Load the conf from the file)"""

        if not self.filepath.exists():
            raise FileNotFound(_("配置文件不存在"), self.filepath)
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                config = self.yaml.load(file) or {}
        except PermissionError:
            raise FilePermissionError(_("配置文件路径无读权限"), self.filepath)
        except Exception as e:
            raise ConfError(
                _("配置文件解析错误: {0}").format(describe_yaml_error(e)),
                filepath=self.filepath,
            ) from e

        if not isinstance(config, dict):
            raise ConfError(_("配置文件的顶层不是键值映射"), filepath=self.filepath)
        # 遍历配置，替换 None 值为空字符串
        return self._replace_none(config)

    def get_config(self, app_name: str, default=None) -> dict:
        """
        从配置中获取给定键的值 (Get the value of the given key from the conf)

        Args:
            app_name: str: 应用名称 (app name)
            default: any: 默认值 (default value)

        Return:
            self.config.get 配置字典 (conf dict)
        """
        value = self.config.get(app_name, default)
        if app_name in self._overrides:
            # 叠加用户级配置，只影响返回值，不修改 self.config
            return deep_merge(value, self._overrides[app_name])
        return value

    def get_app_config(self, app_name: str) -> dict:
        """
        读取应用的配置段，缺少或不是键值映射时报错 (Get an app section, raising if it is missing or invalid)

        CLI 读取主配置与 -c 指定的自定义配置时使用，报错中给出配置文件的路径。

        Args:
            app_name: str: 应用名称 (app name)

        Return:
            dict: 应用的配置 (app conf)
        """
        value = self.get_config(app_name)
        # 缺少这一段时为 None，只写了 "douyin:" 时为空字符串
        if value in (None, "", {}):
            raise ConfError(
                _(
                    "配置文件中没有 {0} 应用的配置，可以用 --init-config 向该文件补充默认配置"
                ).format(app_name),
                filepath=self.filepath,
            )
        if not isinstance(value, dict):
            raise ConfError(
                _("配置文件中 {0} 应用的配置不是键值映射").format(app_name),
                filepath=self.filepath,
            )
        return value

    def _load_user_overrides(self) -> dict:
        """
        读取用户级 conf.yaml（#377），多个文件按优先级依次叠加

        只在 get_config 读取时合并，不写回 self.config，保存配置时也不会写进默认配置文件。
        """
        paths = user_config_paths(exclude=self.filepath)
        key = tuple(_file_signature(path) for path in paths)
        if key in _USER_OVERRIDES_CACHE:
            return _USER_OVERRIDES_CACHE[key]

        merged: Any = {}
        for path in paths:
            try:
                merged = deep_merge(merged, read_yaml_mapping(path))
            except FileNotFoundError:
                raise ConfError(
                    _("环境变量 {0} 指定的配置文件不存在").format(USER_CONFIG_ENV),
                    filepath=path,
                )
            except PermissionError:
                raise FilePermissionError(_("配置文件路径无读权限"), path)
            except NotAMappingError:
                raise ConfError(_("用户配置文件的顶层不是键值映射"), filepath=path)
            except Exception as e:
                raise ConfError(
                    _("用户配置文件无效：{0}").format(describe_yaml_error(e)),
                    filepath=path,
                ) from e
            logger.info(_("已加载用户配置：{0}").format(path))

        overrides = self._replace_none(merged)
        _USER_OVERRIDES_CACHE[key] = overrides
        return overrides

    def save_config(self, config: dict):
        """将配置保存到文件，保留原始格式和注释 (Save the conf to the file preserving original format and comments)

        Args:
            config: dict: 配置字典 (conf dict)
        """
        try:
            with open(self.filepath, "w", encoding="utf-8") as file:
                self.yaml.dump(config, file)
        except PermissionError:
            raise FilePermissionError(_("配置文件路径无写权限"), self.filepath)

    def exists(self):
        """检查配置文件是否存在"""
        return self.filepath.exists()

    def backup_config(self):
        """在进行更改前备份配置文件 (Backup the conf file before making changes)"""
        # 如果已经是备份文件，直接返回 (If it is already a backup file, return directly)
        if self.filepath.suffix == ".bak":
            return

        backup_path = self.filepath.with_suffix(".bak")
        if backup_path.exists():
            backup_path.unlink()  # 删除已经存在的备份文件 (Delete existing backup files)

        # 直接复制而不是重命名，保留原始文件
        import shutil

        shutil.copy2(self.filepath, backup_path)

    def generate_config(self, app_name: str, save_path: str):
        """
        生成应用配置文件，保留格式 (Generate an application-specific conf file with formatting)

        目标文件不存在时写入该应用的默认配置；已存在时只补充缺少的配置项，
        其他应用的配置、已有的值与注释都保持不变，修改前备份为同名 .bak 文件。
        """

        if not isinstance(app_name, str):
            return

        # 将save_path转换为Path对象，但使用新变量而不是重新赋值给参数
        save_path_obj = Path(save_path)

        # 如果save_path是相对路径，则将其转换为绝对路径
        if not save_path_obj.is_absolute():
            save_path_obj = Path.cwd() / save_path

        # 读取默认配置
        defaults_path = Path(get_resource_path(f2.F2_DEFAULTS_FILE_PATH))
        with open(defaults_path, "r", encoding="utf-8") as file:
            default_config = self.yaml.load(file) or {}

        if app_name not in default_config:
            click.echo(_("{0} 应用配置未找到").format(app_name))
            return
        default_app_config = default_config[app_name]

        if not save_path_obj.exists():
            # 确保目录存在，如果不存在则创建
            save_path_obj.parent.mkdir(parents=True, exist_ok=True)
            self._write_yaml(save_path_obj, {app_name: default_app_config})
            click.echo(
                _("{0} 应用配置文件生成成功，保存至 {1}").format(
                    app_name, save_path_obj
                )
            )
            return

        # 文件已存在：不再覆盖，只补充缺少的内容
        existing = self._load_existing_config(save_path_obj)
        current = existing.get(app_name)
        if isinstance(current, dict):
            added = merge_missing_keys(current, default_app_config)
            if added == 0:
                click.echo(
                    _("{0} 已包含 {1} 应用的全部配置项，无需修改").format(
                        save_path_obj, app_name
                    )
                )
                return
        else:
            existing[app_name] = copy.deepcopy(default_app_config)

        backup_path = save_path_obj.with_suffix(".bak")
        shutil.copy2(save_path_obj, backup_path)
        self._write_yaml(save_path_obj, existing)

        if isinstance(current, dict):
            click.echo(
                _("已向 {0} 补充 {1} 应用缺少的 {2} 个配置项，原文件备份为 {3}").format(
                    save_path_obj, app_name, added, backup_path
                )
            )
        else:
            click.echo(
                _("已在 {0} 中追加 {1} 应用的默认配置，原文件备份为 {2}").format(
                    save_path_obj, app_name, backup_path
                )
            )

    def _load_existing_config(self, path: Path) -> Any:
        """读取已存在的配置文件，无法解析或不是键值映射时报错且不做修改"""
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = self.yaml.load(file)
        except PermissionError:
            raise FilePermissionError(_("配置文件路径无读权限"), path)
        except Exception as e:
            raise ConfError(
                _("无法解析配置文件，未做任何修改：{0}").format(describe_yaml_error(e)),
                filepath=path,
            ) from e

        if data is None:
            return CommentedMap()
        if not isinstance(data, dict):
            raise ConfError(
                _("配置文件的顶层不是键值映射，未做任何修改"), filepath=path
            )
        return data

    def _write_yaml(self, path: Path, data: Any) -> None:
        """写入 YAML，保留格式与注释"""
        try:
            with open(path, "w", encoding="utf-8") as file:
                self.yaml.dump(data, file)
        except PermissionError:
            raise FilePermissionError(_("配置文件路径无写权限"), path)

    def update_config(self, app_name: str, app_config: dict):
        """更新配置项并保存

        Args:
            app_name: str: 应用名称
            app_config: dict: 应用配置
        """
        self.config[app_name] = app_config
        self.save_config(self.config)

    def update_config_with_args(self, app_name: str, **kwargs):
        """
        使用提供的参数更新配置 (Update the conf with the provided parameters)

        Args:
            app_name: str: 应用名称 (app name)
            kwargs: dict: 配置字典 (conf dict)
        """
        app_config = self.config.get(app_name, {})

        # 使用提供的参数更新特定应用的配置
        for key, value in kwargs.items():
            if key == "app_name":
                continue
            if value is not None:
                app_config[key] = value

        self.config[app_name] = app_config

        # 在保存前询问用户确认 (Ask the user for confirmation before saving)
        if click.confirm(
            _("是否要使用命令行的参数更新配置文件？")
            + (f"`{Path.cwd() / self.filepath}`"),
            default=True,
        ):
            # 备份原始配置文件
            self.backup_config()
            # 保存更新的配置 (Save the updated conf)
            self.save_config(self.config)
            click.echo(_("配置文件已更新!"))
        else:
            click.echo(_("已取消更新配置文件!"))


def get_f2_setting(key: str, default: Any = None) -> Any:
    """
    读取 conf.yaml 顶层 `f2` 段中的全局设置 (Read a global setting from the `f2` section of conf.yaml)

    Args:
        key: str: 设置名，例如 "verify"、"check_update"
        default: Any: 配置缺失时的默认值

    Returns:
        Any: 配置值，缺失时返回 default
    """
    return (ConfigManager(f2.F2_CONFIG_FILE_PATH).get_config("f2") or {}).get(
        key, default
    )


class TestConfigManager:
    """
    测试配置管理器 (Test Configuration Manager)

    读取 `conf/test.yaml` 中指定应用的测试配置。`test.yaml` 只保存用于测试的游客数据，
    且不会随 wheel 发布；需要使用个人 cookie 等敏感值时，按以下优先级覆盖（高的覆盖低的）：

    1. 环境变量 `F2_TEST_<APP>_<KEY>`，例如 `F2_TEST_DOUYIN_COOKIE`、`F2_TEST_BARK_KEY`。
    2. 与 `test.yaml` 同目录的 `test.local.yaml`（已加入 .gitignore，不会提交）。
    3. `conf/test.yaml` 中的默认值。

    类属性:
    - OVERRIDE_KEYS (tuple): 允许通过环境变量覆盖的字段。
    - LOCAL_CONFIG_FILE_NAME (str): 本地覆盖文件名。

    使用示例:
    ```python
        # F2_TEST_DOUYIN_COOKIE=... pytest f2/apps/douyin/test
        conf = TestConfigManager.get_test_config("douyin")
        crawler = DouyinCrawler(conf)
    ```
    """

    OVERRIDE_KEYS = ("cookie", "key", "token", "device_id")
    LOCAL_CONFIG_FILE_NAME = "test.local.yaml"

    @classmethod
    def _template_path(cls) -> Path:
        """返回 test.yaml 的绝对路径（不要求文件存在）"""
        template = Path(f2.TEST_CONFIG_FILE_PATH)
        if template.is_absolute():
            return template
        return Path(get_resource_path(f2.TEST_CONFIG_FILE_PATH))

    @classmethod
    def _load_app_config(cls, path: Path, app_name: str) -> dict:
        """读取指定文件中某个应用的配置，文件不存在时返回空字典"""
        if not path.exists():
            return {}
        return dict(ConfigManager(str(path)).get_config(app_name) or {})

    @classmethod
    def get_test_config(cls, app_name: str) -> dict:
        """
        获取指定应用的测试配置 (Get the test conf of the given app)

        Args:
            app_name: str: 应用名称 (app name)

        Returns:
            dict: 合并了 test.yaml、test.local.yaml 与环境变量后的配置
        """
        template_path = cls._template_path()
        config = cls._load_app_config(template_path, app_name)

        local_path = template_path.with_name(cls.LOCAL_CONFIG_FILE_NAME)
        config.update(cls._load_app_config(local_path, app_name))

        for key in cls.OVERRIDE_KEYS:
            value = os.environ.get(f"F2_TEST_{app_name.upper()}_{key.upper()}")
            if value:
                config[key] = value

        return config


if __name__ == "__main__":
    print(TestConfigManager.get_test_config("douyin"))

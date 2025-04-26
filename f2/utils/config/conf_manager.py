# path: f2/utils/config/conf_manager.py

from pathlib import Path

import click
from ruamel.yaml import YAML  # type: ignore[import-untyped]

import f2
from f2.exceptions.file_exceptions import (
    FileNotFound,
    FilePermissionError,
)
from f2.i18n.translator import _
from f2.utils.utils import get_resource_path


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
            # 遍历配置，替换 None 值为空字符串
            return self._replace_none(config)
        except PermissionError:
            raise FilePermissionError(_("配置文件路径无读权限"), self.filepath)
        except Exception as e:
            raise RuntimeError(_("配置文件解析错误: {0}").format(str(e))) from e

    def get_config(self, app_name: str, default=None) -> dict:
        """
        从配置中获取给定键的值 (Get the value of the given key from the conf)

        Args:
            app_name: str: 应用名称 (app name)
            default: any: 默认值 (default value)

        Return:
            self.config.get 配置字典 (conf dict)
        """
        return self.config.get(app_name, default)

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
        """生成应用程序特定配置文件，保留格式 (Generate application-specific conf file with formatting)"""

        if not isinstance(app_name, str):
            return

        # 将save_path转换为Path对象，但使用新变量而不是重新赋值给参数
        save_path_obj = Path(save_path)

        # 如果save_path是相对路径，则将其转换为绝对路径
        if not save_path_obj.is_absolute():
            save_path_obj = Path.cwd() / save_path

        # 确保目录存在，如果不存在则创建
        save_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # 读取默认配置
        defaults_path = Path(get_resource_path(f2.F2_DEFAULTS_FILE_PATH))

        try:
            with open(defaults_path, "r", encoding="utf-8") as file:
                default_config = self.yaml.load(file) or {}

            if app_name in default_config:
                # 将app_name作为外层键
                app_config = {app_name: default_config[app_name]}

                # 写入应用程序特定配置，保留格式
                with open(save_path_obj, "w", encoding="utf-8") as file:
                    self.yaml.dump(app_config, file)

                click.echo(
                    _("{0} 应用配置文件生成成功，保存至 {1}").format(
                        app_name, save_path_obj
                    )
                )
            else:
                click.echo(_("{0} 应用配置未找到").format(app_name))
        except Exception as e:
            raise RuntimeError(_("生成配置文件失败：{0}").format(str(e)))

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


class TestConfigManager:
    # 返回传入app的测试配置内容 (Return the test conf content passed in app)

    @classmethod
    def get_test_config(cls, app_name: str) -> dict:
        return ConfigManager(f2.TEST_CONFIG_FILE_PATH).get_config(app_name)


if __name__ == "__main__":
    print(TestConfigManager.get_test_config("douyin"))

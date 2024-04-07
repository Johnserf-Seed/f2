# path: f2/utils/conf_manager.py

import f2
import yaml
import click

from pathlib import Path
from f2.exceptions.file_exceptions import (
    FileNotFound,
    FilePermissionError,
)
from f2.utils.utils import get_resource_path
from f2.i18n.translator import _
from f2.log.logger import logger


class ConfigManager:
    # 如果不传入应用配置路径，则返回项目配置 (If the application conf path is not passed in, the project conf is returned)
    def __init__(self, filepath: str = f2.F2_CONFIG_FILE_PATH):
        if Path(filepath).exists():
            self.filepath = Path(filepath)
        else:
            self.filepath = Path(get_resource_path(filepath))
        self.config = self.load_config()

    def load_config(self) -> dict:
        """从文件中加载配置 (Load the conf from the file)"""

        if not self.filepath.exists():
            raise FileNotFound(_("配置文件不存在"), self.filepath)

        return yaml.safe_load(self.filepath.read_text(encoding="utf-8")) or {}

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
        """将配置保存到文件 (Save the conf to the file)
        Args:
            config: dict: 配置字典 (conf dict)
        """
        try:
            self.filepath.write_text(yaml.dump(config), encoding="utf-8")
        except PermissionError:
            raise FilePermissionError(_("配置文件路径无写权限"), self.filepath)

    def backup_config(self):
        """在进行更改前备份配置文件 (Backup the conf file before making changes)"""
        # 如果已经是备份文件，直接返回 (If it is already a backup file, return directly)
        if self.filepath.suffix == ".bak":
            return

        backup_path = self.filepath.with_suffix(".bak")
        if backup_path.exists():
            backup_path.unlink()  # 删除已经存在的备份文件 (Delete existing backup files)
        self.filepath.rename(backup_path)

    def generate_config(self, app_name: str, save_path: Path):
        """生成应用程序特定配置文件 (Generate application-specific conf file)"""

        if not isinstance(app_name, str):
            return

        # 将save_path转换为Path对象
        save_path = Path(save_path)

        # 如果save_path是相对路径，则将其转换为绝对路径
        if not save_path.is_absolute():
            save_path = Path.cwd() / save_path

        # 确保目录存在，如果不存在则创建
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取默认配置
        default_config = (
            yaml.safe_load(
                Path(get_resource_path(f2.F2_DEFAULTS_FILE_PATH)).read_text(
                    encoding="utf-8"
                )
            )
            or {}
        )

        if app_name in default_config:
            # 将app_name作为外层键 # https://github.com/Johnserf-Seed/TikTokDownload/issues/626  #629
            app_config = {app_name: default_config[app_name]}

            # 写入应用程序特定配置
            save_path.write_text(yaml.dump(app_config), encoding="utf-8")
            logger.info(
                _("{0} 应用配置文件生成成功，保存至 {1}").format(app_name, save_path)
            )
        else:
            logger.info(_("{0} 应用配置未找到").format(app_name))

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

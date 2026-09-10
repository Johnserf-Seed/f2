# path: f2/conf/config_wizard.py

import datetime
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text
from ruamel.yaml import YAML

import f2
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.file.path import get_resource_path


class ConfigWizard:
    """
    配置向导类，提供交互式配置文件生成功能
    """

    def __init__(self):
        self.console = Console()
        self.config_data = {}

        # 配置ruamel.yaml
        self.yaml = YAML()
        self.yaml.preserve_quotes = True  # 保留引号
        self.yaml.width = 160  # 行宽
        self.yaml.indent(mapping=2, sequence=4, offset=2)  # 设置缩进

        # 应用信息配置
        self.app_info = {
            "douyin": {
                "display_name": "抖音 (DouYin)",
                "description": "抖音短视频平台下载工具",
                "modes": [
                    "one",
                    "post",
                    "like",
                    "collection",
                    "collects",
                    "music",
                    "mix",
                    "live",
                    "related",
                    "friend",
                ],
                "required_fields": ["url", "mode", "cookie"],
                "optional_fields": [
                    "path",
                    "naming",
                    "folderize",
                    "timeout",
                    "max_retries",
                    "interval",
                ],
            },
            "tiktok": {
                "display_name": "TikTok",
                "description": "TikTok国际版短视频平台下载工具",
                "modes": [
                    "one",
                    "post",
                    "like",
                    "collect",
                    "mix",
                    "search",
                    "live",
                ],
                "required_fields": ["url", "mode", "cookie"],
                "optional_fields": [
                    "path",
                    "naming",
                    "folderize",
                    "timeout",
                    "max_retries",
                    "interval",
                ],
            },
            "weibo": {
                "display_name": "微博 (Weibo)",
                "description": "新浪微博社交平台下载工具",
                "modes": [
                    "one",
                    "post",
                ],
                "required_fields": ["url", "mode", "cookie"],
                "optional_fields": [
                    "path",
                    "naming",
                    "folderize",
                    "timeout",
                    "max_retries",
                    "interval",
                ],
            },
            "twitter": {
                "display_name": "Twitter (X)",
                "description": "Twitter社交平台下载工具",
                "modes": [
                    "one",
                    "post",
                    "like",
                    "bookmark",
                ],
                "required_fields": ["url", "mode", "cookie"],
                "optional_fields": [
                    "path",
                    "naming",
                    "folderize",
                    "timeout",
                    "max_retries",
                    "interval",
                ],
            },
        }

        # 配置项详细说明
        self.field_descriptions: Dict[str, Dict[str, Any]] = {
            "url": {
                "description": "目标链接",
                "prompt": "请输入要下载的链接",
                "example": "https://v.douyin.com/...",
                "type": "str",
            },
            "mode": {
                "description": "下载模式",
                "prompt": "选择下载模式",
                "type": "choice",
            },
            "cookie": {
                "description": "用户身份验证Cookie",
                "prompt": "请输入Cookie（可留空后续配置）",
                "example": "sessionid=...; csrftoken=...",
                "type": "choice",
                "required": False,
            },
            "path": {
                "description": "下载保存路径",
                "prompt": "请输入下载保存路径",
                "example": "Download",
                "default": "Download",
                "type": "choice",
            },
            "naming": {
                "description": "文件命名模板",
                "prompt": "请输入文件命名模板",
                "example": "{create}_{desc}",
                "type": "choice",
            },
            "folderize": {
                "description": "是否按用户创建文件夹",
                "prompt": "是否按用户创建文件夹",
                "default": True,
                "type": "bool",
            },
            "timeout": {
                "description": "请求超时时间（秒）",
                "prompt": "请输入请求超时时间",
                "default": 10,
                "type": "choice",
            },
            "max_retries": {
                "description": "最大重试次数",
                "prompt": "请输入最大重试次数",
                "default": 3,
                "type": "int",
            },
            "max_connections": {
                "description": "最大并发连接数",
                "prompt": "请输入最大并发连接数",
                "default": 5,
                "type": "int",
            },
            "max_counts": {
                "description": "最大下载数量",
                "prompt": "请输入最大下载数量（0表示不限制）",
                "default": 0,
                "type": "choice",
            },
            "interval": {
                "description": "下载日期区间",
                "prompt": "请输入下载日期区间",
                "example": "2025-01-01|2025-12-31",
                "default": "all",
                "type": "choice",
            },
        }

    def show_welcome(self):
        """显示欢迎界面"""
        welcome_text = Text("🎉 F2 配置向导", style="bold magenta")
        welcome_panel = Panel(
            welcome_text,
            title="欢迎使用",
            subtitle="让配置变得简单",
            border_style="magenta",
        )
        self.console.print(welcome_panel)
        self.console.print()

        intro_text = """
👋 欢迎使用 F2 配置向导！

本向导将帮助您：
• 选择要配置的应用平台
• 交互式设置各项参数
• 生成自定义配置文件
• 快速开始使用 F2

让我们开始吧！
        """
        self.console.print(intro_text.strip())
        self.console.print()

    def select_apps(self) -> List[str]:
        """选择要配置的应用"""
        self.console.print("📱 [bold cyan]选择要配置的应用平台[/bold cyan]")
        self.console.print()

        # 显示可用应用列表
        table = Table(title="可用平台")
        table.add_column("序号", style="cyan")
        table.add_column("平台", style="magenta")
        table.add_column("描述", style="green")

        apps = list(self.app_info.keys())
        for i, app in enumerate(apps, 1):
            info = self.app_info[app]
            table.add_row(str(i), str(info["display_name"]), str(info["description"]))

        self.console.print(table)
        self.console.print()

        # 用户选择
        while True:
            try:
                choice = Prompt.ask(
                    "请输入要配置的平台序号（多个平台用逗号分隔，如: 1,2）", default="1"
                )

                selected_indices = [int(x.strip()) for x in choice.split(",")]
                selected_apps = []

                for idx in selected_indices:
                    if 1 <= idx <= len(apps):
                        selected_apps.append(apps[idx - 1])
                    else:
                        self.console.print(f"❌ 无效选择: {idx}")
                        continue

                if selected_apps:
                    # 确认选择
                    selected_names: List[str] = [
                        str(self.app_info[app]["display_name"]) for app in selected_apps
                    ]
                    if Confirm.ask(f"确认配置以下平台: {', '.join(selected_names)}？"):
                        return selected_apps
                else:
                    self.console.print("❌ 请至少选择一个平台")

            except KeyboardInterrupt:
                # 重新抛出中断信号
                raise
            except ValueError:
                self.console.print("❌ 输入格式错误，请输入数字序号")
            except Exception as e:
                logger.debug(f"选择应用时出错: {e}")
                self.console.print("❌ 选择出错，请重试")

    def configure_app(self, app_name: str) -> Dict[str, Any]:
        """配置单个应用"""
        app_info = self.app_info[app_name]
        self.console.print()
        self.console.print(f"⚙️  [bold cyan]配置 {app_info['display_name']}[/bold cyan]")
        self.console.print()

        config = {}

        # 获取默认配置
        try:
            defaults_path = Path(get_resource_path(f2.F2_DEFAULTS_FILE_PATH))
            with open(defaults_path, "r", encoding="utf-8") as f:
                default_config = self.yaml.load(f) or {}
                app_defaults: Dict[str, Any] = default_config.get(app_name, {})
        except Exception:
            app_defaults = {}

        # 配置必需字段
        self.console.print("📋 [yellow]必需配置项[/yellow]")
        for field in app_info["required_fields"]:
            config[field] = self._configure_field(
                field, app_name, app_defaults.get(field)
            )

        # 询问是否配置可选字段
        self.console.print()
        if Confirm.ask("是否配置可选项（推荐）？", default=True):
            self.console.print("📋 [yellow]可选配置项[/yellow]")
            for field in app_info["optional_fields"]:
                if Confirm.ask(
                    f"配置 {field} ({self.field_descriptions.get(field, {}).get('description', field)})?"
                ):
                    config[field] = self._configure_field(
                        field, app_name, app_defaults.get(field)
                    )

        return config

    def _configure_field(
        self, field_name: str, app_name: str, default_value: Any = None
    ) -> Any:
        """配置单个字段"""
        try:
            field_info: Dict[str, Any] = self.field_descriptions.get(field_name, {})
            field_type = field_info.get("type", "str")
            description = field_info.get("description", field_name)
            prompt_text = field_info.get("prompt", f"请输入 {field_name}")
            example = field_info.get("example")
            default = field_info.get("default", default_value)

            # 显示字段说明
            self.console.print(f"  🔧 {description}")
            if example:
                self.console.print(f"     示例: [dim]{example}[/dim]")

            # 特殊处理不同类型的字段
            if field_name == "mode":
                return self._configure_mode(app_name)
            elif field_type == "bool":
                return Confirm.ask(f"     {prompt_text}", default=default)
            elif field_type == "int":
                return IntPrompt.ask(f"     {prompt_text}", default=default or 0)
            elif field_type == "choice":
                return self._configure_choice_field(field_name, app_name)
            else:  # str
                result = Prompt.ask(
                    f"     {prompt_text}", default=str(default) if default else ""
                )
                return result if result else None
        except KeyboardInterrupt:
            # 重新抛出中断信号
            raise
        except Exception as e:
            logger.debug(f"配置字段 {field_name} 时出错: {e}")
            # 返回默认值
            return default_value

    def _configure_mode(self, app_name: str) -> str:
        """配置下载模式"""
        modes = self.app_info[app_name]["modes"]
        try:
            self.console.print("     可用模式:")
            for i, mode in enumerate(modes, 1):
                mode_desc = self._get_mode_description(mode)
                self.console.print(f"       {i}. {mode} - {mode_desc}")

            while True:
                try:
                    choice = IntPrompt.ask("     请选择模式序号", default=1)
                    if 1 <= choice <= len(modes):
                        return modes[choice - 1]
                    else:
                        self.console.print(f"     ❌ 请输入 1-{len(modes)} 之间的数字")
                except KeyboardInterrupt:
                    # 重新抛出中断信号
                    raise
                except Exception:
                    self.console.print("     ❌ 请输入有效的数字")
        except KeyboardInterrupt:
            # 重新抛出中断信号
            raise
        except Exception as e:
            logger.debug(f"配置模式时出错: {e}")
            # 返回第一个模式作为默认值
            return modes[0] if modes else "post"

    def _get_mode_description(self, mode: str) -> str:
        """获取模式描述"""
        descriptions = {
            "post": "用户主页作品",
            "like": "用户点赞作品",
            "live": "直播相关",
            "music": "用户收藏音乐",
            "one": "单个作品详情",
            "feed": "推荐内容",
            "friend": "好友作品",
            "collection": "收藏作品",
            "collects": "收藏夹作品",
            "mix": "合集列表作品",
            # tk
            "collect": "收藏夹作品",
            # x
            "bookmark": "用户书签推文",
        }
        return descriptions.get(mode, mode)

    def _configure_choice_field(self, field_name: str, app_name: str) -> Any:
        """配置选择类型字段"""
        try:
            field_info: Dict[str, Any] = self.field_descriptions.get(field_name, {})

            # 根据不同字段提供特定的选择逻辑
            if field_name == "naming":
                return self._configure_naming_template(app_name)
            elif field_name == "path":
                return self._configure_path_field(app_name)
            elif field_name == "cookie":
                return self._configure_cookie_field(app_name)
            elif field_name == "max_counts":
                return self._configure_max_counts_field(app_name)
            elif field_name == "timeout":
                return self._configure_timeout_field(app_name)
            elif field_name == "interval":
                return self._configure_interval_field(app_name)
            else:
                # 默认的文本输入
                prompt_text = field_info.get("prompt", f"请输入 {field_name}")
                example = field_info.get("example")

                if example:
                    return Prompt.ask(f"     {prompt_text} (示例: {example})")
                else:
                    return Prompt.ask(f"     {prompt_text}")
        except KeyboardInterrupt:
            # 重新抛出中断信号
            raise
        except Exception as e:
            logger.debug(f"配置选择字段 {field_name} 时出错: {e}")
            # 返回默认值 - 创建一个安全的默认字典
            field_info_safe: Dict[str, Any] = self.field_descriptions.get(
                field_name, {}
            )
            return field_info_safe.get("default", "")

    def _configure_naming_template(self, app_name: str) -> str:
        """配置文件命名模板"""
        self.console.print("     可用命名模板:")

        # 根据不同平台提供不同的命名模板选项
        templates = {
            "douyin": [
                ("{create}_{desc}", "创建时间_作品文案"),
                ("{nickname}_{create}_{desc}", "用户昵称_创建时间_作品文案"),
                ("{aweme_id}_{desc}", "作品ID_作品文案"),
                ("{create}_{aweme_id}", "创建时间_作品ID"),
                ("custom", "自定义模板"),
            ],
            "tiktok": [
                ("{create}_{desc}", "创建时间_作品文案"),
                ("{nickname}_{create}", "用户昵称_创建时间"),
                ("{aweme_id}_{nickname}", "作品ID_用户昵称"),
                ("{create}_{aweme_id}", "创建时间_作品ID"),
                ("custom", "自定义模板"),
            ],
            "weibo": [
                ("{create}_{desc}", "创建时间_微博文案"),
                ("{nickname}_{create}", "用户名_创建时间"),
                ("{weibo_id}_{desc}", "微博ID_微博文案"),
                ("custom", "自定义模板"),
            ],
            "twitter": [
                ("{create}_{desc}", "创建时间_推文文案"),
                ("{user_name}_{create}", "用户名_创建时间"),
                ("{tweet_id}_{desc}", "推文ID_推文文案"),
                ("custom", "自定义模板"),
            ],
        }

        app_templates = templates.get(app_name, templates["douyin"])

        for i, (template, desc) in enumerate(app_templates, 1):
            self.console.print(f"       {i}. {template} - {desc}")

        while True:
            try:
                choice = IntPrompt.ask("     请选择命名模板序号", default=1)
                if 1 <= choice <= len(app_templates):
                    selected_template, _ = app_templates[choice - 1]
                    if selected_template == "custom":
                        custom_template = Prompt.ask("     请输入自定义命名模板")
                        # 如果用户输入为空，使用默认模板
                        if not custom_template or custom_template.strip() == "":
                            default_template = app_templates[0][
                                0
                            ]  # 使用第一个模板作为默认
                            self.console.print(
                                f"     💡 提示: 使用默认模板 '{default_template}'"
                            )
                            return default_template
                        return custom_template.strip()
                    else:
                        return selected_template
                else:
                    self.console.print(
                        f"     ❌ 请输入 1-{len(app_templates)} 之间的数字"
                    )
            except Exception:
                self.console.print("     ❌ 请输入有效的数字")

    def _configure_path_field(self, app_name: str) -> str:
        """配置下载路径"""
        self.console.print("     常用路径选项:")

        common_paths = [
            (".", "当前目录"),
            ("Download", "Download文件夹"),
            (f"Download/{app_name.title()}", f"Download/{app_name.title()}文件夹"),
            ("~/Downloads", "用户下载文件夹"),
            ("D:/Downloads", "D盘下载文件夹"),
            ("custom", "自定义路径"),
        ]

        for i, (path, desc) in enumerate(common_paths, 1):
            self.console.print(f"       {i}. {path} - {desc}")

        while True:
            try:
                choice = IntPrompt.ask(
                    "     请选择路径选项", default=2
                )  # 默认选择Download
                if 1 <= choice <= len(common_paths):
                    selected_path, _ = common_paths[choice - 1]
                    if selected_path == "custom":
                        custom_path = Prompt.ask("     请输入自定义路径")
                        # 如果用户输入为空，使用默认路径
                        if not custom_path or custom_path.strip() == "":
                            self.console.print("     💡 提示: 使用默认路径 'Download'")
                            return "Download"
                        return custom_path.strip()
                    else:
                        return selected_path
                else:
                    self.console.print(
                        f"     ❌ 请输入 1-{len(common_paths)} 之间的数字"
                    )
            except Exception:
                self.console.print("     ❌ 请输入有效的数字")

    def _configure_cookie_field(self, app_name: str) -> str:
        """配置Cookie字段"""
        self.console.print("     Cookie配置选项:")
        self.console.print("       1. 暂时跳过（后续手动配置）")
        self.console.print("       2. 从浏览器复制Cookie")
        self.console.print("       3. 从文件读取Cookie")

        while True:
            try:
                choice = IntPrompt.ask("     请选择Cookie配置方式", default=1)
                if choice == 1:
                    self.console.print("     💡 提示: 可在配置文件中手动添加Cookie")
                    return ""
                elif choice == 2:
                    self.console.print("     📋 请从浏览器开发者工具中复制Cookie:")
                    self.console.print(f"        1. 打开 {app_name} 网页")
                    self.console.print("        2. 按F12打开开发者工具")
                    self.console.print("        3. 在Network标签中找到请求")
                    self.console.print("        4. 复制Cookie字段的值")
                    return Prompt.ask("     请粘贴Cookie", default="")
                elif choice == 3:
                    file_path = Prompt.ask("     请输入Cookie文件路径")
                    # 如果用户输入为空，返回空字符串
                    if not file_path or file_path.strip() == "":
                        self.console.print("     💡 提示: 已跳过Cookie配置")
                        return ""

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            cookie_content = f.read().strip()
                        self.console.print(
                            f"     ✅ 已读取Cookie文件: {len(cookie_content)} 字符"
                        )
                        return cookie_content
                    except FileNotFoundError:
                        self.console.print(f"     ❌ 文件不存在: {file_path}")
                        continue
                    except PermissionError:
                        self.console.print(f"     ❌ 没有权限读取文件: {file_path}")
                        continue
                    except Exception as e:
                        self.console.print(f"     ❌ 读取文件失败: {e}")
                        continue
                else:
                    self.console.print("     ❌ 请输入 1-3 之间的数字")
            except Exception:
                self.console.print("     ❌ 请输入有效的数字")

    def _configure_max_counts_field(self, app_name: str) -> int:
        """配置最大下载数量"""
        self.console.print("     下载数量选项:")

        count_options = [
            (0, "不限制数量"),
            (10, "10个作品"),
            (50, "50个作品"),
            (100, "100个作品"),
            (500, "500个作品"),
            (-1, "自定义数量"),
        ]

        for i, (count, desc) in enumerate(count_options, 1):
            self.console.print(f"       {i}. {desc}")

        while True:
            try:
                choice = IntPrompt.ask("     请选择下载数量", default=1)
                if 1 <= choice <= len(count_options):
                    selected_count, _ = count_options[choice - 1]
                    if selected_count == -1:
                        return IntPrompt.ask("     请输入自定义数量", default=0)
                    else:
                        return selected_count
                else:
                    self.console.print(
                        f"     ❌ 请输入 1-{len(count_options)} 之间的数字"
                    )
            except Exception:
                self.console.print("     ❌ 请输入有效的数字")

    def _configure_timeout_field(self, app_name: str) -> int:
        """配置超时时间"""
        self.console.print("     超时时间选项:")

        timeout_options = [
            (5, "5秒 (较快网络)"),
            (10, "10秒 (推荐)"),
            (30, "30秒 (慢速网络)"),
            (60, "60秒 (很慢网络)"),
            (-1, "自定义时间"),
        ]

        for i, (timeout, desc) in enumerate(timeout_options, 1):
            self.console.print(f"       {i}. {desc}")

        while True:
            try:
                choice = IntPrompt.ask("     请选择超时时间", default=2)  # 默认10秒
                if 1 <= choice <= len(timeout_options):
                    selected_timeout, _ = timeout_options[choice - 1]
                    if selected_timeout == -1:
                        return IntPrompt.ask(
                            "     请输入自定义超时时间(秒)", default=10
                        )
                    else:
                        return selected_timeout
                else:
                    self.console.print(
                        f"     ❌ 请输入 1-{len(timeout_options)} 之间的数字"
                    )
            except Exception:
                self.console.print("     ❌ 请输入有效的数字")

    def _configure_interval_field(self, app_name: str) -> str:
        """配置日期区间字段"""
        self.console.print("     日期区间选项:")

        interval_options = [
            ("all", "下载所有作品"),
            ("2025-01-01|2025-12-31", "2025年全年"),
            ("2024-01-01|2024-12-31", "2024年全年"),
            ("recent_month", "最近一个月"),
            ("recent_week", "最近一周"),
            ("custom", "自定义日期区间"),
        ]

        for i, (interval, desc) in enumerate(interval_options, 1):
            self.console.print(f"       {i}. {interval} - {desc}")

        while True:
            try:
                choice = IntPrompt.ask("     请选择日期区间", default=1)
                if 1 <= choice <= len(interval_options):
                    selected_interval, _ = interval_options[choice - 1]
                    if selected_interval == "custom":
                        self.console.print(
                            "     请输入日期区间格式: YYYY-MM-DD|YYYY-MM-DD"
                        )
                        self.console.print("     示例: 2025-01-01|2025-12-31")
                        custom_interval = Prompt.ask(
                            "     请输入自定义日期区间", default=""
                        )

                        # 如果用户输入为空，返回"all"
                        if not custom_interval or custom_interval.strip() == "":
                            self.console.print(
                                "     💡 提示: 使用默认值 'all' (下载所有作品)"
                            )
                            return "all"

                        custom_interval = custom_interval.strip()
                        # 简单验证日期格式
                        if (
                            "|" in custom_interval
                            and len(custom_interval.split("|")) == 2
                        ):
                            start_date, end_date = custom_interval.split("|")
                            try:
                                # 验证日期格式
                                datetime.datetime.strptime(
                                    start_date.strip(), "%Y-%m-%d"
                                )
                                datetime.datetime.strptime(end_date.strip(), "%Y-%m-%d")
                                return custom_interval
                            except ValueError:
                                self.console.print(
                                    "     ❌ 日期格式错误，请使用 YYYY-MM-DD 格式"
                                )
                                continue
                        else:
                            self.console.print(
                                "     ❌ 格式错误，请使用 开始日期|结束日期 格式"
                            )
                            continue
                    elif selected_interval == "recent_month":
                        # 计算最近一个月的日期区间
                        current_date = datetime.datetime.now()
                        month_ago_date = current_date - datetime.timedelta(days=30)
                        return f"{month_ago_date.strftime('%Y-%m-%d')}|{current_date.strftime('%Y-%m-%d')}"
                    elif selected_interval == "recent_week":
                        # 计算最近一周的日期区间
                        current_date = datetime.datetime.now()
                        week_ago_date = current_date - datetime.timedelta(days=7)
                        return f"{week_ago_date.strftime('%Y-%m-%d')}|{current_date.strftime('%Y-%m-%d')}"
                    else:
                        return selected_interval
                else:
                    self.console.print(
                        f"     ❌ 请输入 1-{len(interval_options)} 之间的数字"
                    )
            except Exception:
                self.console.print("     ❌ 请输入有效的数字")

    def preview_config(self, config_data: Dict[str, Dict]) -> bool:
        """预览配置并确认"""
        self.console.print()
        self.console.print("📋 [bold cyan]配置预览[/bold cyan]")
        self.console.print()

        for app_name, app_config in config_data.items():
            app_display_name = self.app_info[app_name]["display_name"]

            panel_content = ""
            for key, value in app_config.items():
                if value is not None and value != "":
                    panel_content += f"{key}: {value}\n"

            panel = Panel(
                panel_content.strip(),
                title=f"[bold]{app_display_name}[/bold]",
                border_style="green",
            )
            self.console.print(panel)

        self.console.print()
        return Confirm.ask("确认以上配置？", default=True)

    def save_config(self, config_data: Dict[str, Dict], output_path: str):
        """保存配置文件"""
        try:
            output_path_obj = Path(output_path)

            # 确保输出目录存在
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # 添加配置文件注释
            commented_config = self._add_config_comments(config_data)

            # 写入配置文件
            with open(output_path_obj, "w", encoding="utf-8") as f:
                # 添加文件头注释
                f.write("# F2 配置文件\n")
                f.write("# 由配置向导生成，包含详细的配置说明\n")
                f.write("# 更多信息请访问: https://f2.wiki/\n\n")

                # 写入配置数据
                self.yaml.dump(commented_config, f)

            self.console.print()
            self.console.print(
                f"✅ [bold green]配置文件已保存至: {output_path_obj.absolute()}[/bold green]"
            )

            # 显示使用提示
            self.console.print()
            self.console.print("🚀 [bold cyan]使用方法[/bold cyan]")
            for app_name in config_data.keys():
                self.console.print(f"   f2 {app_name} -c {output_path}")

            return True

        except Exception as e:
            self.console.print(f"❌ [bold red]保存配置文件失败: {e}[/bold red]")
            return False

    def _add_config_comments(self, config_data: Dict[str, Dict]) -> Dict:
        """为配置添加注释"""
        # 由于ruamel.yaml的注释功能比较复杂，这里先返回原始数据
        # 后续可以扩展添加inline注释的功能
        return config_data

    def run(self) -> bool:
        """运行配置向导"""
        try:
            # 显示欢迎界面
            self.show_welcome()

            # 选择应用
            selected_apps = self.select_apps()

            # 配置每个应用
            config_data = {}
            for app_name in selected_apps:
                app_config = self.configure_app(app_name)
                config_data[app_name] = app_config

            # 预览配置
            if not self.preview_config(config_data):
                if Confirm.ask("是否重新配置？"):
                    return self.run()  # 递归重新开始
                else:
                    self.console.print("❌ 配置已取消")
                    return False

            # 询问保存路径
            self.console.print()
            default_filename = f"f2_config_{len(selected_apps)}apps.yaml"
            output_path = Prompt.ask("请输入配置文件保存路径", default=default_filename)

            # 保存配置
            return self.save_config(config_data, output_path)

        except KeyboardInterrupt:
            # 优雅处理用户中断
            print("\n")
            print("❌ 配置已取消")
            return False
        except EOFError:
            # 处理EOF错误（比如在管道中运行时）
            print("\n")
            print("❌ 配置已中断")
            return False
        except Exception as e:
            # 简化错误信息，只记录详细日志
            print("\n")
            print("❌ 配置向导出现错误")
            logger.debug(f"配置向导异常详情: {e}")
            trace_logger.error(f"配置向导异常: {traceback.format_exc()}")
            return False


@click.command()
@click.option("--output", "-o", help=_("输出配置文件路径"))
def config_wizard(output: Optional[str]):
    """
    🧙‍♂️ 配置向导 - 交互式生成F2配置文件
    """
    try:
        wizard = ConfigWizard()

        if output:
            # 如果指定了输出路径，直接使用
            print(f"📁 配置文件将保存至: {output}")

        success = wizard.run()

        if success:
            print()
            print("🎉 配置完成！享受使用 F2 吧！")
        else:
            # 配置未完成，静默退出
            raise click.Abort()

    except KeyboardInterrupt:
        print("\n❌ 配置已取消")
        raise click.Abort()
    except click.Abort:
        # 重新抛出 Abort 异常，让 Click 处理
        raise
    except Exception as e:
        # 简化错误信息
        logger.debug(f"配置向导出现异常: {e}")
        print("❌ 配置向导出现错误，请重试")
        raise click.Abort()


if __name__ == "__main__":
    config_wizard()

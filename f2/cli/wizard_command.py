# path: f2/cli/wizard_command.py

from typing import Optional

import click

from f2.conf.config_wizard import ConfigWizard
from f2.i18n.translator import _


@click.command("config-wizard")
@click.option("--output", "-o", help=_("输出配置文件路径"), metavar="PATH")
@click.option("--app", "-a", help=_("指定要配置的应用（可选）"), metavar="APP_NAME")
def config_wizard_command(output: Optional[str], app: Optional[str]) -> None:
    """
    🧙‍♂️ 配置向导 - 交互式生成F2配置文件

    这个命令将引导您通过交互式界面创建F2配置文件，
    类似于 pnpm create 或 npm init 的体验。

    Args:
        output (Optional[str]): 输出配置文件的路径。如果未指定，将使用默认路径。
        app (Optional[str]): 指定要配置的应用名称。如果未指定，将配置所有支持的应用。

    示例:
        f2 config-wizard                    # 启动交互式配置向导
        f2 config-wizard -o my_config.yaml  # 指定输出文件
        f2 config-wizard -a douyin          # 只配置抖音应用
    """
    try:
        wizard = ConfigWizard()

        if output:
            print(f"📁 配置文件将保存至: {output}")

        if app:
            print(f"🎯 将配置应用: {app}")
            # 这里可以预设应用选择

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
    except Exception:
        # 简化错误信息
        print("❌ 配置向导出现错误，请重试")
        raise click.Abort()

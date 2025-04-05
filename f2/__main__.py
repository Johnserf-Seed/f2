# path: f2/__main__.py

from f2.cli.cli_commands import main
from f2.i18n.translator import TranslationManager

# 在启动CLI前初始化翻译管理器
TranslationManager.get_instance()

# 运行主程序
main()

# path: tests/test_i18n.py

from f2.i18n.translator import TranslationManager, _


# 使用 Pytest 测试装饰器标记测试函数
def test_translation():
    # 设置语言为英文
    TranslationManager.get_instance().set_language("en_US")
    assert _("Hello, World!") == "Hello, World!"

    # 设置语言为中文
    TranslationManager.get_instance().set_language("zh_CN")
    assert _("Hello, World!") == "你好，世界！"

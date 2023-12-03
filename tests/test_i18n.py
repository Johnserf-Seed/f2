from f2.i18n.translator import TranslationManager
from f2.i18n.translator import _


def test_translation():
    # 设置语言为英文
    TranslationManager.get_instance().set_language("en_US")
    assert _("Hello, World!") == "Hello, World!"

    # 设置语言为中文
    TranslationManager.get_instance().set_language("zh_CN")
    assert _("Hello, World!") == "你好，世界！"

    print("All tests passed!")


test_translation()

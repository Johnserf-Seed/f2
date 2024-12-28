# path: f2/i18n/translator.py

import gettext
import pathlib


class TranslationManager:
    """
    翻译管理器 (Translation Manager)

    该类提供了一个单例模式的翻译管理器，用于加载和获取不同语言的翻译文本。它支持根据指定语言加载翻译文件，并提供获取翻译文本的功能。

    类属性:
    - _instance (TranslationManager): 翻译管理器的单例实例。
    - translations (dict): 存储已加载的翻译文本。
    - lang (str): 当前语言，默认为 "zh_CN"。

    类方法:
    - get_instance: 获取翻译管理器的单例实例，如果实例不存在则创建新的实例。
    - __init__: 初始化翻译管理器，设置默认语言为 "zh_CN"。
    - load_translations: 加载指定语言的翻译文件。如果语言未加载，则尝试加载对应语言的翻译。
    - set_language: 设置当前语言并加载该语言的翻译文件。
    - gettext: 获取指定消息的翻译文本。如果翻译不存在，则返回原始消息。

    异常处理:
    - 该类在加载翻译文件时，如果文件未找到，会将该语言的翻译设置为 None，并避免程序崩溃。

    使用示例:
    ```python
        # 获取翻译管理器的单例实例
        translation_manager = TranslationManager.get_instance()

        # 设置语言为英语
        translation_manager.set_language('en_US')

        # 获取翻译文本
        translated_message = translation_manager.gettext('Hello, world!')
    ```
    """

    _instance = None

    @staticmethod
    def get_instance():
        if TranslationManager._instance is None:
            TranslationManager._instance = TranslationManager()
        return TranslationManager._instance

    def __init__(self):
        self.translations = {}
        self.lang = "zh_CN"  # 默认语言

    def load_translations(self, lang=None):
        if not lang:
            lang = self.lang

        if lang not in self.translations:
            try:
                translation = gettext.translation(
                    lang,
                    localedir=pathlib.Path(__file__).parents[1] / "languages",
                    languages=[lang],
                )
                self.translations[lang] = translation.gettext
            except FileNotFoundError:
                self.translations[lang] = None

        return self.translations[lang]

    def set_language(self, lang):
        self.lang = lang
        self.load_translations(lang)

    def gettext(self, message):
        _ = self.load_translations()
        if _:
            return _(message)
        return message


_ = TranslationManager.get_instance().gettext

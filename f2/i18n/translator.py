# path: f2/i18n/translator.py

import gettext
from f2.utils.utils import get_resource_path


class TranslationManager:
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
                    lang, get_resource_path("languages/"), languages=[lang]
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

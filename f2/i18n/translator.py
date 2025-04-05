# path: f2/i18n/translator.py

import gettext
import locale
import os
import pathlib

from ruamel.yaml import YAML

import f2


class TranslationManager:
    """
    翻译管理器 (Translation Manager)

    该类提供了一个单例模式的翻译管理器，用于加载和获取不同语言的翻译文本。它支持根据指定语言加载翻译文件，并提供获取翻译文本的功能。
    支持从配置文件加载语言设置，自动检测系统语言，以及语言回退机制。

    类属性:
    - _instance (TranslationManager): 翻译管理器的单例实例。
    - translations (dict): 存储已加载的翻译文本。
    - lang (str): 当前语言，默认为 "zh_CN"。
    - config (dict): 存储配置文件的信息，包括语言设置、默认语言、语言路径等。
    - yaml (YAML): ruamel.yaml实例，用于处理YAML配置文件，保留格式和注释。

    类方法:
    - get_instance: 获取翻译管理器的单例实例，如果实例不存在则创建新的实例。
    - __init__: 初始化翻译管理器，加载配置并设置初始语言。
    - _load_config: 使用ruamel.yaml从conf.yaml加载i18n配置。
    - _detect_system_language: 检测系统语言，优先从环境变量获取，然后尝试匹配支持的语言。
    - _determine_language: 确定要使用的语言，优先使用配置中的设置，其次自动检测。
    - load_translations: 加载指定语言的翻译文件。如果语言未加载或不支持，尝试使用fallback语言。
    - set_language: 设置当前语言并加载该语言的翻译文件，同时更新配置文件，保留原始格式和注释。
    - gettext: 获取指定消息的翻译文本。如果翻译不存在，则返回原始消息。

    配置功能:
    - 支持从conf.yaml读取语言设置
    - 支持自动语言检测(default_language=auto)
    - 支持语言回退机制(fallback_language)
    - 支持自定义语言文件路径(language_path)
    - 支持配置可用语言列表(supported_languages)

    异常处理:
    - 该类在加载翻译文件时，如果文件未找到，会尝试使用fallback语言
    - 如果fallback语言也失败，会将翻译函数设为原样返回
    - 配置文件读取失败时使用默认值
    - 语言设置保存失败只在内存中更新

    使用示例:
    ```python
        # 获取翻译管理器的单例实例
        translation_manager = TranslationManager.get_instance()

        # 设置语言为英语(会保存到配置文件)
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
        # 初始化YAML解析器
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.width = 160
        self.yaml.indent(mapping=2, sequence=4, offset=2)

        # 加载配置并确定初始语言
        self.config = self._load_config()
        self.lang = self._determine_language()
        self.load_translations(self.lang)

    def _load_config(self):
        """使用ruamel.yaml加载i18n配置"""
        try:
            conf_path = pathlib.Path(__file__).parents[1] / "conf" / "conf.yaml"

            if conf_path.exists():
                with open(conf_path, "r", encoding="utf-8") as file:
                    config = self.yaml.load(file)
                    if config and "f2" in config and "i18n" in config["f2"]:
                        return config["f2"]["i18n"]
        except Exception:
            pass

        # 如果配置加载失败，使用默认值
        return {
            "language": "zh_CN",
            "default_language": "auto",
            "fallback_language": "en_US",
            "language_path": "languages",
            "supported_languages": ["zh_CN", "en_US"],
        }

    def _detect_system_language(self):
        """检测系统语言"""
        try:
            # 尝试从环境变量获取语言设置
            env_lang = (
                os.environ.get("LANGUAGE")
                or os.environ.get("LC_ALL")
                or os.environ.get("LC_MESSAGES")
                or os.environ.get("LANG")
            )

            if env_lang:
                system_lang = env_lang.split(":")[0].replace("-", "_").split(".")[0]
            else:
                # 使用locale模块获取系统语言
                system_lang = locale.getdefaultlocale()[0]

            if not system_lang:
                # 默认语言设置
                return self.config.get("fallback_language", "en_US")

            # 检查是否支持此语言
            supported_languages = self.config.get(
                "supported_languages", ["zh_CN", "en_US"]
            )
            if system_lang in supported_languages:
                return system_lang

            # 尝试匹配语言的基础部分（如zh_TW匹配zh_CN）
            base_lang = system_lang.split("_")[0]
            for supported_lang in supported_languages:
                if supported_lang.startswith(base_lang + "_"):
                    return supported_lang

            # 如果没有匹配，使用fallback语言
            return self.config.get("fallback_language", "en_US")
        except Exception:
            # 出错时使用fallback语言
            return self.config.get("fallback_language", "en_US")

    def _determine_language(self):
        """确定要使用的语言"""
        # 首先检查配置中指定的语言
        configured_lang = self.config.get("language")

        # 如果配置为auto或未设置，检测系统语言
        if not configured_lang or configured_lang == "auto":
            return self._detect_system_language()

        # 验证语言是否被支持
        if configured_lang in self.config.get(
            "supported_languages", ["zh_CN", "en_US"]
        ):
            return configured_lang

        # 如果配置的语言不支持，使用fallback
        return self.config.get("fallback_language", "en_US")

    def load_translations(self, lang=None):
        """加载指定语言的翻译"""
        if not lang:
            lang = self.lang

        if lang not in self.translations:
            # 验证语言是否被支持
            supported_languages = self.config.get(
                "supported_languages", ["zh_CN", "en_US"]
            )
            if lang not in supported_languages:
                # 不支持时使用fallback
                lang = self.config.get("fallback_language", "en_US")

            try:
                # 从配置的路径加载语言文件
                language_path = self.config.get("language_path", "languages")
                localedir = pathlib.Path(__file__).parents[1] / language_path

                translation = gettext.translation(
                    lang,
                    localedir=localedir,
                    languages=[lang],
                )
                self.translations[lang] = translation.gettext
            except FileNotFoundError:
                # 尝试使用fallback语言
                fallback_lang = self.config.get("fallback_language", "en_US")
                if lang != fallback_lang:
                    return self.load_translations(fallback_lang)
                else:
                    # 如果fallback也失败，不翻译
                    self.translations[lang] = lambda x: x

        return self.translations[lang]

    def set_language(self, lang):
        """设置语言并使用ruamel.yaml保存到配置文件，保留原始格式和注释"""
        # 验证语言是否被支持
        supported_languages = self.config.get("supported_languages", ["zh_CN", "en_US"])
        if lang not in supported_languages:
            raise ValueError(f"不支持的语言: {lang}")

        # 更新当前实例的语言
        self.lang = lang
        self.load_translations(lang)

        # 同时更新内存中的配置
        self.config["language"] = lang

        # 保存到配置文件
        try:
            conf_path = pathlib.Path(__file__).parents[1] / f2.F2_CONFIG_FILE_PATH

            if conf_path.exists():
                # 使用ruamel.yaml读取配置，保留所有格式和注释
                with open(conf_path, "r", encoding="utf-8") as file:
                    config = self.yaml.load(file)

                # 更新语言设置
                if config and "f2" in config:
                    if "i18n" not in config["f2"]:
                        config["f2"]["i18n"] = {}

                    config["f2"]["i18n"]["language"] = lang

                    # 使用ruamel.yaml写回配置
                    with open(conf_path, "w", encoding="utf-8") as file:
                        self.yaml.dump(config, file)
        except Exception:
            # 如果保存失败，仅在内存中更新
            pass

    def gettext(self, message):
        """获取翻译文本"""
        _ = self.load_translations()
        if _:
            return _(message)
        return message


_ = TranslationManager.get_instance().gettext

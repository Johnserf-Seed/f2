# path: tests/test_i18n.py

from pathlib import Path

from ruamel.yaml import YAML  # type: ignore[import-untyped]

import f2
from f2.i18n.translator import TranslationManager, _

REAL_CONF = Path(f2.__file__).parent / f2.F2_CONFIG_FILE_PATH


def saved_language(path):
    return YAML(typ="safe").load(path.read_text(encoding="utf-8"))["f2"]["i18n"][
        "language"
    ]


# 使用 Pytest 测试装饰器标记测试函数
def test_translation(monkeypatch, tmp_path):
    # set_language 会把语言写回配置文件，这里让它写副本，不改动包内的 conf.yaml
    conf = tmp_path / "conf.yaml"
    original = REAL_CONF.read_bytes()
    conf.write_bytes(original)
    monkeypatch.setattr(f2, "F2_CONFIG_FILE_PATH", str(conf))

    # 设置语言为英文
    TranslationManager.get_instance().set_language("en_US")
    assert _("Hello, World!") == "Hello, World!"
    assert saved_language(conf) == "en_US"

    # 设置语言为中文
    TranslationManager.get_instance().set_language("zh_CN")
    assert _("Hello, World!") == "你好，世界！"
    assert saved_language(conf) == "zh_CN"
    assert REAL_CONF.read_bytes() == original

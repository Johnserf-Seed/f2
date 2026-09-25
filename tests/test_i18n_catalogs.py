# path: tests/test_i18n_catalogs.py

from pathlib import Path

import pytest
from babel.messages.mofile import read_mo
from babel.messages.pofile import read_po

LANGUAGES_DIR = Path(__file__).resolve().parents[1] / "f2" / "languages"


@pytest.mark.parametrize("locale", ["en_US", "zh_CN"])
def test_mo_is_compiled_from_po(locale):
    """.po 是翻译源文件，.mo 必须由它编译而来，只改其中一个时这里会失败"""
    messages_dir = LANGUAGES_DIR / locale / "LC_MESSAGES"
    with open(messages_dir / f"{locale}.po", "rb") as fh:
        po = read_po(fh)
    with open(messages_dir / f"{locale}.mo", "rb") as fh:
        mo = read_mo(fh)

    # .mo 只包含已翻译且不是模糊匹配的条目
    expected = {m.id: m.string for m in po if m.id and m.string and not m.fuzzy}
    actual = {m.id: m.string for m in mo if m.id}
    assert actual == expected, "请运行 make_pot 脚本，由 .po 重新编译 .mo"

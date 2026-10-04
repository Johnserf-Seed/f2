# path: tests/test_i18n.py

from pathlib import Path

import pytest
from click.testing import CliRunner

import f2
from f2.cli.cli_commands import main
from f2.i18n.translator import TranslationManager, _

REAL_CONF = Path(f2.__file__).parent / f2.F2_CONFIG_FILE_PATH
ORIGINAL = REAL_CONF.read_bytes()


@pytest.fixture
def manager():
    manager = TranslationManager.get_instance()
    previous = manager.lang
    yield manager
    manager.set_language(previous)
    # -l 只对本次运行生效，此前会把语言写回包内的 conf.yaml
    assert REAL_CONF.read_bytes() == ORIGINAL


def test_translation(manager):
    manager.set_language("en_US")
    assert _("Hello, World!") == "Hello, World!"

    manager.set_language("zh_CN")
    assert _("Hello, World!") == "你好，世界！"


def test_cli_language_option_applies_to_this_run(manager):
    result = CliRunner().invoke(main, ["-l", "en_US", "--version"])

    assert result.exit_code == 0, result.output
    assert manager.lang == "en_US"


def test_unsupported_language_is_rejected(manager):
    with pytest.raises(ValueError):
        manager.set_language("fr_FR")

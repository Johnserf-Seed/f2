# path: conftest.py

from pathlib import Path

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    """f2/apps/*/test 下的用例都要访问真实平台接口，统一标记为 network，CI 用 -m "not network" 跳过"""

    root = Path(config.rootpath).resolve()
    for item in items:
        rel = Path(item.path).resolve().relative_to(root).as_posix()
        if rel.startswith("f2/apps/") and "/test/" in rel:
            item.add_marker(pytest.mark.network)

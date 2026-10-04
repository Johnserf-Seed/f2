# path: conftest.py

import asyncio
import socket
from pathlib import Path

import pytest

# 离线用例允许解析的主机：本地服务器
_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", "0.0.0.0"})


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    """f2/apps/*/test 下的用例都要访问真实平台接口，统一标记为 network，CI 用 -m "not network" 跳过"""

    root = Path(config.rootpath).resolve()
    for item in items:
        rel = Path(item.path).resolve().relative_to(root).as_posix()
        if rel.startswith("f2/apps/") and "/test/" in rel:
            item.add_marker(pytest.mark.network)


@pytest.fixture(autouse=True)
def _offline_guard(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    """
    没有 network 标记的用例不访问真实网络：解析外部主机时直接报错

    此前抖音弹幕的离线用例会在构造爬虫时请求 ttwid.bytedance.com，
    断网时变慢或失败，CI 上也在请求真实平台。
    """
    if request.node.get_closest_marker("network"):
        return

    resolve = socket.getaddrinfo

    def offline_getaddrinfo(host, *args, **kwargs):
        name = host.decode() if isinstance(host, bytes) else str(host or "")
        if name and name not in _LOCAL_HOSTS and not name.startswith("127."):
            raise OSError(f"离线用例不应访问网络：{name}")
        return resolve(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", offline_getaddrinfo)


@pytest.fixture(autouse=True)
def _isolated_user_dir(tmp_path_factory: pytest.TempPathFactory, monkeypatch):
    """测试不读写真实的 ~/.f2（用户级配置与推特 queryId 缓存）"""
    from f2.utils.config import user_config

    home = tmp_path_factory.mktemp("home") / ".f2"
    monkeypatch.setattr(user_config, "user_config_dir", lambda: home)


@pytest.fixture
def record_waits(monkeypatch: pytest.MonkeyPatch):
    """把模块中的 asyncio.sleep 换成只记录时长的替身，返回记录列表；不影响全局的 asyncio"""
    waits: list = []

    class _Asyncio:
        def __getattr__(self, name):
            return getattr(asyncio, name)

        async def sleep(self, delay, *args, **kwargs):
            waits.append(delay)

    def patch(module):
        monkeypatch.setattr(module, "asyncio", _Asyncio())
        return waits

    return patch

# path: tests/test_mode_registry.py

import importlib

from f2.utils.core.decorators import app_name_of, get_mode_handlers, mode_handler


def _fake_handler(module_name: str):
    async def handler(_instance):
        return module_name

    handler.__module__ = module_name
    return handler


def test_app_name_of():
    assert app_name_of("f2.apps.douyin.handler") == "douyin"
    assert app_name_of("f2.apps.tiktok.handler") == "tiktok"
    assert app_name_of("my_plugin.handler") == "my_plugin.handler"


def test_same_mode_in_two_apps_does_not_overwrite():
    douyin_post = mode_handler("post")(_fake_handler("f2.apps.fake_a.handler"))
    tiktok_post = mode_handler("post")(_fake_handler("f2.apps.fake_b.handler"))

    assert get_mode_handlers("fake_a")["post"] is douyin_post
    assert get_mode_handlers("f2.apps.fake_b.handler")["post"] is tiktok_post
    assert "post" not in get_mode_handlers("fake_c")


def test_real_apps_keep_their_own_mode_tables():
    # 同一进程导入两个应用后，各自的 post 模式仍指向自己模块里的函数
    importlib.import_module("f2.apps.douyin.handler")
    importlib.import_module("f2.apps.tiktok.handler")

    douyin = get_mode_handlers("douyin")
    tiktok = get_mode_handlers("tiktok")
    assert douyin["post"].__module__ == "f2.apps.douyin.handler"
    assert tiktok["post"].__module__ == "f2.apps.tiktok.handler"
    assert douyin["post"] is not tiktok["post"]
    # 抖音独有的模式不会出现在 tiktok 的表里
    assert "collection" in douyin and "collection" not in tiktok

# path: tests/test_twitter_queryid.py

import json
from urllib.parse import parse_qs, unquote, urlparse

import httpx
import pytest

from f2.apps.twitter.api import QUERY_IDS
from f2.apps.twitter.api import TwitterAPIEndpoints as xendpoints
from f2.apps.twitter.crawler import TwitterCrawler
from f2.apps.twitter.model import BookmarkTweetEncode, UserProfileEncode
from f2.apps.twitter.utils import (
    GraphQLOperation,
    find_chunk_scripts,
    find_main_script,
    graphql_cache_path,
    load_graphql_cache,
    parse_graphql_operations,
)
from f2.crawlers.base_crawler import BaseCrawler
from f2.exceptions.api_exceptions import APINotFoundError

CDN = "https://abs.twimg.com/responsive-web/client-web"
MAIN = f"{CDN}/main.b68ede6d9df21c95a.js"
CHUNK = f"{CDN}/shared~bundle.BookmarkFolders~bundle.Bookmarks.0b251bfed83c436aa.js"
# 已登录的 x.com 页面：入口脚本与 webpack 运行时中按需加载脚本的名称、哈希表
PAGE = (
    f'<script src="{MAIN}"></script><script>t.u=e=>(({{346:"bundle.NotABot",'
    '34778:"shared~bundle.BookmarkFolders~bundle.Bookmarks",34779:"bundle.Bookmarks"})'
    '[e]||e)+"."+({346:"d9addbf1a926b314",34778:"0b251bfed83c436a",'
    '34779:"c3a497f097710f8d"})[e]+"a.js"</script>'
)
MAIN_JS = (
    'e.exports={queryId:"qJy3MbaNndtzxf9IqUzxMg",operationName:"UserTweets",'
    'operationType:"query",metadata:{featureSwitches:["a_enabled"],fieldToggles:[]}}'
    ',e.exports={queryId:"KybxDj9RrADIITXlGG8kpw",operationName:"UserByScreenName",'
    'operationType:"query"}'
)
CHUNK_JS = (
    'e.exports={queryId:"New-Bookmarks_Id",operationName:"Bookmarks",'
    'operationType:"query",metadata:{featureSwitches:["rweb_cashtags_enabled",'
    '"brand_new_switch"],fieldToggles:["withPayments"]}}'
)
KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://x.com/"},
    "cookie": "auth_token=secret; ct0=csrf",
    "proxies": {"http://": None, "https://": None},
    "timeout": 1,
}


def test_parse_graphql_operations():
    operations = parse_graphql_operations(MAIN_JS + CHUNK_JS)

    assert operations["UserTweets"] == GraphQLOperation(
        "qJy3MbaNndtzxf9IqUzxMg", ("a_enabled",)
    )
    assert operations["UserByScreenName"].features == ()
    assert operations["Bookmarks"].query_id == "New-Bookmarks_Id"
    assert parse_graphql_operations("") == {}


def test_find_scripts_in_page():
    assert find_main_script(PAGE) == MAIN
    assert find_main_script("<html>未登录的页面</html>") is None
    # 名称包含关键字的按需加载脚本，按名称从短到长排列
    assert find_chunk_scripts(PAGE, MAIN, ["Bookmarks"]) == [
        f"{CDN}/bundle.Bookmarks.c3a497f097710f8da.js",
        CHUNK,
    ]
    assert find_chunk_scripts(PAGE, MAIN, ["Likes"]) == []
    assert find_chunk_scripts("", MAIN, ["Bookmarks"]) == []


class FakeX:
    """模拟 x.com：内置的收藏 queryId 已失效，新的定义在按需加载的脚本里"""

    def __init__(self, page=PAGE, chunk=CHUNK_JS, valid="New-Bookmarks_Id"):
        self.page = page
        self.chunk = chunk
        self.valid = valid  # 有效的收藏 queryId，其他的都返回 404
        self.requests = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        url = str(request.url)
        if url == "https://x.com/":
            # 与 x.com 一致：带接口的 Authorization 请求页面时返回 401 空内容
            if "authorization" in request.headers:
                return httpx.Response(401)
            return httpx.Response(200, text=self.page)
        if url == MAIN:
            return httpx.Response(200, text=MAIN_JS)
        if url == CHUNK:
            return httpx.Response(200, text=self.chunk)
        if request.url.host == "abs.twimg.com":
            return httpx.Response(200, text="e.exports={}")
        if request.url.path == f"/i/api/graphql/{self.valid}/Bookmarks":
            return httpx.Response(200, json={"data": {"bookmark_timeline_v2": {}}})
        return httpx.Response(404, text='{"message":"Query not found"}')

    def api_paths(self):
        return [r.url.path for r in self.requests if r.url.path.startswith("/i/api")]


def new_run(monkeypatch):
    """模拟重新运行 F2：清空进程内获取的查询，下次请求时重新读入缓存文件"""
    monkeypatch.setattr(TwitterCrawler, "_operations", {})
    monkeypatch.setattr(TwitterCrawler, "_refreshed", set())
    monkeypatch.setattr(TwitterCrawler, "_cache_loaded", False)


@pytest.fixture
def fake_x(monkeypatch):
    new_run(monkeypatch)

    def use(server):
        monkeypatch.setattr(
            BaseCrawler,
            "_create_mount",
            lambda self, async_mode=False: {"all://": httpx.MockTransport(server)},
        )
        return server

    return use


async def fetch_bookmarks():
    async with TwitterCrawler(dict(KWARGS)) as crawler:
        return await crawler.fetch_bookmark_tweet(BookmarkTweetEncode(count=5))


async def test_expired_query_id_is_read_from_web_scripts(fake_x):
    server = fake_x(FakeX())
    builtin = urlparse(xendpoints.USER_BOOKMARK).path

    assert await fetch_bookmarks() == {"data": {"bookmark_timeline_v2": {}}}
    assert server.api_paths() == [builtin, "/i/api/graphql/New-Bookmarks_Id/Bookmarks"]

    # 新查询需要而内置 features 中没有的开关补上 false，已有的开关保持原值
    retried = parse_qs(server.requests[-1].url.query.decode())
    features = json.loads(unquote(retried["features"][0]))
    assert features["brand_new_switch"] is False
    assert features["rweb_cashtags_enabled"] is True

    # 脚本在 abs.twimg.com 上，下载时不带 x.com 的 cookie 与授权头
    for request in server.requests:
        if request.url.host == "abs.twimg.com":
            assert "cookie" not in request.headers
            assert "authorization" not in request.headers
    assert "auth_token=secret" in server.requests[1].headers["cookie"]

    # 之后的请求直接使用新的 queryId，不再先请求失效的地址
    server.requests.clear()
    await fetch_bookmarks()
    assert server.api_paths() == ["/i/api/graphql/New-Bookmarks_Id/Bookmarks"]


async def test_operation_missing_from_scripts_keeps_the_error(fake_x):
    server = fake_x(FakeX(chunk="e.exports={}"))

    with pytest.raises(APINotFoundError):
        await fetch_bookmarks()

    assert TwitterCrawler._operations == {}
    assert len(server.api_paths()) == 1


async def test_logged_out_page_keeps_the_error(fake_x):
    # cookie 失效时 x.com 返回未登录的页面，其中没有 main.js
    server = fake_x(FakeX(page="<html>logged out</html>"))

    with pytest.raises(APINotFoundError):
        await fetch_bookmarks()

    assert [str(r.url) for r in server.requests if r.url.host == "abs.twimg.com"] == []


async def test_valid_builtin_query_id_needs_no_scripts(fake_x):
    def server(request):
        server.urls.append(str(request.url))
        return httpx.Response(200, json={"data": {"user": {}}})

    server.urls = []
    fake_x(server)

    async with TwitterCrawler(dict(KWARGS)) as crawler:
        await crawler.fetch_user_profile(UserProfileEncode(screen_name="NASA"))

    assert len(server.urls) == 1
    assert urlparse(server.urls[0]).path == urlparse(xendpoints.USER_PROFILE).path


# ---------------- 获取的 queryId 缓存到本地，直到下次更新 ----------------

BUILTIN = QUERY_IDS["Bookmarks"]


def write_cache(query_id, replaces, text=None):
    path = graphql_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"query_id": query_id, "replaces": replaces, "features": []}
    path.write_text(text or json.dumps({"operations": {"Bookmarks": entry}}))
    return path


async def test_new_query_id_is_cached_for_later_runs(fake_x, monkeypatch):
    server = fake_x(FakeX())
    await fetch_bookmarks()

    cached = load_graphql_cache()["Bookmarks"]
    assert (cached.query_id, cached.replaces) == ("New-Bookmarks_Id", BUILTIN)
    assert "brand_new_switch" in cached.features

    # 再次运行时直接使用缓存的值，不再先请求失效的地址，也不用再下载网页脚本
    new_run(monkeypatch)
    server.requests.clear()
    await fetch_bookmarks()

    assert all(r.url.path.startswith("/i/api") for r in server.requests)
    assert server.api_paths() == ["/i/api/graphql/New-Bookmarks_Id/Bookmarks"]


async def test_cache_is_ignored_after_builtin_update(fake_x):
    # 缓存的值替换的是旧版 F2 的内置值；F2 更新内置值后仍然内置优先
    write_cache("Cached_Id", "Old-Builtin_Id")
    server = fake_x(FakeX(valid=BUILTIN))

    await fetch_bookmarks()

    assert server.api_paths() == [f"/i/api/graphql/{BUILTIN}/Bookmarks"]


async def test_expired_cached_query_id_is_refreshed(fake_x):
    # X 再次更换 queryId 后，缓存的值也返回 404：重新获取并更新缓存
    write_cache("Stale_Id", BUILTIN)
    server = fake_x(FakeX())

    await fetch_bookmarks()

    assert server.api_paths() == [
        "/i/api/graphql/Stale_Id/Bookmarks",
        "/i/api/graphql/New-Bookmarks_Id/Bookmarks",
    ]
    assert load_graphql_cache()["Bookmarks"].query_id == "New-Bookmarks_Id"


async def test_unreadable_cache_is_ignored(fake_x):
    write_cache("", "", text="{not json")
    server = fake_x(FakeX(valid=BUILTIN))

    await fetch_bookmarks()

    assert server.api_paths() == [f"/i/api/graphql/{BUILTIN}/Bookmarks"]


async def test_unwritable_cache_does_not_break_requests(fake_x):
    # 缓存目录的位置被文件占住，无法写入时只记录警告，本次请求照常完成
    blocker = graphql_cache_path().parent
    blocker.parent.mkdir(parents=True, exist_ok=True)
    blocker.write_text("x")
    fake_x(FakeX())

    assert await fetch_bookmarks() == {"data": {"bookmark_timeline_v2": {}}}
    assert load_graphql_cache() == {}

# path: f2/apps/twitter/crawler.py

import json
from typing import Dict, Optional, Set
from urllib.parse import quote, unquote

from f2.apps.twitter.api import TwitterAPIEndpoints as xendpoints
from f2.apps.twitter.model import (
    BookmarkTweet,
    BookmarkTweetEncode,
    LikeTweet,
    LikeTweetEncode,
    PostTweet,
    PostTweetEncode,
    TweetDetail,
    TweetDetailEncode,
    UserProfile,
    UserProfileEncode,
    encode_model,
)
from f2.apps.twitter.utils import (
    ClientConfManager,
    GraphQLOperation,
    ModelManager,
    find_chunk_scripts,
    find_main_script,
    load_graphql_cache,
    parse_graphql_operations,
    save_graphql_cache,
)
from f2.crawlers.base_crawler import BaseCrawler
from f2.exceptions.api_exceptions import APINotFoundError
from f2.i18n.translator import _
from f2.log.logger import logger
from f2.utils.http.cookie import parse_cookie_str

# 最多再下载几个按需加载的脚本来查找不在 main.js 中的查询
_MAX_CHUNK_SCRIPTS = 5


class TwitterCrawler(BaseCrawler):
    # 内置 queryId 失效后从网页脚本中获取的查询，同一进程内的爬虫共用；
    # 第一次请求时读入缓存文件，之后的运行不再先请求失效的地址
    _operations: Dict[str, GraphQLOperation] = {}
    _cache_loaded = False
    # 本次运行中已经重新获取过的查询，再次失效时不再重复获取
    _refreshed: Set[str] = set()

    def __init__(
        self,
        kwargs: Optional[dict] = None,
    ):
        # 需要与cli同步
        kwargs = kwargs or {}
        self.kwargs = kwargs
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        self.authorization = (
            kwargs.get("Authorization") or ClientConfManager.authorization()
        )
        # X 要求 X-Csrf-Token 与 cookie 里的 ct0 一致，cookie 带有 ct0 时优先使用它，
        # 避免配置文件里过期的值导致 403（#426，移植自 #442）
        ct0 = parse_cookie_str(kwargs.get("cookie") or "").get("ct0")
        self.x_csrf_token = (
            ct0 or kwargs.get("X-Csrf-Token") or ClientConfManager.x_csrf_token()
        )
        self.headers = kwargs.get("headers", {}) | {
            "Cookie": kwargs.get("cookie"),
            "Authorization": self.authorization,
            "X-Csrf-Token": self.x_csrf_token,
        }

        super().__init__(kwargs=kwargs, proxies=proxies, crawler_headers=self.headers)

    @classmethod
    def _active_operation(cls, endpoint: str) -> Optional[GraphQLOperation]:
        """
        替换该内置 queryId 的查询，没有时使用内置值
        (The operation that replaces the built-in queryId of the endpoint, if any)

        缓存记录了每个新值替换的是哪个内置 queryId，F2 更新内置值后旧记录不再使用。
        """
        if not cls._cache_loaded:
            cls._cache_loaded = True
            for name, cached in load_graphql_cache().items():
                cls._operations.setdefault(name, cached)
        _prefix, builtin, operation = endpoint.rsplit("/", 2)
        resolved = cls._operations.get(operation)
        return resolved if resolved and resolved.replaces == builtin else None

    @classmethod
    def _graphql_endpoint(cls, endpoint: str) -> str:
        """内置接口地址中的 queryId 已经失效并获取了新的值时，换成新的值"""
        resolved = cls._active_operation(endpoint)
        if resolved is None:
            return endpoint
        prefix, _builtin, operation = endpoint.rsplit("/", 2)
        return f"{prefix}/{resolved.query_id}/{operation}"

    @classmethod
    def _graphql_params(cls, endpoint: str, params: dict) -> dict:
        """新的查询需要内置 features 中没有的开关时补上 false，避免接口报开关不能为空"""
        resolved = cls._active_operation(endpoint)
        if not resolved or "features" not in params:
            return params
        features = json.loads(unquote(params["features"]))
        missing = {name: False for name in resolved.features if name not in features}
        if not missing:
            return params
        return params | {"features": quote(json.dumps(features | missing))}

    async def fetch_graphql_operation(
        self, operation: str
    ) -> Optional[GraphQLOperation]:
        """
        从 x.com 网页加载的脚本中读取查询的 queryId
        (Read the queryId of an operation from the scripts loaded by x.com)

        已登录的 x.com 页面会加载入口脚本 main.js，大部分查询定义在其中；收藏等查询在
        按需加载的脚本里，按名称查找。页面只带 cookie：带上接口的 Authorization 时
        x.com 返回 401 空内容；脚本在 abs.twimg.com 上，下载时不带 cookie。

        Args:
            operation (str): 查询名，如 UserTweets (Operation name)

        Returns:
            Optional[GraphQLOperation]: 找到的查询，找不到时为 None
        """
        user_agent = self.headers.get("User-Agent") or ClientConfManager.user_agent()
        page_headers = {"User-Agent": user_agent, "Cookie": self.kwargs.get("cookie")}
        async with BaseCrawler(
            self.kwargs, proxies=self.proxies, crawler_headers=page_headers
        ) as page_crawler:
            html = (
                await page_crawler.get_fetch_data(f"{xendpoints.TWITTER_DOMAIN}/")
            ).text

        main_script = find_main_script(html)
        if not main_script:
            logger.debug(_("x.com 页面中没有找到 main.js，cookie 可能已失效"))
            return None

        scripts = [main_script] + find_chunk_scripts(html, main_script, [operation])[
            :_MAX_CHUNK_SCRIPTS
        ]
        script_headers = {
            "User-Agent": user_agent,
            "Referer": f"{xendpoints.TWITTER_DOMAIN}/",
        }
        async with BaseCrawler(
            self.kwargs, proxies=self.proxies, crawler_headers=script_headers
        ) as script_crawler:
            for script in scripts:
                logger.debug(_("在脚本中查找查询 {0}：{1}").format(operation, script))
                response = await script_crawler.get_fetch_data(script)
                found = parse_graphql_operations(response.text).get(operation)
                if found:
                    return found
        return None

    async def _request_graphql(self, endpoint: str, params: dict, label: str) -> dict:
        url = ModelManager.model_2_endpoint(
            self._graphql_endpoint(endpoint), self._graphql_params(endpoint, params)
        )
        logger.debug(label.format(url))
        return await self._fetch_get_json(url)

    async def _fetch_graphql(self, endpoint: str, params: dict, label: str) -> dict:
        """
        请求网页端 GraphQL 接口 (Request X's web GraphQL API)

        queryId 随 X 发版变化，内置的值失效时接口返回 404（Query not found）。
        此时从网页脚本中读取新的 queryId 重试一次并写入缓存，内置值不变时之后的运行
        直接使用缓存的值；缓存的值也失效时再重新获取。

        Args:
            endpoint (str): 内置的接口地址 (Built-in endpoint)
            params (dict): 请求参数 (Request parameters)
            label (str): 调试日志中接口地址的说明 (Log message for the endpoint)

        Returns:
            dict: 接口响应 (API response)
        """
        _prefix, builtin, operation = endpoint.rsplit("/", 2)
        try:
            return await self._request_graphql(endpoint, params, label)
        except APINotFoundError:
            if operation in self._refreshed:
                raise
            logger.warning(
                _(
                    "推特接口 {0} 的 queryId 已失效，正在从 X 网页的脚本中获取新的值"
                ).format(operation)
            )
            found = await self.fetch_graphql_operation(operation)
            if found is None:
                logger.error(
                    _("没有在 X 网页的脚本中找到接口 {0}，请更新 F2 后再试").format(
                        operation
                    )
                )
                raise
            resolved = found._replace(replaces=builtin)
            type(self)._refreshed.add(operation)
            type(self)._operations[operation] = resolved
            logger.info(
                _("接口 {0} 改用新的 queryId：{1}").format(operation, resolved.query_id)
            )
            if resolved.query_id != builtin:
                cached = load_graphql_cache()
                cached[operation] = resolved
                path = save_graphql_cache(cached)
                if path:
                    logger.debug(
                        _(
                            "新的 queryId 已缓存到 {0}，内置值不变时之后的运行直接使用"
                        ).format(path)
                    )
        return await self._request_graphql(endpoint, params, label)

    async def fetch_tweet_detail(self, params: TweetDetailEncode):
        return await self._fetch_graphql(
            xendpoints.POST_DETAIL,
            TweetDetail(variables=encode_model(params)).model_dump(),
            _("推文详情接口地址: {0}"),
        )

    async def fetch_user_profile(self, params: UserProfileEncode):
        return await self._fetch_graphql(
            xendpoints.USER_PROFILE,
            UserProfile(variables=encode_model(params)).model_dump(),
            _("用户信息接口地址: {0}"),
        )

    async def fetch_post_tweet(self, params: PostTweetEncode):
        return await self._fetch_graphql(
            xendpoints.USER_POST,
            PostTweet(variables=encode_model(params)).model_dump(),
            _("主页推文接口地址: {0}"),
        )

    async def fetch_like_tweet(self, params: LikeTweetEncode):
        return await self._fetch_graphql(
            xendpoints.USER_LIKE,
            LikeTweet(variables=encode_model(params)).model_dump(),
            _("喜欢推文接口地址: {0}"),
        )

    async def fetch_bookmark_tweet(self, params: BookmarkTweetEncode):
        return await self._fetch_graphql(
            xendpoints.USER_BOOKMARK,
            BookmarkTweet(variables=encode_model(params)).model_dump(),
            _("书签(收藏)推文接口地址: {0}"),
        )

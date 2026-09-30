# path: tools/update_twitter_queryid.py
# 从 X 前端 JS bundle 提取 GraphQL 接口的最新 queryId，并可选回写 api.py
#
# 背景：f2 的 Twitter 抓取走 X 前端的内部 GraphQL 接口
#   https://x.com/i/api/graphql/<queryId>/<OperationName>
# queryId 是前端打包时生成的哈希，X 发版会轮换（旧值通常在过渡期仍可用）。
# 本工具从公开可下载的前端代码中提取 operationName -> queryId 映射。
#
# 原理（已验证）：
#   1. 以登录态抓取 https://x.com/ 首页 HTML，定位 main.<hash>.js 主 bundle；
#   2. 主 bundle 内含大部分查询定义，格式为
#        {queryId:"...",operationName:"Likes",operationType:"query",metadata:{...}}
#   3. 懒加载的查询（如 Bookmarks 已移到 bundle.History 中）不在主 bundle 内，
#      改由 Service Worker（/sw.js）的缓存清单列出全部 chunk，逐一下载扫描。
#
# 用法:
#   .venv/Scripts/python.exe tools/update_twitter_queryid.py            # 仅打印映射
#   .venv/Scripts/python.exe tools/update_twitter_queryid.py --patch    # 提取并回写 api.py
#
# 依赖 cookie：优先读取项目内 twi*.yaml，其次 f2/conf/conf.yaml，也可 --cookie-file
# 指定（X 仅向登录态提供完整 bundle）。均未找到时给出警告。

import argparse
import re
import sys
from pathlib import Path

import httpx
from ruamel.yaml import YAML

# 关注的 GraphQL 操作名 -> api.py 中的端点常量名
OPERATIONS = {
    "Likes": "USER_LIKE",
    "UserTweets": "USER_POST",
    "UserByScreenName": "USER_PROFILE",
    "Bookmarks": "USER_BOOKMARK",
    "TweetDetail": "POST_DETAIL",
}

HOME_URL = "https://x.com/"
SW_URL = "https://x.com/sw.js"
CDN_BASE = "https://abs.twimg.com/responsive-web/client-web/"

SCRIPT_SRC_RE = re.compile(r'<script[^>]+src="([^"]+\.js)"')
QUERY_DEF_RE = re.compile(
    r"\{queryId:\"([A-Za-z0-9_-]{15,})\",operationName:\"([A-Za-z0-9_]+)\""
)
SW_CHUNK_RE = re.compile(r"client-web/([A-Za-z0-9_\-./]+\.js)")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
)

# api.py 中操作名出现的位置：`{API_DOMAIN}/<queryId>/<OperationName>`
_ENDPOINT_LINE_TPL = r"({endpoint} = f\"{{API_DOMAIN}}/)[^/]+(/{op}\")"


def load_cookie_from_yaml(path: Path) -> str:
    """从 f2 配置 yaml 中读取 twitter.cookie，兼容多级嵌套结构。"""
    _yaml = YAML(typ="safe")
    with open(path, encoding="utf-8") as f:
        data = _yaml.load(f)
    # 逐层下钻 twitter / f2 容器，兼容 conf.yaml 的 f2: → twitter: → cookie: 两层嵌套
    for _ in range(3):
        if not isinstance(data, dict) or "cookie" in data:
            break
        for key in ("twitter", "f2"):
            if key in data:
                data = data[key]
                break
        else:
            break
    return data["cookie"] if isinstance(data, dict) and "cookie" in data else ""


def extract_from_text(text: str) -> dict:
    """从 JS 文本中提取 operationName -> queryId。"""
    found = {}
    for m in QUERY_DEF_RE.finditer(text):
        qid, op = m.group(1), m.group(2)
        if op in OPERATIONS and op not in found:
            found[op] = qid
    return found


def discover_js_files(client: httpx.Client, home_html: str) -> list:
    """从首页 HTML 中收集 JS bundle 地址，优先 main。<br>"""
    urls: list[str] = []
    for src in SCRIPT_SRC_RE.findall(home_html):
        if "main." in src:
            urls.insert(0, src)
        elif src not in urls:
            urls.append(src)
    return urls


def sweep_chunks(client: httpx.Client, wanted: list, max_workers: int = 20):
    """通过 sw.js chunk 清单兜底扫描，返回缺失操作的 queryId。"""
    import concurrent.futures as cf

    sw = client.get(SW_URL).text
    chunks = list(dict.fromkeys(SW_CHUNK_RE.findall(sw)))
    missing = {op: None for op in wanted}
    found = {}

    def scan(name):
        try:
            r = client.get(CDN_BASE + name, timeout=60.0)
            if r.status_code != 200:
                return None
            return extract_from_text(r.text)
        except Exception:
            return None

    with cf.ThreadPoolExecutor(max_workers=max_workers) as ex:
        for part in ex.map(scan, chunks):
            if not part:
                continue
            for op, qid in part.items():
                if op in missing and op not in found:
                    found[op] = qid
    return found


def patch_api_py(api_path: Path, mapping: dict) -> list:
    """回写 api.py 中的 queryId，返回实际修改的端点列表。"""
    text = api_path.read_text(encoding="utf-8")
    changed = []
    for op, endpoint in OPERATIONS.items():
        qid = mapping.get(op)
        if not qid:
            continue
        pattern = re.compile(
            _ENDPOINT_LINE_TPL.format(endpoint=re.escape(endpoint), op=re.escape(op))
        )
        new_text, n = re.subn(pattern, rf"\g<1>{qid}\g<2>", text)
        if n and new_text != text:
            text = new_text
            changed.append(endpoint)
    if changed:
        api_path.write_text(text, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="提取 X GraphQL queryId 并可选回写 api.py"
    )
    parser.add_argument(
        "--patch",
        action="store_true",
        help="将提取到的新 queryId 回写到 f2/apps/twitter/api.py",
    )
    parser.add_argument(
        "--cookie-file",
        default=None,
        help="包含 twitter.cookie 的 yaml 文件（默认自动探测项目内 twi*.yaml / conf.yaml）",
    )
    parser.add_argument(
        "--api-path",
        default=str(
            Path(__file__).resolve().parent.parent
            / "f2"
            / "apps"
            / "twitter"
            / "api.py"
        ),
        help="api.py 路径（默认自动定位）",
    )
    args = parser.parse_args()

    # 解析 cookie：优先 --cookie-file，其次项目内 twi*.yaml，最后 conf.yaml
    cookie = ""
    candidates = [args.cookie_file] if args.cookie_file else []
    root = Path(__file__).resolve().parent.parent
    candidates += sorted(str(p) for p in root.glob("twi*.yaml"))
    candidates.append(str(root / "f2" / "conf" / "conf.yaml"))
    for c in candidates:
        if c and Path(c).exists():
            try:
                cookie = load_cookie_from_yaml(Path(c))
                if cookie:
                    break
            except Exception:
                continue
    if not cookie:
        print(
            "警告: 未在 twi*.yaml / conf.yaml 中找到 twitter.cookie，"
            "可能无法提取完整 queryId，可用 --cookie-file 显式指定",
            file=sys.stderr,
        )

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
    }
    if cookie:
        headers["Cookie"] = cookie

    try:
        with httpx.Client(
            headers=headers, follow_redirects=True, timeout=30.0, verify=False
        ) as client:
            home = client.get(HOME_URL).text
            mapping = {}
            for url in discover_js_files(client, home):
                try:
                    js = client.get(url).text
                except Exception:
                    continue
                mapping.update(extract_from_text(js))
                if len(mapping) >= len(OPERATIONS):
                    break
            # 兜底：扫描 sw.js 列出的全部 chunk
            missing = [op for op in OPERATIONS if op not in mapping]
            if missing:
                print(f"主 bundle 缺 {missing}，扫描 sw.js chunk 清单…")
                mapping.update(sweep_chunks(client, missing))
    except httpx.HTTPError as e:
        print(f"网络请求失败: {e}", file=sys.stderr)
        return 1

    print("当前 X 前端 queryId 映射:")
    for op in OPERATIONS:
        print(f"  {op:16s} -> {mapping.get(op, '(未找到)')}")

    if args.patch:
        api_path = Path(args.api_path)
        changed = patch_api_py(api_path, mapping)
        if changed:
            print(f"已回写 {api_path}: {', '.join(changed)}")
        else:
            print("无变化（映射未找到或与现有值一致）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

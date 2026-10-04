# path: f2/log/redact.py

import logging
import re
from typing import Any, Iterable, List

# 各平台的登录 cookie，出现在 cookie 串或 名称=值 中时打码
LOGIN_COOKIE_NAMES = (
    # 推特
    "auth_token",
    "ct0",
    "kdt",
    "twid",
    "auth_multi",
    # 微博
    "SUB",
    "SUBP",
    "SRT",
    "SRF",
    "SCF",
    "WBPSESS",
    "_T_WM",
    # 抖音与 TikTok
    "sessionid_ss",
    "sid_tt",
    "sid_guard",
    "uid_tt",
    "uid_tt_ss",
    "sid_ucp_v1",
    "ssid_ucp_v1",
    "sid_ucp_sso_v1",
    "ssid_ucp_sso_v1",
    "sso_uid_tt",
    "sso_uid_tt_ss",
    "toutiao_sso_user",
    "toutiao_sso_user_ss",
    "multi_sids",
    "cmpl_token",
    "d_ticket",
    "n_mh",
    "passport_csrf_token_default",
    "tt_chain_token",
    "tt_csrf_token",
    "csrf_session_id",
    "bd_ticket_guard_client_data",
)

# 键名（不区分大小写，"-" 视同 "_"）命中即视为敏感配置项
SENSITIVE_KEYS = frozenset(
    {name.lower() for name in LOGIN_COOKIE_NAMES}
    | {
        "cookie",
        "cookies",
        "key",
        "token",
        "password",
        "passwd",
        "secret",
        "authorization",
        "mstoken",
        "ttwid",
        "odin_tt",
        "sessionid",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "csrf_token",
    }
)
SENSITIVE_KEY_SUFFIXES = ("_key", "_token", "_cookie", "_password", "_secret")

# 形如 scheme://user:password@host 的代理地址，只脱敏凭据部分
_URL_CREDENTIALS = re.compile(r"(\w+://)([^/\s:@]+):([^/\s@]+)@")
_SECRET_NAMES = "|".join(
    re.escape(name)
    for name in (
        *LOGIN_COOKIE_NAMES,
        "cookie",
        "msToken",
        "ttwid",
        "odin_tt",
        "sessionid",
        "s_v_web_id",
        "passport_csrf_token",
        "access_token",
        "refresh_token",
        "csrf_token",
        "api_key",
        "apikey",
        "token",
        "key",
        "password",
        "passwd",
        "secret",
        "authorization",
    )
)
# 一次扫描处理两种写法，打码后的值不会被再次打码
_SECRETS = re.compile(
    r"(?i)"
    # 整个 cookie 串：Cookie: a=1; b=2，以及请求头字典、JSON 中的 'Cookie': 'a=1; b=2'
    r"(?P<cookie>\bcookies?\b['\"]?\s*[=:：]\s*)"
    r"(?:(?P<quote>['\"])(?P<quoted>[^'\"]+)(?P=quote)"
    r"|(?P<items>[^\s;=,'\"]+=[^\s;,'\"]*(?:;\s*[^\s;=,'\"]+=[^\s;,'\"]*)*))"
    # 名称=值 / 名称: 值 / 名称：值（cookie 中的各项、token、密钥、密码），名称与值可以带引号
    rf"|(?P<name>\b(?:{_SECRET_NAMES})\b|密钥|密码)"
    r"(?P<sep>['\"]?\s*[=:：]\s*['\"]?)"
    r"(?P<value>(?:bearer\s+|basic\s+)?[^;&,\s'\"}\]]+)"
)


def mask_secret(value: Any, keep: int = 4) -> str:
    """
    把敏感值打码，只保留开头 keep 个字符和长度 (Mask a secret, keeping only a short prefix and its length)

    Args:
        value (Any): 敏感值，非字符串会先转成字符串
        keep (int): 保留的开头字符数，值太短时整体打码

    Returns:
        str: 打码后的字符串，如 "ttwi***(len=512)"
    """

    text = str(value)
    if len(text) <= keep * 2:
        return "***"
    return f"{text[:keep]}***(len={len(text)})"


def is_sensitive_key(key: Any) -> bool:
    """判断配置键名是否属于敏感项 (Whether a config key holds a secret)"""

    name = str(key).lower().replace("-", "_")
    return name in SENSITIVE_KEYS or name.endswith(SENSITIVE_KEY_SUFFIXES)


def redact_text(text: str) -> str:
    """
    脱敏一段文本里的凭据 (Redact credentials embedded in free text)

    处理代理地址中的用户名密码、整个 cookie 串、cookie 中各平台的登录字段，以及
    token/密钥/密码 的 名称=值 写法（包括请求头字典、JSON 中带引号的写法）。
    """

    def _mask(match: "re.Match[str]") -> str:
        if match.group("quoted"):
            quote = match.group("quote")
            secret = mask_secret(match.group("quoted"))
            return f"{match.group('cookie')}{quote}{secret}{quote}"
        if match.group("items"):
            return f"{match.group('cookie')}{mask_secret(match.group('items'))}"
        return f"{match.group('name')}{match.group('sep')}{mask_secret(match.group('value'))}"

    text = _URL_CREDENTIALS.sub(r"\1***:***@", text)
    return _SECRETS.sub(_mask, text)


def redact_config(data: Any) -> Any:
    """
    返回配置的脱敏副本，用于写日志 (Return a redacted copy of a config for logging)

    敏感键（cookie、key、token、password 等）的值整体打码；其它字符串值按 redact_text
    处理（如带密码的代理地址）；dict/list 递归；原对象不会被修改。
    """

    if isinstance(data, dict):
        return {
            key: (
                mask_secret(value)
                if is_sensitive_key(key) and value not in (None, "")
                else redact_config(value)
            )
            for key, value in data.items()
        }
    if isinstance(data, (list, tuple)):
        return type(data)(redact_config(item) for item in data)
    if isinstance(data, str):
        return redact_text(data)
    return data


class SecretRedactFilter(logging.Filter):
    """
    日志脱敏过滤器 (Logging filter that redacts secrets)

    挂在 logger 上：记录在交给处理器、向上传播到宿主程序的 root logger 之前就已脱敏，
    因此无论输出到控制台、文件还是用户自己的 handler，cookie/token/密码都不会明文出现。
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:
            return True
        redacted = redact_text(message)
        if redacted != message:
            record.msg = redacted
            record.args = ()
        return True


def install_redact_filter(loggers: Iterable[logging.Logger]) -> None:
    """给记录器安装脱敏过滤器，重复调用不会重复安装"""

    for target in loggers:
        if not any(isinstance(f, SecretRedactFilter) for f in target.filters):
            target.addFilter(SecretRedactFilter())


__all__: List[str] = [
    "SecretRedactFilter",
    "install_redact_filter",
    "is_sensitive_key",
    "mask_secret",
    "redact_config",
    "redact_text",
]

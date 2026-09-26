# path: f2/utils/http/browser.py

import browser_cookie3  # type: ignore[import-untyped]

from f2.i18n.translator import _
from f2.log.logger import logger

FAQ_URL = "https://f2.wiki/faq"


def explain_browser_error(error: Exception) -> str:
    """
    为 browser_cookie3 的常见错误补充原因与解决办法 (Explain common browser_cookie3 errors)

    Args:
        error (Exception): browser_cookie3 抛出的异常

    Returns:
        str: 原始错误信息，常见错误后面附上原因与解决办法
    """
    message = str(error)
    if "Unable to get key for cookie decryption" in message:
        # Windows 上的 Chrome、Edge 自 2024 年 8 月起改用应用绑定加密（#193）
        return _(
            "{0}。Windows 上的新版 Chrome、Edge 改用了应用绑定加密，暂时无法自动获取 cookie；"
            "macOS 需要在钥匙串弹窗中允许访问。可以改用 --auto-cookie firefox，或在浏览器中手动复制 cookie，详见 {1}"
        ).format(message, FAQ_URL)
    if "Unable to read database file" in message:
        return _("{0}。浏览器的 cookie 数据库被占用，请完全关闭浏览器后重试").format(
            message
        )
    return message


def get_cookie_from_browser(browser_choice: str, domain: str = "") -> dict:
    """
    根据用户选择的浏览器获取domain的cookie。

    Args:
        browser_choice (str): 用户选择的浏览器名称
        domain (str): 域名

    Returns:
        dict: *.domain的cookie值
    """
    if not browser_choice or not domain:
        return {}

    BROWSER_FUNCTIONS = {
        "chrome": browser_cookie3.chrome,
        "firefox": browser_cookie3.firefox,
        "edge": browser_cookie3.edge,
        "opera": browser_cookie3.opera,
        "opera_gx": browser_cookie3.opera_gx,
        "safari": browser_cookie3.safari,
        "chromium": browser_cookie3.chromium,
        "brave": browser_cookie3.brave,
        "vivaldi": browser_cookie3.vivaldi,
        "librewolf": browser_cookie3.librewolf,
    }
    cj_function = BROWSER_FUNCTIONS.get(browser_choice)
    if not cj_function:
        logger.error(_("不支持的浏览器：{0}").format(browser_choice))
        return {}
    try:
        cj = cj_function(domain_name=domain)
    except browser_cookie3.BrowserCookieError as e:
        raise browser_cookie3.BrowserCookieError(explain_browser_error(e)) from e
    cookie_value = {c.name: c.value for c in cj if c.domain.endswith(domain)}
    return cookie_value

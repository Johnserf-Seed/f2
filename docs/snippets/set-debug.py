// #region set-debug-snippet
import asyncio
from f2.apps.douyin.handler import DouyinHandler

from f2.log.logger import logger    # [!code focus]
logger.setLevel("WARNING")    # [!code focus]

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
}

if __name__ == "__main__":
    asyncio.run(DouyinHandler(kwargs).fetch_user_post(
        "MS4wLjABAAAA35iXl5qqCbLKY99pUvxkXzvpSXi8jgUbJ0zR4EuTpcHcS8PHaEb6G9yB6iKR0dNl"
        )
    )

// #endregion set-debug-snippet


// #region cli-debug-snippet
f2 -d WARNING -M post -u https://www.douyin.com/user/MS4wLjABAAAA35iXl5qqCbLKY99pUvxkXzvpSXi8jgUbJ0zR4EuTpcHcS8PHaEb6G9yB6iKR0dNl
// #endregion cli-debug-snippet


// #region log-2-console-snippet
import asyncio
from f2.apps.douyin.handler import DouyinHandler

from f2.log.logger import log_setup    # [!code focus]
logger = log_setup(log_to_console=True)    # [!code focus]

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
}

if __name__ == "__main__":
    asyncio.run(DouyinHandler(kwargs).fetch_user_post(
        "MS4wLjABAAAA35iXl5qqCbLKY99pUvxkXzvpSXi8jgUbJ0zR4EuTpcHcS8PHaEb6G9yB6iKR0dNl"
        )
    )

// #endregion log-2-console-snippet
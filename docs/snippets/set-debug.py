// #region set-debug-snippet
import asyncio
from f2.apps.douyin.handler import fetch_user_post

from f2.log.logger import logger    # [!code focus]
logger.setLevel("WARNING")    # [!code focus]

if __name__ == "__main__":
    asyncio.run(fetch_user_post("MS4wLjABAAAA35iXl5qqCbLKY99pUvxkXzvpSXi8jgUbJ0zR4EuTpcHcS8PHaEb6G9yB6iKR0dNl"))

// #endregion set-debug-snippet


// #region log-2-console-snippet
import asyncio
from f2.apps.douyin.handler import fetch_user_post

from f2.log.logger import log_setup    # [!code focus]
logger = log_setup(log_to_console=True)    # [!code focus]

if __name__ == "__main__":
    asyncio.run(fetch_user_post("MS4wLjABAAAA35iXl5qqCbLKY99pUvxkXzvpSXi8jgUbJ0zR4EuTpcHcS8PHaEb6G9yB6iKR0dNl"))

// #endregion log-2-console-snippet
# path: f2/utils/http/proxy.py

import traceback
from typing import Optional

import httpx

from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger


def check_proxy_avail(
    http_proxy: str,
    https_proxy: str,
    test_url: str = "https://www.google.com",
    timeout: int = 5,
    method: str = "GET",
    **kwargs,
) -> bool:
    """
    检查 HTTP 和 HTTPS 代理是否可用

    Args:
        http_proxy (str): HTTP 代理地址 (例如 "http://proxy_ip:proxy_port")
        https_proxy (str): HTTPS 代理地址 (例如 "http://proxy_ip:proxy_port")
        test_url (str): 测试地址，默认 https://www.google.com
        expected_content (str): 预期的内容关键字，用于验证页面加载正确
        timeout (int): 请求超时时间，默认 5 秒
        method (str): 请求方法，如 "GET", "POST", "PUT", "DELETE", "OPTIONS"
        **kwargs: 其他请求参数，如 data, json, headers 等

    Returns:
        bool: 如果代理可用返回 True，否则返回 False
    """

    if not http_proxy or not https_proxy:
        logger.error(_("代理地址为空"))
        return False

    proxy_mounts = {
        "http://": httpx.HTTPTransport(proxy=http_proxy),
        "https://": httpx.HTTPTransport(proxy=https_proxy),
    }

    try:
        logger.info(_("正在测试代理服务器是否可用🚀"))
        # 创建 HTTP 和 HTTPS 的代理挂载
        with httpx.Client(timeout=timeout, mounts=proxy_mounts) as client:
            # 根据方法选择请求
            response = client.request(
                method.upper(),
                test_url,
                follow_redirects=True,
                **kwargs,
            )
            response.raise_for_status()

            # 验证响应内容是否包含预期关键字
            if expected_content and expected_content not in response.text:
                logger.warning(_("代理请求成功，但内容不符合预期"))
                return False

            logger.info("[green]代理请求成功，测试地址：{0}[/green]".format(test_url))
            return True

    except httpx.ProxyError as e:
        logger.error(_("代理错误：{0}").format(e))
    except httpx.TimeoutException as e:
        logger.error(_("代理请求超时，错误: {0}").format(e))
    except httpx.TooManyRedirects as e:
        logger.error(_("重定向次数过多：{0}").format(e))
    except httpx.HTTPStatusError as e:
        logger.error(
            _("代理请求 {0} 状态码错误：{1}").format(test_url, e.response.status_code)
        )
    except httpx.RequestError as e:
        logger.error(_("代理请求错误：{0}").format(e))
    except Exception as e:
        trace_logger.error(traceback.format_exc())
        logger.error(_("代理请求失败：{0}").format(e))

    return False

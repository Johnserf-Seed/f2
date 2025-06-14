# path: f2/utils/http/proxy.py

import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union

import httpx
from httpx_socks import SyncProxyTransport

from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger


class ProxyType(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


@dataclass
class ProxyConfig:
    type: ProxyType
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    rdns: bool = True

    def get_url(self) -> str:
        """获取代理URL格式"""
        auth = (
            f"{self.username}:{self.password}@"
            if self.username and self.password
            else ""
        )
        return f"{self.type.value}://{auth}{self.host}:{self.port}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "type": self.type.value,
            "host": self.host,
            "port": self.port,
            "rdns": self.rdns,
        }
        if self.username:
            result["username"] = self.username
        if self.password:
            result["password"] = self.password
        return result


def check_proxy_avail(
    proxy_config: Union[Dict[str, str], ProxyConfig, str],
    test_url: str = "https://httpbin.org/ip",
    expected_content: Optional[str] = None,
    timeout: int = 10,
    method: str = "GET",
    **kwargs,
) -> bool:
    """
    检查代理是否可用，支持HTTP、HTTPS、SOCKS4和SOCKS5代理

    Args:
        proxy_config: 代理配置，可以是以下格式：
                     - 字典: {"type": "socks5", "host": "127.0.0.1", "port": 1080, ...}
                     - ProxyConfig对象
                     - 字符串: "socks5://username:password@127.0.0.1:1080"
        test_url: 测试地址，默认 https://httpbin.org/ip (返回当前IP地址的JSON)
        expected_content: 预期的内容关键字，用于验证页面加载正确
        timeout: 请求超时时间，默认 10 秒 (增加到10秒，因为代理可能较慢)
        method: 请求方法，如 "GET", "POST", "PUT", "DELETE", "OPTIONS"
        **kwargs: 其他请求参数，如 data, json, headers 等

    Returns:
        bool: 如果代理可用返回 True，否则返回 False
    """
    # 处理多种输入格式
    if isinstance(proxy_config, str):
        # 解析URL格式的代理字符串
        proxy_url = proxy_config
    elif isinstance(proxy_config, dict):
        # 从字典构建代理配置
        proxy_type = proxy_config.get("type", "http")
        host = proxy_config.get("host", "")
        port = proxy_config.get("port", 0)
        username = proxy_config.get("username", "")
        password = proxy_config.get("password", "")

        if not host or not port:
            logger.error(_("代理地址或端口为空"))
            return False

        auth = f"{username}:{password}@" if username and password else ""
        proxy_url = f"{proxy_type}://{auth}{host}:{port}"
    elif isinstance(proxy_config, ProxyConfig):
        proxy_url = proxy_config.get_url()
    else:
        logger.error(_("不支持的代理配置格式"))
        return False

    try:
        logger.info(_("正在测试代理服务器是否可用🚀"))
        logger.debug(_("代理URL：{0}").format(proxy_url))

        # 根据代理类型选择合适的传输方式
        if proxy_url.startswith(("socks4://", "socks5://")):
            transport = SyncProxyTransport.from_url(proxy_url)
            client = httpx.Client(transport=transport, timeout=timeout, verify=False)
        else:
            # HTTP/HTTPS代理 - 使用 mounts 挂载代理传输
            proxy_transport = httpx.HTTPTransport(proxy=proxy_url)
            mounts = {
                "http://": proxy_transport,
                "https://": proxy_transport,
            }
            client = httpx.Client(
                timeout=timeout,
                mounts=mounts,
                verify=False,
            )

        with client:
            # 根据方法选择请求
            response = client.request(
                method.upper(),
                test_url,
                follow_redirects=True,
                **kwargs,
            )
            response.raise_for_status()

            # 如果使用默认的 httpbin.org/ip，验证返回的是否为有效的IP地址JSON
            if test_url == "https://httpbin.org/ip":
                try:
                    ip_data = response.json()
                    origin_ip = ip_data.get("origin", "")

                    if not origin_ip:
                        logger.warning(_("代理请求成功，但未获取到有效的IP地址"))
                        return False

                    # 检查是否是有效的IP地址格式（简单验证）
                    import re

                    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
                    if not re.match(ip_pattern, origin_ip.split(",")[0].strip()):
                        logger.warning(
                            _("代理请求成功，但返回的IP格式无效：{0}").format(origin_ip)
                        )
                        return False

                    logger.debug(_("代理测试成功，当前出口IP：{0}").format(origin_ip))
                    return True

                except (ValueError, KeyError) as e:
                    logger.warning(_("代理请求成功，但响应格式异常：{0}").format(e))
                    return False

            # 验证响应内容是否包含预期关键字（用于自定义测试URL）
            if expected_content and expected_content not in response.text:
                logger.warning(_("代理请求成功，但内容不符合预期"))
                return False

            logger.debug(_("代理请求成功，测试地址：{0}").format(test_url))
            return True

    except httpx.ConnectTimeout:
        logger.error(_("代理连接超时：{0}").format(proxy_url))
        trace_logger.error(traceback.format_exc())
        return False
    except httpx.ReadTimeout:
        logger.error(_("代理读取超时：{0}").format(proxy_url))
        trace_logger.error(traceback.format_exc())
        return False
    except httpx.ProxyError as e:
        logger.error(_("代理服务器错误：{0} - {1}").format(proxy_url, e))
        trace_logger.error(traceback.format_exc())
        return False
    except httpx.HTTPStatusError as e:
        logger.error(
            _("HTTP状态错误：{0} - 状态码：{1}").format(
                proxy_url, e.response.status_code
            )
        )
        trace_logger.error(traceback.format_exc())
        return False
    except httpx.NetworkError as e:
        logger.error(_("网络连接错误：{0} - {1}").format(proxy_url, e))
        trace_logger.error(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(_("代理请求失败：{0} - {1}").format(proxy_url, e))
        trace_logger.error(traceback.format_exc())
        return False

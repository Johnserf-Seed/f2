# path: f2/utils/http/proxy.py

import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union
from urllib.parse import quote, unquote

import httpx
from httpx_socks import SyncProxyTransport

from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.log.redact import redact_text


class ProxyType(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


def _encode_credential(value: Any) -> str:
    # 先解码再编码：此前密码含特殊字符时只能自己按 URL 编码后填写，这样的配置结果不变
    return quote(unquote(str(value)), safe="")


def _proxy_auth(username: Any, password: Any) -> str:
    """
    代理地址中的用户名与密码 (Credentials part of a proxy URL)

    按 URL 编码，此前密码中有 @、:、/ 等字符时拼出的地址无法解析，httpx 与
    python-socks 会报端口无效，代理连接直接失败。

    Returns:
        str: "用户名:密码@"，没有用户名或密码时为空字符串
    """
    if not username or not password:
        return ""
    return f"{_encode_credential(username)}:{_encode_credential(password)}@"


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
        auth = _proxy_auth(self.username, self.password)
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


def proxy_url_from_config(proxies: Any) -> Optional[str]:
    """
    F2 代理配置对应的代理地址 (Proxy URL of an F2 proxy configuration)

    支持新格式 type、host、port（可带 username、password）与旧格式的 http:// 键。

    Args:
        proxies (Any): 配置中的 proxies (The proxies setting)

    Returns:
        Optional[str]: 代理地址，没有配置时为 None (Proxy URL, None when not configured)
    """
    if not isinstance(proxies, dict):
        return None

    proxy_type, host, port = (
        proxies.get("type"),
        proxies.get("host"),
        proxies.get("port"),
    )
    if proxy_type and host and port:
        auth = _proxy_auth(proxies.get("username"), proxies.get("password"))
        return f"{proxy_type}://{auth}{host}:{port}"

    return proxies.get("http://") or None


def prefer_proxies(proxies: Any, default: Any) -> Any:
    """
    调用方配置了代理时使用它，否则使用默认的代理配置 (The caller's proxies when configured)

    应用配置与命令行 --proxies 中的代理优先；它们没有配置代理时（例如只有空的
    http://、https://），使用客户端配置中的代理，与此前一致。
    """
    return proxies if proxy_url_from_config(proxies) else default


def parse_proxy_address(proxy_type: str, address: str) -> Dict[str, Any]:
    """
    命令行中的代理地址转换为代理配置 (Proxy configuration from a command line address)

    地址形如 host:port 或 username:password@host:port。用户名与主机按最后一个 @ 分开，
    密码中有 @ 时也能识别。

    Args:
        proxy_type (str): 代理类型 (Proxy type)
        address (str): 代理地址 (Proxy address)

    Returns:
        Dict[str, Any]: 与配置文件中 proxies 格式相同的配置 (Config in the proxies format)

    Raises:
        ValueError: 缺少端口，或端口不是 1–65535 之间的数字
    """
    userinfo, _at, hostport = address.rpartition("@")
    host, _colon, port = hostport.rpartition(":")
    if not host or not port.isdigit() or not 0 < int(port) < 65536:
        raise ValueError(address)

    config: Dict[str, Any] = {"type": proxy_type, "host": host, "port": int(port)}
    if userinfo:
        config["username"], _colon, config["password"] = userinfo.partition(":")
    return config


def check_proxy_avail(
    proxy_config: Union[Dict[str, str], ProxyConfig, str],
    test_url: str = "https://httpbin.org/ip",
    expected_content: Optional[str] = None,
    timeout: int = 10,
    method: str = "GET",
    verify: Union[bool, str] = True,
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
        verify: TLS 证书校验，True / False / CA 证书路径，默认为 True
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

        proxy_url = f"{proxy_type}://{_proxy_auth(username, password)}{host}:{port}"
    elif isinstance(proxy_config, ProxyConfig):
        proxy_url = proxy_config.get_url()
    else:
        logger.error(_("不支持的代理配置格式"))
        return False

    try:
        logger.info(_("正在测试代理服务器是否可用🚀"))
        logger.debug(_("代理URL：{0}").format(redact_text(proxy_url)))

        # 根据代理类型选择合适的传输方式
        if proxy_url.startswith(("socks4://", "socks5://")):
            transport = SyncProxyTransport.from_url(proxy_url, verify=verify)
            client = httpx.Client(transport=transport, timeout=timeout)
        else:
            # HTTP/HTTPS代理 - 使用 mounts 挂载代理传输
            proxy_transport = httpx.HTTPTransport(proxy=proxy_url, verify=verify)
            mounts = {
                "http://": proxy_transport,
                "https://": proxy_transport,
            }
            client = httpx.Client(
                timeout=timeout,
                mounts=mounts,
                verify=verify,
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

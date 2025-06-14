# path: tests/test_proxy.py

import pytest

from f2.i18n.translator import _
from f2.utils.http.proxy import ProxyConfig, ProxyType


class TestProxyType:
    """测试代理类型枚举"""

    def test_proxy_type_values(self):
        """测试代理类型的值是否正确"""
        assert ProxyType.HTTP.value == "http"
        assert ProxyType.HTTPS.value == "https"
        assert ProxyType.SOCKS4.value == "socks4"
        assert ProxyType.SOCKS5.value == "socks5"

    def test_proxy_type_membership(self):
        """测试代理类型成员检查"""
        assert ProxyType.HTTP in ProxyType
        assert ProxyType.SOCKS5 in ProxyType
        assert len(ProxyType) == 4


class TestProxyConfig:
    """测试代理配置类"""

    def test_proxy_config_init_basic(self):
        """测试基本代理配置初始化"""
        config = ProxyConfig(type=ProxyType.HTTP, host="127.0.0.1", port=8080)
        assert config.type == ProxyType.HTTP
        assert config.host == "127.0.0.1"
        assert config.port == 8080
        assert config.username is None
        assert config.password is None
        assert config.rdns is True

    def test_proxy_config_init_with_auth(self):
        """测试带认证的代理配置初始化"""
        config = ProxyConfig(
            type=ProxyType.SOCKS5,
            host="proxy.example.com",
            port=1080,
            username="user",
            password="pass",
            rdns=False,
        )
        assert config.type == ProxyType.SOCKS5
        assert config.host == "proxy.example.com"
        assert config.port == 1080
        assert config.username == "user"
        assert config.password == "pass"
        assert config.rdns is False

    def test_get_url_without_auth(self):
        """测试生成不带认证的代理URL"""
        config = ProxyConfig(type=ProxyType.HTTP, host="127.0.0.1", port=8080)
        expected_url = "http://127.0.0.1:8080"
        assert config.get_url() == expected_url

    def test_get_url_with_auth(self):
        """测试生成带认证的代理URL"""
        config = ProxyConfig(
            type=ProxyType.SOCKS5,
            host="proxy.example.com",
            port=1080,
            username="user",
            password="pass",
        )
        expected_url = "socks5://user:pass@proxy.example.com:1080"
        assert config.get_url() == expected_url

    def test_get_url_with_partial_auth(self):
        """测试只有用户名或密码时的URL生成"""
        config = ProxyConfig(
            type=ProxyType.HTTP,
            host="127.0.0.1",
            port=8080,
            username="user",
            # password is None
        )
        expected_url = "http://127.0.0.1:8080"
        assert config.get_url() == expected_url

    def test_to_dict_without_auth(self):
        """测试转换为字典格式（无认证）"""
        config = ProxyConfig(
            type=ProxyType.HTTPS, host="proxy.example.com", port=443, rdns=False
        )
        expected_dict = {
            "type": "https",
            "host": "proxy.example.com",
            "port": 443,
            "rdns": False,
        }
        assert config.to_dict() == expected_dict

    def test_to_dict_with_auth(self):
        """测试转换为字典格式（带认证）"""
        config = ProxyConfig(
            type=ProxyType.SOCKS4,
            host="127.0.0.1",
            port=1080,
            username="testuser",
            password="testpass",
        )
        expected_dict = {
            "type": "socks4",
            "host": "127.0.0.1",
            "port": 1080,
            "rdns": True,
            "username": "testuser",
            "password": "testpass",
        }
        assert config.to_dict() == expected_dict


if __name__ == "__main__":
    pytest.main([__file__])

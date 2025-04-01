# path: tests/test_rsa.py

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

from f2.utils.utils import RSAEncryptionUtils


# 生成RSA密钥对
@pytest.fixture
def rsa_keypair():
    # 生成一个2048位的RSA密钥对
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


# 测试 RSA 加密和解密
def test_rsa_encrypt_decrypt(rsa_keypair):
    private_key, public_key = rsa_keypair
    rsa_utils = RSAEncryptionUtils(
        private_key, public_key, algorithm="RSA2048", padding_scheme="pkcs1"
    )

    plaintext = b"Hello, RSA!"

    # 加密
    encrypted = rsa_utils.rsa_encrypt(plaintext)

    # 解密
    decrypted = rsa_utils.rsa_decrypt(encrypted)

    assert decrypted == plaintext, "解密后的明文与原始明文不匹配"


# 测试不同的填充方案（PKCS1 和 OAEP）
def test_rsa_encrypt_decrypt_with_padding(rsa_keypair):
    private_key, public_key = rsa_keypair

    # 测试 PKCS1 填充方案
    rsa_utils_pkcs1 = RSAEncryptionUtils(
        private_key, public_key, algorithm="RSA2048", padding_scheme="pkcs1"
    )
    plaintext = b"Test with PKCS1 padding"
    encrypted_pkcs1 = rsa_utils_pkcs1.rsa_encrypt(plaintext)
    decrypted_pkcs1 = rsa_utils_pkcs1.rsa_decrypt(encrypted_pkcs1)
    assert decrypted_pkcs1 == plaintext, "PKCS1 填充方案解密失败"

    # 测试 OAEP 填充方案
    rsa_utils_oaep = RSAEncryptionUtils(
        private_key, public_key, algorithm="RSA2048", padding_scheme="oaep"
    )
    encrypted_oaep = rsa_utils_oaep.rsa_encrypt(plaintext)
    decrypted_oaep = rsa_utils_oaep.rsa_decrypt(encrypted_oaep)
    assert decrypted_oaep == plaintext, "OAEP 填充方案解密失败"


# 测试无效填充方案
def test_invalid_padding_scheme(rsa_keypair):
    private_key, public_key = rsa_keypair
    with pytest.raises(ValueError, match="填充方案必须为 'pkcs1' 或 'oaep'"):
        RSAEncryptionUtils(
            private_key, public_key, algorithm="RSA2048", padding_scheme="invalid"
        )


# 测试密钥长度检查
def test_invalid_key_length():
    # 使用不符合期望的密钥长度
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024,  # 使用不符合2048位要求的密钥长度
        backend=default_backend(),
    )
    public_key = private_key.public_key()
    with pytest.raises(
        ValueError, match="RSA2048 算法私钥长度不正确：1024 位，期望长度为 2048 位。"
    ):
        RSAEncryptionUtils(
            private_key, public_key, algorithm="RSA2048", padding_scheme="pkcs1"
        )


# 测试公钥加密和私钥解密
def test_rsa_public_key_encrypt_private_key_decrypt(rsa_keypair):
    private_key, public_key = rsa_keypair
    rsa_utils = RSAEncryptionUtils(
        private_key, public_key, algorithm="RSA2048", padding_scheme="pkcs1"
    )

    plaintext = b"Encrypt with public key, decrypt with private key"

    # 公钥加密
    encrypted = rsa_utils.rsa_encrypt(plaintext)

    # 私钥解密
    decrypted = rsa_utils.rsa_decrypt(encrypted)

    assert decrypted == plaintext, "解密后的明文与原始明文不匹配"


# 测试私钥加密和公钥解密
def test_rsa_private_key_encrypt_public_key_decrypt(rsa_keypair):
    private_key, public_key = rsa_keypair
    rsa_utils = RSAEncryptionUtils(
        private_key, public_key, algorithm="RSA2048", padding_scheme="pkcs1"
    )

    plaintext = b"Encrypt with private key, decrypt with public key"

    # 私钥加密
    encrypted = rsa_utils.rsa_encrypt(plaintext)

    # 公钥解密
    decrypted = rsa_utils.rsa_decrypt(encrypted)

    assert decrypted == plaintext, "解密后的明文与原始明文不匹配"


# 测试解密错误
def test_rsa_decrypt_with_wrong_key(rsa_keypair):
    private_key, public_key = rsa_keypair
    rsa_utils = RSAEncryptionUtils(
        private_key, public_key, algorithm="RSA2048", padding_scheme="pkcs1"
    )

    plaintext = b"Test decryption with wrong key"

    # 加密
    encrypted = rsa_utils.rsa_encrypt(plaintext)

    # 创建一个新的公私钥对作为“错误的私钥”实例
    wrong_private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    rsa_utils_wrong_key = RSAEncryptionUtils(
        wrong_private_key, public_key, algorithm="RSA2048", padding_scheme="pkcs1"
    )

    # 使用错误的私钥解密，应该返回错误的结果或抛出异常
    try:
        decrypted = rsa_utils_wrong_key.rsa_decrypt(encrypted)
    except ValueError:
        # 捕获到填充校验失败的异常，符合预期
        pass
    else:
        # 验证解密结果与原始明文不同
        assert decrypted != plaintext, "解密结果不应与原始明文相同"

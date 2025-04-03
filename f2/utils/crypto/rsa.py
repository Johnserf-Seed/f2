# path: f2/utils/crypto/rsa.py

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from f2.i18n.translator import _


class RSAEncryptionUtils:
    """
    RSA加密工具类
    支持RSA1024, RSA2048, RSA4096算法
    支持pkcs1和oaep填充方案
    支持使用公钥加密和私钥解密
    支持使用私钥签名和公钥验证
    """

    # 支持的算法
    SUPPORTED_ALGORITHMS = [
        "RSA512",
        "RSA1024",
        "RSA2048",
        "RSA4096",
    ]

    SUPPORTED_PADDING_SCHEMES = [
        "pkcs1",
        "oaep",  # 更安全
    ]

    def __init__(
        self,
        private_key: rsa.RSAPrivateKey,
        public_key: rsa.RSAPublicKey,
        algorithm: str = "RSA2048",
        padding_scheme: str = "pkcs1",
    ):
        """
        初始化RSA加密工具类实例

        Args:
            private_key (RSAPrivateKey): 私钥
            public_key (RSAPublicKey): 公钥
            algorithm (str, optional): 加密算法 (RSA1024, RSA2048, RSA4096)
            padding_scheme (str, optional): 填充方案 ('pkcs1' 或 'oaep')

        Raises:
            ValueError: 当算法不可用或密钥长度不正确时抛出错误

        Returns:
            RSAEncryptionUtils: 加密工具类实例
        """
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(_("算法必须为 'RSA1024', 'RSA2048' 或 'RSA4096'。"))

        if padding_scheme not in self.SUPPORTED_PADDING_SCHEMES:
            raise ValueError(_("填充方案必须为 'pkcs1' 或 'oaep'。"))

        # 设置私钥和公钥
        self.private_key = private_key
        self.public_key = public_key
        self.padding_scheme = padding_scheme

        # 检查密钥长度是否正确
        expected_key_length = int(algorithm[3:])
        if private_key.key_size != expected_key_length:
            raise ValueError(
                _("{0} 算法私钥长度不正确：{1} 位，期望长度为 {2} 位。").format(
                    algorithm, private_key.key_size, expected_key_length
                )
            )

    def rsa_encrypt(self, plaintext: bytes) -> bytes:
        """
        RSA 加密（使用公钥加密）

        Args:
            plaintext (bytes): 明文数据

        Returns:
            bytes: 密文数据
        """
        if self.padding_scheme == "pkcs1":
            padding_scheme = padding.PKCS1v15()
        elif self.padding_scheme == "oaep":
            padding_scheme = padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            )

        ciphertext = self.public_key.encrypt(plaintext, padding_scheme)
        return ciphertext

    def rsa_decrypt(self, ciphertext: bytes) -> bytes:
        """
        RSA 解密（使用私钥解密）

        Args:
            ciphertext (bytes): 密文数据

        Returns:
            bytes: 明文数据
        """

        if self.padding_scheme == "pkcs1":
            padding_scheme = padding.PKCS1v15()
        elif self.padding_scheme == "oaep":
            padding_scheme = padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            )

        plaintext = self.private_key.decrypt(ciphertext, padding_scheme)
        return plaintext

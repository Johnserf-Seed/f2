# path: f2/utils/crypto/aes.py

import secrets
from typing import Optional

from cryptography.exceptions import InvalidKey, InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from f2.i18n.translator import _


class AESEncryptionUtils:
    """
    AES加密工具类
    支持AES128, AES192, AES256算法
    支持GCM, CBC, ECB模式
    支持pkcs7填充
    """

    # 支持的加密算法和密钥长度
    SUPPORTED_ALGORITHMS = {
        "AES128": 16,
        "AES192": 24,
        "AES256": 32,
    }

    SUPPORTED_MODES = ["GCM", "CBC", "ECB"]

    def __init__(
        self,
        key: bytes,
        algorithm: str = "AES256",
        mode: str = "GCM",
        padding_scheme: str = "pkcs7",
        iv: Optional[bytes] = None,
    ):
        """
        初始化AES加密工具类实例

        Args:
            key (bytes): 密钥
            algorithm (str, optional): 加密算法
            mode (str, optional): 加密模式 ('GCM', 'CBC', 'ECB')
            padding_scheme (str, optional): 填充方案 ('pkcs7')
            iv (Optional[bytes], optional): IV (初始化向量)

        Raises:
            ValueError: 当算法或模式不可用时抛出错误

        Returns:
            EncryptionUtils: 加密工具类实例
        """
        # 检查算法是否支持
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(_("算法必须为 'AES128', 'AES192' 或 'AES256'。"))

        # 检查模式是否支持
        if mode not in self.SUPPORTED_MODES:
            raise ValueError(_("模式必须为 'GCM', 'CBC' 或 'ECB'。"))

        self.key = key
        self.algorithm = algorithm
        self.mode = mode
        self.padding_scheme = padding_scheme
        self.iv = iv

        # 检查密钥长度是否正确
        expected_key_length = self.SUPPORTED_ALGORITHMS[algorithm]
        if len(self.key) != expected_key_length:
            raise ValueError(
                _("{0} 算法密钥长度不正确：{1} 字节，期望长度为 {2} 字节。").format(
                    algorithm, len(self.key), expected_key_length
                )
            )

    def aes_encrypt(self, plaintext: bytes) -> bytes:
        """
        AES 加密

        Args:
            plaintext (bytes): 明文数据

        Returns:
            bytes: 密文数据
        """
        if self.mode == "GCM":
            return self._aes_encrypt_gcm(plaintext)
        elif self.mode == "CBC":
            return self._aes_encrypt_cbc(plaintext)
        elif self.mode == "ECB":
            return self._aes_encrypt_ecb(plaintext)
        else:
            raise ValueError(_("不支持的加密模式：{0}").format(self.mode))

    def aes_decrypt(self, ciphertext: bytes, iv: Optional[bytes] = None) -> bytes:
        """
        AES 解密

        Args:
            ciphertext (bytes): 密文数据
            iv (Optional[bytes], optional): 用于CBC模式的初始化向量

        Returns:
            bytes: 明文数据
        """
        if self.mode == "GCM":
            return self._aes_decrypt_gcm(ciphertext)
        elif self.mode == "CBC":
            # 确保 CBC 模式下有有效的 IV
            if iv is None:
                iv = self.iv
            if iv is None:
                raise ValueError(_("CBC 模式解密需要提供初始化向量(IV)"))
            return self._aes_decrypt_cbc(ciphertext, iv)
        elif self.mode == "ECB":
            return self._aes_decrypt_ecb(ciphertext)
        else:
            raise ValueError(_("不支持的解密模式：{0}").format(self.mode))

    # 以下是私有方法实现具体加密算法
    def _aes_encrypt_gcm(
        self, plaintext: bytes, nonce: Optional[bytes] = None
    ) -> bytes:
        """GCM模式加密"""
        if nonce is None:
            nonce = self.iv or secrets.token_bytes(12)
        # 为了安全，GCM每次加密都应该生成一个新的随机 12位 nonce
        # 但 Bark 应用不支持随机 nonce 的解密
        # 所以其他开发者在GCM模式的下不需要传入 iv 参数，就会使用随机 nonce
        cipher = Cipher(
            algorithms.AES(self.key), modes.GCM(nonce), backend=default_backend()
        )
        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return nonce + encryptor.tag + ciphertext  # 返回 nonce、tag 和密文

    def _aes_decrypt_gcm(self, ciphertext: bytes) -> bytes:
        """GCM模式解密"""
        nonce = ciphertext[:12]  # 获取 nonce（12 字节）
        tag = ciphertext[12:28]  # 获取认证标签（16 字节）
        ciphertext_data = ciphertext[28:]  # 获取密文

        try:
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(nonce, tag),
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext_data) + decryptor.finalize()
        except InvalidTag:
            raise ValueError(_("GCM 模式解密失败：认证标签无效"))

    def _aes_encrypt_cbc(self, plaintext: bytes) -> bytes:
        """CBC模式加密"""
        if self.iv is None:
            raise ValueError(_("CBC 模式加密需要提供初始化向量(IV)"))

        # 使用 PKCS7 填充
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()

        cipher = Cipher(
            algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext  # 返回密文

    def _aes_decrypt_cbc(self, ciphertext: bytes, iv: bytes) -> bytes:
        """CBC模式解密"""
        cipher = Cipher(
            algorithms.AES(self.key), modes.CBC(iv), backend=default_backend()
        )
        decryptor = cipher.decryptor()

        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # 去除填充
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_plaintext) + unpadder.finalize()

    def _aes_encrypt_ecb(self, plaintext: bytes) -> bytes:
        """ECB模式加密"""
        # 使用 PKCS7 填充
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()

        cipher = Cipher(
            algorithms.AES(self.key), modes.ECB(), backend=default_backend()
        )
        encryptor = cipher.encryptor()

        return encryptor.update(padded_data) + encryptor.finalize()

    def _aes_decrypt_ecb(self, ciphertext: bytes) -> bytes:
        """ECB模式解密"""
        cipher = Cipher(
            algorithms.AES(self.key), modes.ECB(), backend=default_backend()
        )
        decryptor = cipher.decryptor()

        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # 去除填充
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_plaintext) + unpadder.finalize()

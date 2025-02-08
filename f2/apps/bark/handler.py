# path: f2/apps/bark/handler.py

import json
import traceback

from typing import Dict
from base64 import b64encode

from f2.log.logger import logger, trace_logger
from f2.i18n.translator import _
from f2.utils.decorators import mode_handler, mode_function_map
from f2.utils.utils import AESEncryptionUtils
from f2.apps.bark.crawler import BarkCrawler
from f2.apps.bark.model import BarkModel, BarkCipherModel
from f2.apps.bark.filter import BarkNotificationFilter
from f2.apps.bark.utils import generate_numeric_bytes
from f2.apps.bark.utils import ClientConfManager


class BarkHandler:

    def __init__(self, kwargs: Dict = {}) -> None:
        self.kwargs = kwargs

    async def _send_bark_notification(self, send_method: str) -> BarkNotificationFilter:
        """
        发送Bark通知的辅助方法。

        Args:
            send_method (str): 调用的发送方法（"fetch" 或 "post"）
            kwargs (Dict): 通知参数

        Returns:
            BarkNotificationFilter: 处理后的Bark通知过滤结果
        """
        logger.debug(_("正在发送 Bark 通知"))

        # 获取并确保 body 存在
        self.kwargs["body"] = self.kwargs.get("body", _("无内容"))

        try:
            async with BarkCrawler(self.kwargs) as crawler:
                params = BarkModel(**self.kwargs)
                # 动态调用发送方法
                if send_method == "fetch":
                    response = await crawler.fetch_bark_notification(params)
                elif send_method == "post":
                    response = await crawler.post_bark_notification(params)
                else:
                    raise ValueError(_("无效的发送方法：{0}").format(send_method))

                bark = BarkNotificationFilter(response)
                # 原本status_code应该放接口code中，但由于bark接口将响应的状态码直接设置为了响应的code
                # 所以这里不判断code
                logger.info(_("Bark通知发送成功，时间：{0}").format(bark.timestamp))
                logger.debug(_("Bark通知内容：{0}").format(self.kwargs["body"]))
                return bark

        except Exception as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("Bark 通知发送失败，请检查 key 和网络连接：{0}").format(e))

        return None

    @mode_handler("get")
    async def fetch_bark_notification(self) -> BarkNotificationFilter:
        """用于发送Bark通知 (fetch 方式)"""
        return await self._send_bark_notification("fetch")

    @mode_handler("post")
    async def post_bark_notification(self) -> BarkNotificationFilter:
        """用于发送Bark通知 (post 方式)"""
        return await self._send_bark_notification("post")

    @mode_handler("cipher")
    async def cipher_bark_notification(self) -> BarkNotificationFilter:
        """用于发送加密 Bark 通知"""

        logger.debug(_("正在发送 Bark 加密通知"))

        # 获取 Bark 加密设置参数
        encryption = self.kwargs.get("encryption")
        if not encryption:
            raise ValueError(_("Bark 加密配置缺失"))

        # 获取并检查加密算法相关参数
        aes_algo = encryption.get("algorithm")
        if not aes_algo:
            raise ValueError(_("加密算法缺失"))

        aes_mode = encryption.get("mode")
        if not aes_mode:
            raise ValueError(_("加密模式缺失"))

        aes_padding = encryption.get("padding")
        aes_key = encryption.get("key")
        if not aes_key:
            raise ValueError(_("加密密钥缺失"))

        aes_key = aes_key.encode("utf-8")

        # 根据加密模式生成不同位数的 IV
        if aes_mode == "ECB":
            aes_iv = None
        elif aes_mode == "CBC":
            aes_iv = generate_numeric_bytes(16)
        elif aes_mode == "GCM":
            aes_iv = generate_numeric_bytes(12)
        else:
            raise ValueError(_("无效的加密模式：{0}").format(aes_mode))

        # 初始化 AES 加密工具并校验参数
        aes = AESEncryptionUtils(
            key=aes_key,
            algorithm=aes_algo,
            mode=aes_mode,
            padding_scheme=aes_padding,
            iv=aes_iv,
        )

        try:
            async with BarkCrawler(self.kwargs) as crawler:
                # 对原始 params 进行加密
                plaintext = json.dumps(
                    BarkModel(**self.kwargs).model_dump(), ensure_ascii=False
                ).encode("utf-8")
                encrypted_params = aes.aes_encrypt(plaintext)

                # 需要将随机生成的 IV 一并发送
                cipher_params = BarkCipherModel(
                    ciphertext=b64encode(encrypted_params).decode("utf-8"),
                    iv="".join(chr(b) for b in aes.iv) if aes.iv else "",
                )

                response = await crawler.cipher_bark_notification(cipher_params)
                bark = BarkNotificationFilter(response)

                logger.info(
                    _("Bark 加密通知发送成功，时间：{0}").format(bark.timestamp)
                )
                logger.debug(_("Bark 加密通知内容：{0}").format(self.kwargs["body"]))
                return bark
        except Exception as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("Bark 通知发送失败，请检查 key 和网络连接：{0}").format(e))

    async def send_quick_notification(
        self,
        title: str,
        body: str,
        send_method: str = "fetch",
        **kwargs,
    ) -> BarkNotificationFilter:
        """
        用于发送Bark通知的快捷方法

        Args:
            title (str): 通知标题
            body (str): 通知内容
            send_method (str): 调用的发送方法（"fetch" 或 "post"）
            kwargs (Dict): 其他通知参数

        Returns:
            BarkNotificationFilter: Bark通知过滤器，包含结果数据的_to_raw()、_to_dict()方法
        """
        self.kwargs.update({"title": title, "body": body, **kwargs})

        # 获取加密配置
        encryption = kwargs.get("encryption") or {}

        # 检查是否启用加密通知并设置了加密密钥
        if ClientConfManager.enable_encryption() and encryption.get("key"):
            logger.debug(_("已设置加密密钥，使用加密通知"))
            return await self.cipher_bark_notification()

        # 使用普通通知
        logger.debug(_("未设置加密密钥，改用普通通知"))
        return await self._send_bark_notification(send_method)


async def main(kwargs):
    mode = kwargs.get("mode")
    if mode in mode_function_map:
        await mode_function_map[mode](BarkHandler(kwargs))
    else:
        logger.error(_("不存在该模式：{0}").format(mode))

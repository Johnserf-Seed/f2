# path: f2/apps/bark/handler.py

from typing import Dict

from f2.log.logger import logger
from f2.i18n.translator import _
from f2.utils.decorators import mode_handler, mode_function_map
from f2.apps.bark.crawler import BarkCrawler
from f2.apps.bark.model import BarkModel
from f2.apps.bark.filter import BarkNotificationFilter


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
        logger.info(_("正在发送Bark通知"))

        # 获取并确保 body 存在
        self.kwargs["body"] = self.kwargs.get("body", "无内容")

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
                logger.info(
                    _("Bark通知发送成功，内容：{0}，时间：{1}").format(
                        self.kwargs["body"], bark.timestamp
                    )
                )
                return bark

        except Exception as e:
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
        return await self._send_bark_notification(send_method)


async def main(kwargs):
    mode = kwargs.get("mode")
    if mode in mode_function_map:
        await mode_function_map[mode](BarkHandler(kwargs))
    else:
        logger.error(_("不存在该模式：{0}").format(mode))

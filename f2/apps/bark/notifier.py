# path: f2/apps/bark/notifier.py

import traceback
from typing import Any

from f2.apps.bark.handler import BarkHandler
from f2.apps.bark.utils import ClientConfManager
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.core.run_report import Notifier, NullNotifier


class BarkNotifier:
    """
    通过 Bark 发送运行通知 (Send run notifications through Bark)

    每条通知都用新的参数发送，互不影响；发送失败只记录日志，不影响下载。
    """

    def __init__(self, conf: dict, send_method: str = "post") -> None:
        self.conf = dict(conf)
        self.send_method = send_method

    async def send(self, title: str, body: str, **options: Any) -> None:
        try:
            await BarkHandler(self.conf).send_quick_notification(
                title, body, send_method=self.send_method, **options
            )
        except Exception as e:
            trace_logger.error(traceback.format_exc())
            logger.error(_("Bark 通知发送失败，请检查 key 和网络连接：{0}").format(e))


def notifier_from_config() -> Notifier:
    """
    按配置创建通知对象 (Create the notifier from the configuration)

    开启 enable_bark 时返回 BarkNotifier，否则返回什么也不做的 NullNotifier，
    调用方不必再判断是否开启了通知。
    """
    if not ClientConfManager.enable_bark():
        return NullNotifier()
    return BarkNotifier(ClientConfManager.merge())

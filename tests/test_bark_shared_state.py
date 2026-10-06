# path: tests/test_bark_shared_state.py

import asyncio

from f2.apps.bark import handler as bark_handler


async def test_quick_notifications_do_not_share_parameters(monkeypatch):
    # 此前 send_quick_notification 把标题、正文与额外参数写回 self.kwargs，
    # 上一条通知的参数会带到下一条
    sent = []

    async def fake_send(self, send_method, params=None):
        sent.append(params if params is not None else dict(self.kwargs))

    monkeypatch.setattr(bark_handler.BarkHandler, "_send_bark_notification", fake_send)
    handler = bark_handler.BarkHandler({"key": "k", "group": "F2"})

    await handler.send_quick_notification("一", "正文一", url="https://a.example")
    await handler.send_quick_notification("二", "正文二")

    assert sent[0]["url"] == "https://a.example"
    assert "url" not in sent[1]
    assert (sent[1]["title"], sent[1]["body"]) == ("二", "正文二")
    assert handler.kwargs == {"key": "k", "group": "F2"}


async def test_concurrent_quick_notifications_keep_their_own_text(monkeypatch):
    # 此前同一个实例并发发送时，后一条的标题与正文会覆盖前一条
    sent = []

    async def fake_send(self, send_method, params=None):
        await asyncio.sleep(0)
        sent.append((params if params is not None else self.kwargs)["title"])

    monkeypatch.setattr(bark_handler.BarkHandler, "_send_bark_notification", fake_send)
    handler = bark_handler.BarkHandler({"key": "k"})

    await asyncio.gather(
        handler.send_quick_notification("一", "正文"),
        handler.send_quick_notification("二", "正文"),
    )

    assert sorted(sent) == ["一", "二"]

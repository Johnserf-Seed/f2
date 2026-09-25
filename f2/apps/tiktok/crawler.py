# path: f2/apps/tiktok/crawler.py

import asyncio
import gzip
import json
import traceback
from typing import Any, Optional, Union

from google.protobuf import json_format
from google.protobuf.message import DecodeError as ProtoDecodeError
from websockets import (
    ConnectionClosedOK,
    WebSocketServer,
    WebSocketServerProtocol,
    serve,
)

from f2.apps.tiktok.api import TiktokAPIEndpoints as tkendpoint
from f2.apps.tiktok.model import (
    CheckLiveAlive,
    LiveImFetch,
    LiveWebcast,
    PostComment,
    PostDetail,
    PostSearch,
    UserCollect,
    UserLike,
    UserLive,
    UserMix,
    UserPlayList,
    UserPost,
    UserProfile,
)
from f2.apps.tiktok.proto.tiktok_webcast_pb2 import (
    ChatMessage,
    GiftMessage,
    LikeMessage,
    LinkLayerMessage,
    LinkMessage,
    LinkMicBattle,
    LinkMicFanTicketMethod,
    LinkMicMethod,
    MemberMessage,
    OecLiveShoppingMessage,
    PushFrame,
    Response,
    RoomMessage,
    RoomUserSeqMessage,
    SocialMessage,
    UserFanTicket,
)
from f2.apps.tiktok.utils import ClientConfManager, XBogusManager
from f2.crawlers.base_crawler import BaseCrawler
from f2.crawlers.websocket_crawler import WebSocketCrawler
from f2.i18n.translator import _
from f2.log.logger import logger, trace_logger
from f2.utils.http.endpoint import BaseEndpointManager


class TiktokCrawler(BaseCrawler):
    def __init__(
        self,
        kwargs: Optional[dict] = None,
    ):
        # 需要与cli同步
        kwargs = kwargs or {}
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        self.headers = kwargs.get("headers", {}) | {"Cookie": kwargs["cookie"]}
        super().__init__(kwargs=kwargs, proxies=proxies, crawler_headers=self.headers)

    async def fetch_user_profile(self, params: UserProfile):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_DETAIL,
            params.model_dump(),
        )
        logger.debug(_("用户信息接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_post(self, params: UserPost):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_POST,
            params.model_dump(),
        )
        logger.debug(_("主页作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_like(self, params: UserLike):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_LIKE,
            params.model_dump(),
        )
        logger.debug(_("喜欢作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collect(self, params: UserCollect):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_COLLECT,
            params.model_dump(),
        )
        logger.debug(_("收藏作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_play_list(self, params: UserPlayList):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_PLAY_LIST,
            params.model_dump(),
        )
        logger.debug(_("合集列表接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_mix(self, params: UserMix):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_MIX,
            params.model_dump(),
        )
        logger.debug(_("合集作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_detail(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.AWEME_DETAIL,
            params.model_dump(),
        )
        logger.debug(_("作品详情接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_comment(self, params: PostComment):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.POST_COMMENT,
            params.model_dump(),
        )
        logger.debug(_("作品评论接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_recommend(self, params: PostDetail):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.HOME_RECOMMEND,
            params.model_dump(),
        )
        logger.debug(_("首页推荐接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_search(self, params: PostSearch):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.POST_SEARCH,
            params.model_dump(),
        )
        logger.debug(_("搜索作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_live(self, params: UserLive):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.USER_LIVE,
            params.model_dump(),
        )
        logger.debug(_("用户直播接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_check_live_alive(self, params: CheckLiveAlive):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.CHECK_LIVE_ALIVE,
            params.model_dump(),
        )
        logger.debug(_("检查开播状态接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_live_im_fetch(self, params: LiveImFetch):
        endpoint = XBogusManager.model_2_endpoint(
            self.headers.get("User-Agent"),
            tkendpoint.LIVE_IM_FETCH,
            params.model_dump(),
        )
        logger.debug(_("直播弹幕初始化接口地址：{0}").format(endpoint))
        response = await self._fetch_response(endpoint)
        payload_package = Response()
        payload_package.ParseFromString(response.content)
        return payload_package

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class TiktokWebSocketCrawler(WebSocketCrawler):
    # 是否显示直播间消息
    show_message = False

    def __init__(self, kwargs: Optional[dict] = None, callbacks: dict = {}):
        # 需要与cli同步
        kwargs = kwargs or {}
        self.__class__.show_message = bool(kwargs.get("show_message", True))
        self.headers = kwargs.get("headers", {}) | {"Cookie": kwargs.get("cookie", {})}
        self.callbacks = callbacks or {}
        self.timeout = kwargs.get("timeout", 10)
        self.connected_clients: set[WebSocketServerProtocol] = set()  # 管理连接的客户端
        super().__init__(
            wss_headers=self.headers,
            callbacks=self.callbacks,
            timeout=self.timeout,
            proxy=kwargs.get("proxies", {"http://": None, "https://": None}).get(
                "http://"
            ),
        )

    @classmethod
    def _log(cls, message, level="info"):
        """控制消息日志输出的辅助方法"""
        if cls.show_message:
            getattr(logger, level)(message)

    async def fetch_live_danmaku(self, params: LiveWebcast):
        endpoint = BaseEndpointManager.model_2_endpoint(
            tkendpoint.LIVE_IM_WSS,
            params.model_dump(),
        )
        logger.debug(_("直播弹幕接口地址：{0}").format(endpoint))
        await self.connect_websocket(endpoint)

        server_task = asyncio.create_task(self.start_server())
        try:
            return await self.receive_messages()
        finally:
            server_task.cancel()  # 确保在完成时取消服务器任务
            try:
                await server_task
            except asyncio.CancelledError:
                pass  # 抑制 CancelledError 异常

    async def handle_wss_message(self, message: bytes):
        """
        处理 WebSocket 消息

        Args:
            message (bytes): WebSocket 消息的字节数据
        """
        try:
            wss_package = PushFrame()
            wss_package.ParseFromString(message)

            logger.debug(_("[WssPackage] [📦Wss包] | [{0}]").format(wss_package))

            # 检查数据是否为 gzip 格式
            if wss_package.payload[:2] == b"\x1f\x8b":
                try:
                    decompressed = gzip.decompress(wss_package.payload)
                except gzip.BadGzipFile:
                    trace_logger.error(traceback.format_exc())
                    return
            else:
                logger.warning(_("解压缩数据时出错，数据不是 gzip 格式，无法解压缩"))
                decompressed = wss_package.payload

            payload_package = Response()
            payload_package.ParseFromString(decompressed)

            logger.debug(
                _("[PayloadPackage] [📦Payload包] | [{0}]").format(payload_package)
            )

            # 发送 ack 包
            if payload_package.needAck:
                await self.send_ack(wss_package.logid, payload_package.internalExt)

            # 处理每个消息
            tasks = []
            for msg in payload_package.messages:
                method = msg.method
                payload = msg.payload

                # 调用对应的回调函数处理消息
                if method in self.callbacks:
                    # 创建异步任务
                    tasks.append(self.callbacks[method](data=payload))
                else:
                    logger.warning(
                        _(
                            "[HandleWssMessage] [❌未找到对应的回调函数] | [方法：{0}]"
                        ).format(method)
                    )

            # 并发运行所有回调
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # 处理每个任务的结果
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(
                            _(
                                "[HandleWssMessage] [⚠️ 回调执行出错] | [方法：{0}] | [错误：{1}]"
                            ).format(payload_package.messages[i].method, result)
                        )
                    else:
                        if result is not None:
                            # 转发处理后的数据
                            await self.broadcast_message(result)

            # 增加保活机制
            await self.send_ack(wss_package.logid, payload_package.internalExt)

        except ProtoDecodeError as e:
            logger.error(
                _(
                    "[HandleWssMessage] [❌ 解析消息格式出错] | [错误：{0}] | [消息：{1}]"
                ).format(e, message)
            )

        except Exception:
            trace_logger.error(traceback.format_exc())
            logger.error(
                _("[HandleWssMessage] [⚠️ 处理消息出错] | [错误：{0}]").format(
                    traceback.format_exc()
                )
            )

    async def send_ack(self, log_id: int, internal_ext: str) -> None:
        """
        发送 ack 包

        Args:
            log_id: 日志ID
            internal_ext: 内部扩展信息
        """
        if self.websocket is None:
            logger.warning(_("[SendAck] [❌ 无法发送 ack 包] | [WebSocket 未连接]"))
            return

        ack = PushFrame()
        ack.logid = log_id
        ack.payload_type = internal_ext
        data = ack.SerializeToString()
        logger.debug(_("[SendAck] [💓 发送 ack 包] | [日志ID：{0}]").format(log_id))
        await self.websocket.send(data)

    async def send_ping(self) -> None:
        """
        发送 ping 包
        """
        if self.websocket is None:
            logger.warning(_("[SendPing] [❌ 无法发送 ping 包] | [WebSocket 未连接]"))
            return

        ping = PushFrame()
        ping.payload_type = "hb"
        data = ping.SerializeToString()
        self._waiting_for_pong = True
        logger.debug(_("[SendPing] [📤发送ping包]"))
        await self.websocket.ping(data)

    async def on_message(self, message):
        await self.handle_wss_message(message)

    async def on_error(self, message):
        return await super().on_error(message)

    async def on_close(self, message):
        return await super().on_close(message)

    async def on_open(self):
        return await super().on_open()

    async def start_server(self) -> None:
        """启动 WebSocket 服务器"""
        wss_conf = ClientConfManager.wss()
        wss_domain = wss_conf.get("domain")
        wss_port = wss_conf.get("port")
        # wss_verify = wss_conf.get("verify")
        # 暂不支持wss本地证书验证

        try:
            server = await serve(self.register_client, wss_domain, wss_port)
            logger.info(
                _(
                    "[StartServer] [🚀本地 WebSocket 服务器已启动] ｜ 连接地址：ws://{0}:{1}"
                ).format(wss_domain, wss_port)
            )
            await self._timeout_check(server)
            await asyncio.Future()  # 这里保持服务器运行
        except asyncio.CancelledError:
            logger.warning(_("[StartServer] [⚠️ 服务器任务被取消]"))
        except Exception as exc:
            trace_logger.error(traceback.format_exc())
            logger.error(
                _("[StartServer] [❌ 服务器启动失败] | [错误：{0}]").format(exc)
            )
        finally:
            server.close()
            await server.wait_closed()
            logger.info(_("[StartServer] [🔒 本地 WebSocket 服务器已关闭]"))

    async def _timeout_check(self, server: WebSocketServer) -> None:
        """
        检查本地服务器是否超时无连接

        Args:
            server: WebSocketServer 对象
        """

        while True:
            await asyncio.sleep(self.timeout)
            if not self.connected_clients:
                logger.info(
                    _(
                        "[TimeoutCheck] [⏳ 无客户端连接超时关闭] | [超时时间：{0} 秒]"
                    ).format(self.timeout)
                )
                break
        server.close()
        # await server.wait_closed()
        await self.close_websocket()

    async def register_client(self, websocket: WebSocketServerProtocol) -> None:
        """
        注册新的客户端连接

        Args:
            websocket: WebSocketServerProtocol 实例
        """

        self.connected_clients.add(websocket)
        logger.info(
            _("[RegisterClient] [🔗 新的客户端连接] ｜ [Ip：{0} Port：{1}]").format(
                *websocket.remote_address
            )
        )
        try:
            async for message in websocket:
                # TODO: 处理客户端消息或鉴权
                pass
        except ConnectionClosedOK:
            logger.info(
                _("[RegisterClient] [⛓ 客户端断开连接] | [Ip：{0} Port：{1}]").format(
                    *websocket.remote_address
                )
            )
        finally:
            self.connected_clients.remove(websocket)

    async def broadcast_message(self, message: Union[str, dict, list, Any]) -> None:
        """
        转发消息给所有连接的客户端

        Args:
            message: 要转发的消息（字符串格式）
        """

        if not isinstance(message, str):
            try:
                message = json.dumps(message, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError) as exc:
                logger.error(
                    _("[BroadcastMessage] [❌ 消息格式错误] | [错误：{0}]").format(exc)
                )
                return

        tasks = [client.send(message) for client in self.connected_clients]
        await asyncio.gather(*tasks, return_exceptions=True)

    @classmethod
    async def WebcastChatMessage(cls, data: bytes) -> dict:
        """
        处理直播间消息

        Args:
            data (bytes): 直播间消息的字节数据

        Returns:
            dict: 直播间消息的 JSON 数据
        """

        chatMessage = ChatMessage()
        chatMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                chatMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        nick_name = data_json.get("user").get("nickname")
        content = data_json.get("content")

        cls._log(
            _("[WebcastChatMessage] [💬直播间消息] [用户：{0} 说：{1}]").format(
                nick_name, content
            )
        )
        return data_json

    @classmethod
    async def WebcastMemberMessage(cls, data: bytes) -> dict:
        """
        处理直播间成员消息

        Args:
            data (bytes): 直播间成员消息的字节数据

        Returns:
            dict: 直播间成员消息的 JSON 数据
        """

        memberMessage = MemberMessage()
        memberMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                memberMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        nick_name = data_json.get("user").get("nickname")

        cls._log(
            _(
                "[WebcastMemberMessage] [👥直播间成员消息] [用户：{0} 加入了直播间]"
            ).format(nick_name)
        )
        return data_json

    @classmethod
    async def WebcastRoomUserSeqMessage(cls, data: bytes) -> dict:
        """
        处理直播间用户序列消息

        Args:
            data (bytes): 直播间用户序列消息的字节数据

        Returns:
            dict: 直播间用户序列消息的 JSON 数据
        """

        roomUserSeqMessage = RoomUserSeqMessage()
        roomUserSeqMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                roomUserSeqMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        ranks = data_json.get("ranks")
        if not ranks:
            cls._log(_("[WebcastRoomUserSeqMessage] [👥在线观众排行榜] | [无数据]"))
            return data_json
        else:
            top_users = ", ".join(
                _("用户ID：{0}").format(rank.get("user", {}).get("id"))
                for rank in ranks
            )

            cls._log(
                _("[WebcastRoomUserSeqMessage] [👥在线观众排行榜] | [{0}]").format(
                    top_users
                )
            )
        return data_json

    @classmethod
    async def WebcastGiftMessage(cls, data: bytes) -> dict:
        """
        处理直播间礼物消息

        Args:
            data (bytes): 直播间礼物消息的字节数据

        Returns:
            dict: 直播间礼物消息的 JSON 数据
        """

        giftMessage = GiftMessage()
        giftMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                giftMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        nick_name = data_json.get("user").get("nickname", "N/A")
        gift_name = data_json.get("gift").get("describe", "N/A")
        gift_price = data_json.get("gift").get("diamondCount", "N/A")

        cls._log(
            _(
                "[WebcastGiftMessage] [🎁直播间礼物] [用户：{0} 送出了 {1} 价值 {2} 钻石]"
            ).format(nick_name, gift_name, gift_price)
        )
        return data_json

    @classmethod
    async def WebcastSocialMessage(cls, data: bytes) -> dict:
        """
        处理直播间社交消息

        Args:
            data (bytes): 直播间社交消息的字节数据

        Returns:
            dict: 直播间社交消息的 JSON 数据
        """

        socialMessage = SocialMessage()
        socialMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                socialMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        nick_name = data_json.get("user").get("nickname")

        cls._log(
            _("[WebcastSocialMessage] [➕观众关注] [用户：{0} 关注了主播]").format(
                nick_name
            )
        )
        return data_json

    @classmethod
    async def WebcastLikeMessage(cls, data: bytes) -> dict:
        """
        处理直播间点赞消息

        Args:
            data (bytes): 直播间点赞消息的字节数据

        Returns:
            dict: 直播间点赞消息的 JSON 数据
        """

        likeMessage = LikeMessage()
        likeMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                likeMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        nick_name = data_json.get("user").get("nickname")

        cls._log(
            _("[WebcastLikeMessage] [❤️观众点赞] [用户：{0} 点赞了直播间]").format(
                nick_name
            )
        )
        return data_json

    @classmethod
    async def WebcastLinkMicFanTicketMethod(cls, data: bytes) -> dict:
        """
        处理直播间连麦粉丝票消息

        Args:
            data (bytes): 直播间连麦粉丝票消息的字节数据

        Returns:
            dict: 直播间连麦粉丝票消息的 JSON 数据
        """

        linkMicFanTicketMethod = LinkMicFanTicketMethod()
        linkMicFanTicketMethod.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                linkMicFanTicketMethod,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(
            _("[WebcastLinkMicFanTicketMethod] [🎟️连麦粉丝票] {0}").format(data_json)
        )
        return data_json

    @classmethod
    async def WebcastLinkMicMethod(cls, data: bytes) -> dict:
        """
        处理直播间连麦消息

        Args:
            data (bytes): 直播间连麦消息的字节数据

        Returns:
            dict: 直播间连麦消息的 JSON 数据
        """

        linkMicMethod = LinkMicMethod()
        linkMicMethod.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                linkMicMethod,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(_("[WebcastLinkMicMethod] [🎤连麦消息] {0}").format(data_json))
        return data_json

    @classmethod
    async def UserFanTicket(cls, data: bytes) -> dict:
        """
        处理直播间用户粉丝票消息

        Args:
            data (bytes): 直播间用户粉丝票消息的字节数据

        Returns:
            dict: 直播间用户粉丝票消息的 JSON 数据
        """

        userFanTicket = UserFanTicket()
        userFanTicket.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                userFanTicket,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(_("[WebcastUserFanTicket] [🎟️用户粉丝团] {0}").format(data_json))
        return data_json

    @classmethod
    async def WebcastLinkMessage(cls, data: bytes) -> dict:
        """
        处理直播间连麦消息

        Args:
            data (bytes): 直播间连麦消息的字节数据

        Returns:
            dict: 直播间连麦消息的 JSON 数据
        """

        linkMessage = LinkMessage()
        linkMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                linkMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(_("[WebcastLinkMessage] [🎤连麦消息] {0}").format(data_json))
        return data_json

    @classmethod
    async def WebcastLinkMicBattle(cls, data: bytes) -> dict:
        """
        处理直播间连麦对决消息

        Args:
            data (bytes): 直播间连麦对决消息的字节数据

        Returns:
            dict: 直播间连麦对决消息的 JSON 数据
        """

        linkMicBattle = LinkMicBattle()
        linkMicBattle.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                linkMicBattle,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(_("[WebcastLinkMicBattle] [🎤连麦对决] {0}").format(data_json))
        return data_json

    @classmethod
    async def WebcastLinkLayerMessage(cls, data: bytes) -> dict:
        """
        处理直播间连麦对决消息

        Args:
            data (bytes): 直播间连麦层消息的字节数据

        Returns:
            dict: 直播间连麦层消息的 JSON 数据
        """

        linkLayerMessage = LinkLayerMessage()
        linkLayerMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                linkLayerMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(_("[WebcastLinkLayerMessage] [🎤连麦层信息] {0}").format(data_json))
        return data_json

    @classmethod
    async def WebcastRoomMessage(cls, data: bytes) -> dict:
        """
        处理直播间消息

        Args:
            data (bytes): 直播间消息的字节数据

        Returns:
            dict: 直播间消息的 JSON 数据
        """

        roomMessage = RoomMessage()
        roomMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                roomMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(_("[WebcastRoomMessage] [📜直播间消息] {0}").format(data_json))
        return data_json

    @classmethod
    async def WebcastOecLiveShoppingMessage(cls, data: bytes) -> dict:
        """
        处理直播间消息

        Args:
            data (bytes): 直播间消息的字节数据

        Returns:
            dict: 直播间消息的 JSON 数据
        """

        oecLiveShoppingMessage = OecLiveShoppingMessage()
        oecLiveShoppingMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                oecLiveShoppingMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(
            _("[WebcastOecLiveShoppingMessage] [🛍️直播间购物消息] {0}").format(
                data_json
            )
        )
        return data_json

    async def __aenter__(self):
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

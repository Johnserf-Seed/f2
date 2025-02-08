# path: f2/apps/douyin/crawler.py

import json
import gzip
import asyncio
import traceback

from typing import Dict
from google.protobuf import json_format
from google.protobuf.message import DecodeError as ProtoDecodeError
from websockets import (
    ConnectionClosedOK,
    WebSocketServerProtocol,
    WebSocketServer,
    serve,
)

from f2.log.logger import logger, trace_logger
from f2.i18n.translator import _
from f2.crawlers.base_crawler import BaseCrawler, WebSocketCrawler
from f2.utils.utils import BaseEndpointManager
from f2.apps.douyin.api import DouyinAPIEndpoints as dyendpoint
from f2.apps.douyin.model import (
    UserProfile,
    UserPost,
    UserLike,
    UserCollection,
    UserCollects,
    UserCollectsVideo,
    UserMusicCollection,
    PostDetail,
    UserMix,
    UserLive,
    UserLive2,
    FollowingUserLive,
    LoginGetQr,
    LoginCheckQr,
    UserFollowing,
    UserFollower,
    LiveWebcast,
    LiveImFetch,
    QueryUser,
    PostStats,
)
from f2.apps.douyin.utils import (
    XBogusManager,
    ABogusManager,
    ClientConfManager,
    TokenManager,
)
from f2.apps.douyin.proto.douyin_webcast_pb2 import (
    PushFrame,
    Response,
    RoomMessage,
    LikeMessage,
    MemberMessage,
    ChatMessage,
    GiftMessage,
    SocialMessage,
    RoomUserSeqMessage,
    UpdateFanTicketMessage,
    CommonTextMessage,
    MatchAgainstScoreMessage,
    EcomFansClubMessage,
    RoomStatsMessage,
    LiveShoppingMessage,
    LiveEcomGeneralMessage,
    RoomStreamAdaptationMessage,
    RanklistHourEntranceMessage,
    ProductChangeMessage,
    NotifyEffectMessage,
    LightGiftMessage,
    ProfitInteractionScoreMessage,
    RoomRankMessage,
    FansclubMessage,
    HotRoomMessage,
    InRoomBannerMessage,
    ScreenChatMessage,
    RoomDataSyncMessage,
    LinkerContributeMessage,
    EmojiChatMessage,
    LinkMicMethod,
    LinkMessage,
    BattleTeamTaskMessage,
    HotChatMessage,
)


class DouyinCrawler(BaseCrawler):
    def __init__(
        self,
        kwargs: Dict = ...,
    ):
        # 需要与cli同步
        proxies = kwargs.get("proxies", {"http://": None, "https://": None})
        self.headers = kwargs.get("headers", {}) | {"Cookie": kwargs["cookie"]}
        if ClientConfManager.encryption() == "ab":
            self.bogus_manager = ABogusManager
        else:
            self.bogus_manager = XBogusManager
        super().__init__(kwargs, proxies=proxies, crawler_headers=self.headers)

    async def fetch_user_profile(self, params: UserProfile):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_DETAIL,
            params.model_dump(),
        )
        logger.debug(_("用户信息接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_post(self, params: UserPost):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_POST,
            params.model_dump(),
        )
        logger.debug(_("主页作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_like(self, params: UserLike):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_FAVORITE_A,
            params.model_dump(),
        )
        logger.debug(_("主页喜欢作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collection(self, params: UserCollection):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_COLLECTION,
            params.model_dump(),
        )
        logger.debug(_("主页收藏作品接口地址：{0}").format(endpoint))
        return await self._fetch_post_json(endpoint, params.model_dump())

    async def fetch_user_collects(self, params: UserCollects):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_COLLECTS,
            params.model_dump(),
        )
        logger.debug(_("收藏夹接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_collects_video(self, params: UserCollectsVideo):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_COLLECTS_VIDEO,
            params.model_dump(),
        )
        logger.debug(_("收藏夹作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_music_collection(self, params: UserMusicCollection):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_MUSIC_COLLECTION,
            params.model_dump(),
        )
        logger.debug(_("音乐收藏接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_mix(self, params: UserMix):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.MIX_AWEME,
            params.model_dump(),
        )
        logger.debug(_("合集作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_detail(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.POST_DETAIL,
            params.model_dump(),
        )
        logger.debug(_("作品详情接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_comment(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.POST_COMMENT,
            params.model_dump(),
        )
        logger.debug(_("作品评论接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_feed(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.TAB_FEED,
            params.model_dump(),
        )
        logger.debug(_("首页推荐作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_follow_feed(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.FOLLOW_FEED,
            params.model_dump(),
        )
        logger.debug(_("关注作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_friend_feed(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.FRIEND_FEED,
            params.model_dump(),
        )
        logger.debug(_("朋友作品接口地址：{0}").format(endpoint))
        return await self._fetch_post_json(endpoint)

    async def fetch_post_related(self, params: PostDetail):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.POST_RELATED,
            params.model_dump(),
        )
        logger.debug(_("相关推荐作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_live(self, params: UserLive):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.LIVE_INFO,
            params.model_dump(),
        )
        logger.debug(_("直播信息接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_live_room_id(self, params: UserLive2):
        original_headers = self.aclient.headers.copy()
        try:
            # 避免invalid session
            self.aclient.headers.update({"Cookie": ""})
            endpoint = self.bogus_manager.model_2_endpoint(
                self.headers.get("User-Agent"),
                dyendpoint.LIVE_INFO_ROOM_ID,
                params.model_dump(),
            )
            logger.debug(_("直播接口地址（room_id）：{0}").format(endpoint))
            return await self._fetch_get_json(endpoint)
        finally:
            self.aclient.headers = original_headers

    async def fetch_following_live(self, params: FollowingUserLive):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.FOLLOW_USER_LIVE,
            params.model_dump(),
        )
        logger.debug(_("关注用户直播接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_locate_post(self, params: UserPost):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.LOCATE_POST,
            params.model_dump(),
        )
        logger.debug(_("定位上一次作品接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_login_qrcode(self, parms: LoginGetQr):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.SSO_LOGIN_GET_QR,
            parms.model_dump(),
        )
        logger.debug(_("SSO获取二维码接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_check_qrcode(self, parms: LoginCheckQr):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.SSO_LOGIN_CHECK_QR,
            parms.model_dump(),
        )
        logger.debug(_("SSO检查扫码状态接口地址：{0}").format(endpoint))
        return await self._fetch_response(endpoint)

    async def fetch_check_login(self, parms: LoginCheckQr):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.SSO_LOGIN_CHECK_LOGIN,
            parms.model_dump(),
        )
        logger.debug(_("SSO检查登录状态接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_following(self, params: UserFollowing):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_FOLLOWING,
            params.model_dump(),
        )
        logger.debug(_("用户关注列表接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_user_follower(self, params: UserFollower):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.USER_FOLLOWER,
            params.model_dump(),
        )
        logger.debug(_("用户粉丝列表接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_live_im_fetch(self, params: LiveImFetch):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.LIVE_IM_FETCH,
            params.model_dump(),
        )
        logger.debug(_("直播弹幕初始化接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_query_user(self, params: QueryUser):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.QUERY_USER,
            params.model_dump(),
        )
        logger.debug(_("查询用户接口地址：{0}").format(endpoint))
        return await self._fetch_get_json(endpoint)

    async def fetch_post_stats(self, params: PostStats):
        endpoint = self.bogus_manager.model_2_endpoint(
            self.headers.get("User-Agent"),
            dyendpoint.POST_STATS,
            params.model_dump(),
        )
        logger.debug(_("作品统计接口地址：{0}").format(endpoint))
        return await self._fetch_post_json(endpoint, params.model_dump())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class DouyinWebSocketCrawler(WebSocketCrawler):
    # 是否显示直播间消息
    show_message = False

    def __init__(self, kwargs: Dict = ..., callbacks: Dict = None):
        self.__class__.show_message = bool(kwargs.get("show_message", True))
        # 需要与cli同步
        self.headers = kwargs.get("headers", {}) | {
            "Cookie": f"ttwid={TokenManager.gen_ttwid()};"
        }
        self.callbacks = callbacks or {}
        self.timeout = kwargs.get("timeout", 10)
        self.connected_clients = set()  # 管理连接的客户端
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

    async def fetch_live_danmaku(self, params: LiveWebcast) -> None:
        endpoint = BaseEndpointManager.model_2_endpoint(
            dyendpoint.LIVE_IM_WSS,
            params.model_dump(),
        )
        logger.debug(
            _("[FetchLiveDanmaku] [🔗 直播弹幕接口地址] | [地址：{0}]").format(endpoint)
        )
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

    async def handle_wss_message(self, message: bytes) -> None:
        """
        处理 WebSocket 消息

        Args:
            message (bytes): WebSocket 消息的字节数据
        """
        try:
            wss_package = PushFrame()
            wss_package.ParseFromString(message)

            logger.debug(_("[WssPackage] [📦Wss包] | [{0}]").format(wss_package))

            log_id = wss_package.logId
            decompressed = gzip.decompress(wss_package.payload)

            payload_package = Response()
            payload_package.ParseFromString(decompressed)

            logger.debug(
                _("[PayloadPackage] [📦Payload包] | [{0}]").format(payload_package)
            )

            # 发送 ack 包
            if payload_package.need_ack:
                await self.send_ack(log_id, payload_package.internal_ext)

            # 并发处理每个消息
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

    async def send_ack(self, log_id: str, internal_ext: str) -> None:
        """
        发送 ack 包

        Args:
            log_id: 日志ID
            internal_ext: 内部扩展信息
        """
        ack = PushFrame()
        ack.logId = log_id
        ack.payloadType = internal_ext
        data = ack.SerializeToString()
        logger.debug(_("[SendAck] [💓 发送 ack 包] | [日志ID：{0}]").format(log_id))
        await self.websocket.send(data)

    async def send_ping(self) -> None:
        """发送 ping 包"""
        ping = PushFrame()
        ping.payloadType = "hb"
        data = ping.SerializeToString()
        logger.debug(_("[SendPing] [📤 发送 ping 包]"))
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

    async def broadcast_message(self, message: str) -> None:
        """
        转发消息给所有连接的客户端

        Args:
            message: 要转发的消息（字符串格式）
        """

        if not isinstance(message, str):
            try:
                message = json.dumps(message, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError) as exc:
                trace_logger.error(traceback.format_exc())
                logger.error(
                    _("[BroadcastMessage] [❌ 消息格式错误] | [错误：{0}]").format(exc)
                )
                return

        tasks = [client.send(message) for client in self.connected_clients]
        await asyncio.gather(*tasks, return_exceptions=True)

    # 定义所有的回调消息函数
    @classmethod
    async def WebcastRoomMessage(cls, data: bytes) -> dict:
        """
        处理直播间消息

        Args:
            data (bytes): 直播间消息的字节数据

        Returns:
            dict: 解析后的直播间消息数据
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

        cls._log(
            _("[WebcastRoomMessage] [🏠房间消息] | [房间信息：{0}]").format(
                data_json.get("room")
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
            dict: 解析后的点赞消息数据
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

        cls._log(
            _(
                "[WebcastLikeMessage] [👍点赞消息] | [用户昵称：{0}] [当前用户点赞：{1}] [直播间总点赞：{2}]"
            ).format(
                data_json.get("user", {}).get("nickname"),
                data_json.get("count"),
                data_json.get("total"),
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
            dict: 解析后的成员消息数据
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

        cls._log(
            _(
                "[WebcastMemberMessage] [🚺观众加入消息] | [用户ID：{0}] [用户名：{1}]"
            ).format(
                data_json.get("user", {}).get("id"),
                data_json.get("user", {}).get("nickname"),
            )
        )
        return data_json

    @classmethod
    async def WebcastChatMessage(cls, data: bytes) -> dict:
        """
        处理直播间聊天消息

        Args:
            data (bytes): 直播间聊天消息的字节数据

        Returns:
            dict: 解析后的聊天消息数据
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

        cls._log(
            _("[WebcastChatMessage] [💬聊天消息] | [内容：{0}]").format(
                data_json.get("content")
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
            dict: 解析后的礼物消息数据
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

        cls._log(
            _("[WebcastGiftMessage] [🎁礼物消息] | [描述：{0}]").format(
                data_json.get("common", {}).get("describe")
            )
        )
        return data_json

    @classmethod
    async def WebcastSocialMessage(cls, data: bytes) -> dict:
        """
        处理直播间关注消息

        Args:
            data (bytes): 直播间关注消息的字节数据

        Returns:
            dict: 解析后的关注消息数据
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

        cls._log(
            _("[WebcastSocialMessage] [➕用户关注消息] | [用户ID：{0}]").format(
                data_json.get("user", {}).get("id")
            )
        )
        return data_json

    @classmethod
    async def WebcastRoomUserSeqMessage(cls, data: bytes) -> dict:
        """
        处理直播间用户序列消息

        Args:
            data (bytes): 直播间用户序列消息的字节数据

        Returns:
            dict: 解析后的用户序列消息数据
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
        ranks = data_json.get("ranksList", [])
        top_users = ", ".join(
            f"用户ID：{rank.get('user', {}).get('id')}" for rank in ranks[:3]
        )

        cls._log(
            _("[WebcastRoomUserSeqMessage] [👥在线观众排行榜] | [{0}]").format(
                top_users
            )
        )
        return data_json

    @classmethod
    async def WebcastUpdateFanTicketMessage(cls, data: bytes) -> dict:
        """
        处理直播间粉丝票更新消息

        Args:
            data (bytes): 直播间粉丝票更新消息的字节数据

        Returns:
            dict: 解析后的粉丝票更新消息数据
        """

        updateFanTicketMessage = UpdateFanTicketMessage()
        updateFanTicketMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                updateFanTicketMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(
            _(
                "[WebcastUpdateFanTicketMessage] [🎟️粉丝票更新消息] | [粉丝票数量：{0}]"
            ).format(data_json.get("roomFanTicketCount"))
        )
        return data_json

    @classmethod
    async def WebcastCommonTextMessage(cls, data: bytes) -> dict:
        """
        处理直播间文本消息

        Args:
            data (bytes): 直播间文本消息的字节数据

        Returns:
            dict: 解析后的文本消息数据
        """

        commonTextMessage = CommonTextMessage()
        commonTextMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                commonTextMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(
            _("[WebcastCommonTextMessage] [📝文本消息] | [内容：{0}]").format(data_json)
        )
        return data_json

    @classmethod
    async def WebcastMatchAgainstScoreMessage(cls, data: bytes) -> dict:
        """
        处理直播间对战积分消息

        Args:
            data (bytes): 直播间对战积分消息的字节数据

        Returns:
            dict: 解析后的对战积分消息数据
        """

        matchAgainstScoreMessage = MatchAgainstScoreMessage()
        matchAgainstScoreMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                matchAgainstScoreMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(
            _(
                "[WebcastMatchAgainstScoreMessage] [🏆对战积分消息] | [内容：{0}]"
            ).format(data_json)
        )
        return data_json

    @classmethod
    async def WebcastEcomFansClubMessage(cls, data: bytes) -> dict:
        """
        处理直播间电商粉丝团消息

        Args:
            data (bytes): 直播间电商粉丝团消息的字节数据

        Returns:
            dict: 解析后的电商粉丝团消息数据
        """

        fansClubMessage = EcomFansClubMessage()
        fansClubMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                fansClubMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(
            _("[WebcastEcomFansClubMessage] [🛍️电商粉丝团消息] | [内容：{0}]").format(
                data_json.get("content")
            )
        )
        return data_json

    @classmethod
    async def WebcastRoomStatsMessage(cls, data: bytes) -> dict:
        """
        处理直播间统计消息

        Args:
            data (bytes): 直播间统计消息的字节数据

        Returns:
            dict: 解析后的统计消息数据
        """

        statsMessage = RoomStatsMessage()
        statsMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                statsMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        # 提取关键信息
        common_info = data_json.get("common", {})
        create_time = common_info.get("create_time", "N/A")
        display_value = data_json.get("display_value", "N/A")
        total = data_json.get("total", "N/A")

        cls._log(
            _(
                "[WebcastStatsMessage] [📊统计消息] | [创建时间：{0}] | [在线观众数：{1}] [总计：{2}]"
            ).format(create_time, display_value, total)
        )
        return data_json

    @classmethod
    async def WebcastLiveShoppingMessage(cls, data: bytes) -> dict:
        """
        处理直播间购物消息

        Args:
            data (bytes): 直播间购物消息的字节数据

        Returns:
            dict: 解析后的购物消息数据
        """

        liveShoppingMessage = LiveShoppingMessage()
        liveShoppingMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                liveShoppingMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        msg_type = data_json.get("msg_type", "N/A")
        promotion_id = data_json.get("promotion_id", "N/A")

        cls._log(
            _(
                "[WebcastLiveShoppingMessage] [🛒直播购物消息] | [消息类型：{0}] [促销ID：{1}]"
            ).format(msg_type, promotion_id)
        )
        return data_json

    @classmethod
    async def WebcastLiveEcomGeneralMessage(cls, data: bytes) -> dict:
        """
        处理直播间电商通用消息

        Args:
            data (bytes): 直播间电商通用消息的字节数据

        Returns:
            dict: 解析后的电商通用消息数据
        """

        liveEcomGeneralMessage = LiveEcomGeneralMessage()
        liveEcomGeneralMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                liveEcomGeneralMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        # # data字段由Base64编码了
        # content_type = data_json.get("content_type", "N/A")

        # cls._log(
        #     _(
        #         "[WebcastLiveEcomGeneralMessage] [🛍️直播电商通用消息] | [内容类型：{0}]"
        #     ).format(content_type)
        # )

        return data_json

    @classmethod
    async def WebcastRoomStreamAdaptationMessage(cls, data: bytes) -> dict:
        """
        处理直播间流适配消息

        Args:
            data (bytes): 直播间流适配消息的字节数据

        Returns:
            dict: 解析后的流适配消息数据
        """

        roomStreamAdaptationMessage = RoomStreamAdaptationMessage()
        roomStreamAdaptationMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                roomStreamAdaptationMessage, preserving_proto_field_name=True
            )
        )

        # adaptation_type = data_json.get("adaptation_type", "N/A")

        # cls._log(
        #     _(
        #         "[WebcastRoomStreamAdaptationMessage] [📡直播流适配消息] | "
        #         "[消息ID：{0}] [房间ID：{1}] [适配类型：{2}]"
        #     ).format(adaptation_type)
        # )
        return data_json

    @classmethod
    async def WebcastRanklistHourEntranceMessage(cls, data: bytes) -> dict:
        """
        处理直播间小时榜入口消息

        Args:
            data (bytes): 直播间小时榜入口消息的字节数据

        Returns:
            dict: 解析后的小时榜入口消息数据
        """

        ranklistHourEntranceMessage = RanklistHourEntranceMessage()
        ranklistHourEntranceMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                ranklistHourEntranceMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        # 提取关键信息
        common_info = data_json.get("common", {})
        create_time = common_info.get("create_time", "N/A")
        ranklist_types = []

        for global_info in data_json.get("info", {}).get("global_infos", []):
            for detail in global_info.get("details", []):
                for page in detail.get("pages", []):
                    content = page.get("content", "N/A")
                    ranklist_type = detail.get("ranklist_type", "N/A")
                    ranklist_types.append(f"{content} (Type: {ranklist_type})")

        cls._log(
            _(
                "[WebcastRanklistHourEntranceMessage] [🕒小时榜入口消息] | "
                "[创建时间：{0}] | [榜单类型：{1}]"
            ).format(create_time, ", ".join(ranklist_types))
        )
        return data_json

    @classmethod
    async def WebcastProductChangeMessage(cls, data: bytes) -> dict:
        """
        处理直播间商品变更消息

        Args:
            data (bytes): 直播间商品变更消息的字节数据

        Returns:
            dict: 解析后的商品变更消息数据
        """

        productChangeMessage = ProductChangeMessage()
        productChangeMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                productChangeMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        cls._log(
            _("[WebcastProductChangeMessage] [🔄商品变更消息] | [内容：{0}]").format(
                data_json
            )
        )
        return data_json

    @classmethod
    async def WebcastNotifyEffectMessage(cls, data: bytes) -> dict:
        """
        处理直播间通知效果消息

        Args:
            data (bytes): 直播间通知效果消息的字节数据

        Returns:
            dict: 解析后的通知效果消息数据
        """

        notifyEffectMessage = NotifyEffectMessage()
        notifyEffectMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                notifyEffectMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        cls._log(
            _("[WebcastNotifyEffectMessage] [📢通知效果消息] | [内容：{0}]").format(
                data_json
            )
        )
        return data_json

    @classmethod
    async def WebcastLightGiftMessage(cls, data: bytes) -> dict:
        """
        处理直播间轻礼物消息

        Args:
            data (bytes): 直播间轻礼物消息的字节数据

        Returns:
            dict: 解析后的轻礼物消息数据
        """

        lightGiftMessage = LightGiftMessage()
        lightGiftMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                lightGiftMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        gift_id = data_json.get("gift_info", {}).get("gift_id", "N/A")
        to_user_id = data_json.get("to_user_id", "N/A")
        diamond_count = data_json.get("gift_info", {}).get("diamond_count", "N/A")

        cls._log(
            _(
                "[WebcastLightGiftMessage] [💡轻礼物消息] | [礼物ID：{0}] [赠送给用户ID：{1}] [钻石数量：{2}]"
            ).format(gift_id, to_user_id, diamond_count)
        )

        return data_json

    @classmethod
    async def WebcastProfitInteractionScoreMessage(cls, data: bytes) -> dict:
        """
        处理直播间互动分数消息

        Args:
            data (bytes): 直播间互动分数消息的字节数据

        Returns:
            dict: 解析后的互动分数消息数据
        """

        profitInteractionScoreMessage = ProfitInteractionScoreMessage()
        profitInteractionScoreMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                profitInteractionScoreMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        interaction_score_status = data_json.get("interaction_score_status", "N/A")

        cls._log(
            _(
                "[WebcastProfitInteractionScoreMessage] [💰互动分数消息] | "
                "[互动分数状态：{0}]"
            ).format(interaction_score_status)
        )

        return data_json

    @classmethod
    async def WebcastRoomRankMessage(cls, data: bytes) -> dict:
        """
        处理直播间排行榜消息

        Args:
            data (bytes): 直播间排行榜消息的字节数据

        Returns:
            dict: 解析后的排行榜消息数据
        """

        roomRankMessage = RoomRankMessage()
        roomRankMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                roomRankMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        # 获取前三名用户的 ID
        ranks = data_json.get("ranks", [])
        top_user_ids = [rank.get("user", {}).get("id_str", "N/A") for rank in ranks[:3]]

        cls._log(
            _(
                "[WebcastRoomRankMessage] [🏆房间排行榜消息] | [前三名用户ID：{0}]"
            ).format(top_user_ids)
        )

        return data_json

    @classmethod
    async def WebcastFansclubMessage(cls, data: bytes) -> dict:
        """
        处理直播间粉丝团消息

        Args:
            data (bytes): 直播间粉丝团消息的字节数据

        Returns:
            dict: 解析后的粉丝团消息数据
        """

        fansclubMessage = FansclubMessage()
        fansclubMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                fansclubMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        cls._log(
            _("[WebcastFansclubMessage] [🎉粉丝团消息] | [内容：{0}]").format(
                data_json.get("content")
            )
        )
        return data_json

    @classmethod
    async def WebcastHotRoomMessage(cls, data: bytes) -> dict:
        """
        处理直播间热门房间消息

        Args:
            data (bytes): 直播间热门房间消息的字节数据

        Returns:
            dict: 解析后的热门房间消息数据
        """

        hotRoomMessage = HotRoomMessage()
        hotRoomMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                hotRoomMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        cls._log(
            _("[WebcastHotRoomMessage] [🔥热门房间消息] | [内容：{0}]").format(
                data_json
            )
        )
        return data_json

    @classmethod
    async def WebcastInRoomBannerMessage(cls, data: bytes) -> dict:
        """
        处理直播间内横幅消息

        Args:
            data (bytes): 直播间内横幅消息的字节数据

        Returns:
            dict: 解析后的内横幅消息数据
        """

        inRoomBannerMessage = InRoomBannerMessage()
        inRoomBannerMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                inRoomBannerMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        # cls._log(
        #     _("[WebcastInRoomBannerMessage] [🚩房间内横幅消息] | [内容：{0}]").format(
        #         data_json
        #     )
        # )
        return data_json

    @classmethod
    async def WebcastScreenChatMessage(cls, data: bytes) -> dict:
        """
        处理直播间全局聊天消息

        Args:
            data (bytes): 直播间全局聊天消息的字节数据

        Returns:
            dict: 解析后的全局聊天消息数据
        """

        screenChatMessage = ScreenChatMessage()
        screenChatMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                screenChatMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        cls._log(
            _("[WebcastScreenChatMessage] [📺管理员全局聊天消息] | [内容：{0}]").format(
                data_json
            )
        )
        return data_json

    @classmethod
    async def WebcastRoomDataSyncMessage(cls, data: bytes) -> dict:
        """
        处理直播间数据同步消息

        Args:
            data (bytes): 直播间数据同步消息的字节数据

        Returns:
            dict: 解析后的数据同步消息数据
        """

        roomDataSyncMessage = RoomDataSyncMessage()
        roomDataSyncMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                roomDataSyncMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        # sync_key = data_json.get("syncKey", "N/A")
        # version = data_json.get("version", "N/A")

        # cls._log(
        #     _(
        #         "[WebcastRoomDataSyncMessage] [🔄房间数据同步消息] | [同步键：{0}] [版本：{1}]"
        #     ).format(sync_key, version)
        # )
        return data_json

    @classmethod
    async def WebcastLinkerContributeMessage(cls, data: bytes) -> dict:
        """
        处理直播间连麦贡献消息

        Args:
            data (bytes): 直播间连麦贡献消息的字节数据

        Returns:
            dict: 解析后的连麦贡献消息数据
        """

        linkerContributeMessage = LinkerContributeMessage()
        linkerContributeMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                linkerContributeMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )

        user_id = data_json.get("user_id", "N/A")
        total_score = data_json.get("total_score", "N/A")

        cls._log(
            _(
                "[WebcastLinkerContributeMessage] [🔗连麦贡献消息] | "
                "[用户ID：{0}] [总贡献分数：{1}]"
            ).format(user_id, total_score)
        )
        return data_json

    @classmethod
    async def WebcastEmojiChatMessage(cls, data: bytes) -> dict:
        """
        处理直播间表情聊天消息

        Args:
            data (bytes): 直播间表情聊天消息的字节数据

        Returns:
            dict: 解析后的表情聊天消息数据
        """

        emojiChatMessage = EmojiChatMessage()
        emojiChatMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                emojiChatMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        cls._log(
            _("[WebcastEmojiChatMessage] [😊表情聊天消息] | [内容：{0}]").format(
                data_json
            )
        )
        return data_json

    @classmethod
    async def WebcastLinkMicMethod(cls, data: bytes) -> dict:
        """
        处理直播间连麦消息(Mic)

        Args:
            data (bytes): 直播间连麦消息的字节数据

        Returns:
            dict: 解析后的连麦消息数据
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

        message_type = data_json.get("message_type", "N/A")
        channel_id = data_json.get("channel_id", "N/A")

        cls._log(
            _(
                "[WebcastLinkMicMethod] [🎤连麦PK对战消息] | [消息类型：{0}] [频道ID：{1}]"
            ).format(message_type, channel_id)
        )
        return data_json

    @classmethod
    async def WebcastLinkMessage(cls, data: bytes) -> dict:
        """
        处理直播间连麦消息

        Args:
            data (bytes): 直播间连麦消息的字节数据

        Returns:
            dict: 解析后的连麦消息数据
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

        message_type = data_json.get("message_type", "N/A")
        linker_id = data_json.get("linker_id", "N/A")

        cls._log(
            _(
                "[WebcastLinkMessage] [🔗连麦消息] | [消息类型：{0}] [连麦ID：{1}]"
            ).format(message_type, linker_id)
        )
        return data_json

    @classmethod
    async def WebcastBattleTeamTaskMessage(cls, data: bytes) -> dict:
        """
        处理直播间战队任务消息

        Args:
            data (bytes): 直播间战队任务消息的字节数据

        Returns:
            dict: 解析后的战队任务消息数据
        """

        battleTeamTaskMessage = BattleTeamTaskMessage()
        battleTeamTaskMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                battleTeamTaskMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        # 提取关键信息
        battle_id = data_json.get("team_task", {}).get("battle_id", "N/A")
        battle_type = data_json.get("team_task", {}).get("battle_type", "N/A")

        cls._log(
            _(
                "[WebcastBattleTeamTaskMessage] [🎯战队任务消息] | "
                "[战斗ID：{0}] [战斗类型：{1}]"
            ).format(battle_id, battle_type)
        )
        return data_json

    @classmethod
    async def WebcastHotChatMessage(cls, data: bytes) -> dict:
        """
        处理直播间热聊消息

        Args:
            data (bytes): 直播间热聊消息的字节数据

        Returns:
            dict: 解析后的热聊消息数据
        """

        hotChatMessage = HotChatMessage()
        hotChatMessage.ParseFromString(data)
        data_json = json.loads(
            json_format.MessageToJson(
                hotChatMessage,
                preserving_proto_field_name=True,
                ensure_ascii=False,
            )
        )
        cls._log(
            _("[WebcastHotChatMessage] [🔥热聊消息] | [内容：{0}]").format(data_json)
        )
        return data_json

    async def __aenter__(self):
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

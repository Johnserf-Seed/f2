# path: f2/apps/douyin/crawler.py

import json
import gzip
import asyncio
import traceback

from typing import Dict
from google.protobuf import json_format
from google.protobuf.message import DecodeError as ProtoDecodeError
from websockets import ConnectionClosedOK, WebSocketServerProtocol, serve

from f2.log.logger import logger
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
        super().__init__(proxies=proxies, crawler_headers=self.headers)

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
        logger.debug(_("直播接口地址：{0}").format(endpoint))
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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class DouyinWebSocketCrawler(WebSocketCrawler):
    # 是否显示直播间消息
    show_message = False

    def __init__(self, kwargs: Dict = ..., callbacks: Dict = None):
        self.__class__.show_message = bool(kwargs.get("show_message", False))
        # 需要与cli同步
        self.headers = kwargs.get("headers", {}) | {
            "Cookie": f"ttwid={TokenManager.gen_ttwid()};"
        }
        self.callbacks = callbacks or {}
        self.timeout = kwargs.get("timeout", 10)
        self.connected_clients = set()  # 管理连接的客户端
        super().__init__(
            wss_headers=self.headers, callbacks=self.callbacks, timeout=self.timeout
        )

    @classmethod
    def _log(cls, message, level="info"):
        """控制消息日志输出的辅助方法"""
        if cls.show_message:
            getattr(logger, level)(message)

    async def fetch_live_danmaku(self, params: LiveWebcast):
        endpoint = BaseEndpointManager.model_2_endpoint(
            dyendpoint.LIVE_IM_WSS,
            params.model_dump(),
        )
        logger.debug(
            _("[FetchLiveDanmaku] [🔗 直播弹幕接口地址] | [地址：{0}]").format(endpoint)
        )
        await self.connect_websocket(endpoint)

        server_task = asyncio.create_task(
            self.start_server()
        )  # 在后台启动 WebSocket 服务器
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
            log_id = wss_package.logId
            decompressed = gzip.decompress(wss_package.payload)
            payload_package = Response()
            payload_package.ParseFromString(decompressed)

            # 发送 ack 包
            if payload_package.need_ack:
                await self.send_ack(log_id, payload_package.internal_ext)

            # 处理每个消息
            for msg in payload_package.messages:
                method = msg.method
                payload = msg.payload

                # 调用对应的回调函数处理消息
                if method in self.callbacks:
                    processed_data = await self.callbacks[method](data=payload)
                    # 转发处理后的数据
                    if processed_data is not None:
                        await self.broadcast_message(processed_data)
                else:
                    logger.warning(
                        _(
                            "[HandleWssMessage] [❌未找到对应的回调函数] | [方法：{0}]"
                        ).format(method)
                    )

        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.error(
                _("[HandleWssMessage] [⚠️ 处理消息出错] | [错误：{0}]").format(exc)
            )

    async def send_ack(self, log_id: str, internal_ext: str):
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

    async def send_ping(self):
        """
        发送 ping 包
        """
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

    async def start_server(self):
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
            logger.debug(_("[StartServer] [⚠️ 服务器任务被取消]"))
        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.error(
                _("[StartServer] [❌ 服务器启动失败] | [错误：{0}]").format(exc)
            )
        finally:
            server.close()
            await server.wait_closed()
            logger.info(_("[StartServer] [🔒 本地 WebSocket 服务器已关闭]"))

    async def _timeout_check(self, server):
        timeout = 10  # 设置超时时间，单位为秒
        while True:
            await asyncio.sleep(timeout)
            if not self.connected_clients:
                logger.info(
                    _(
                        "[TimeoutCheck] [⏳ 无客户端连接超时关闭] | [超时时间：{0} 秒]"
                    ).format(self.timeout)
                )
                break
        server.close()
        await server.wait_closed()
        logger.info(_("本地服务器由于超时无连接而关闭"))
        await self.close_websocket()

    async def register_client(self, websocket: WebSocketServerProtocol):
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
                # 如果需要处理验证信息，可以在这里处理
                pass
        except ConnectionClosedOK:
            logger.info(
                _("[RegisterClient] [⛓ 客户端断开连接] | [Ip：{0} Port：{1}]").format(
                    *websocket.remote_address
                )
            )
        finally:
            self.connected_clients.remove(websocket)

    async def broadcast_message(self, message: str):
        """
        转发消息给所有连接的客户端

        Args:
            message: 要转发的消息（字符串格式）
        """
        if not isinstance(message, str):
            try:
                message = json.dumps(message, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                logger.error(
                    _("[BroadcastMessage] [❌ 消息格式错误] | [错误：{0}]").format(exc)
                )
                return

        tasks = [client.send(message) for client in self.connected_clients]
        await asyncio.gather(*tasks, return_exceptions=True)

    # 定义所有的回调消息函数
    @classmethod
    async def WebcastRoomMessage(cls, data: bytes):
        roomMessage = RoomMessage()
        roomMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            roomMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )
        cls._log(
            _("[WebcastRoomMessage] [🏠房间消息] ｜ {0}").format(data_json.get("room"))
        )

    @classmethod
    async def WebcastLikeMessage(cls, data: bytes):
        likeMessage = LikeMessage()
        likeMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            likeMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )
        return data_dict
        cls._log(
            _(
                "[WebcastLikeMessage] [👍点赞消息] ｜ "
                + "[用户昵称：{0}] [当前用户点赞：{1}] [直播间总点赞：{2}]".format(
                    data_json.get("user").get("nickname"),
                    data_json.get("count"),
                    data_json.get("total"),
                ),
            )
        )

    @classmethod
    async def WebcastMemberMessage(cls, data: bytes):
        memberMessage = MemberMessage()
        memberMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            memberMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )
        # logger.info(
        #     f"[WebcastMemberMessage] [🚺观众加入消息] ｜ [用户Id：{data_dict.get('user').get('id')} 用户名：{data_dict.get('user').get('nickname')}]"
        # )
        return data_dict

    @classmethod
    async def WebcastChatMessage(cls, data: bytes):
        chatMessage = ChatMessage()
        chatMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            chatMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastChatMessage] [💬聊天消息] ｜ {0}").format(
        #         data_dict.get("content")
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastGiftMessage(cls, data: bytes):
        giftMessage = GiftMessage()
        giftMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            giftMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )
        # logger.info(
        #     _("[WebcastGiftMessage] [🎁礼物消息] | [{0}]").format(
        #         data_dict.get("common").get("describe")
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastSocialMessage(cls, data: bytes):
        socialMessage = SocialMessage()
        socialMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            socialMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )
        # logger.info(
        #     _("[WebcastSocialMessage] [➕用户关注消息] | [{0}]").format(
        #         data_dict.get("user").get("id")
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastRoomUserSeqMessage(cls, data: bytes):
        roomUserSeqMessage = RoomUserSeqMessage()
        roomUserSeqMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            roomUserSeqMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastRoomUserSeqMessage] [👥在线观众排行榜] | [{0} {1} {2}]").format(
        #         data_dict.get("ranksList")[0].get("user").get("id"),
        #         data_dict.get("ranksList")[1].get("user").get("id"),
        #         data_dict.get("ranksList")[2].get("user").get("id"),
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastUpdateFanTicketMessage(cls, data: bytes):
        updateFanTicketMessage = UpdateFanTicketMessage()
        updateFanTicketMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            updateFanTicketMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastUpdateFanTicketMessage] [🎟️粉丝票更新消息] | [{0}]").format(
        #         data_dict.get("roomFanTicketCount")
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastCommonTextMessage(cls, data: bytes):
        commonTextMessage = CommonTextMessage()
        commonTextMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            commonTextMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastCommonTextMessage] [📝文本消息] | [{0}]").format(data_dict)
        # )
        return data_dict

    @classmethod
    async def WebcastMatchAgainstScoreMessage(cls, data: bytes):
        matchAgainstScoreMessage = MatchAgainstScoreMessage()
        matchAgainstScoreMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            matchAgainstScoreMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastMatchAgainstScoreMessage] [🏆对战积分消息] | [{0}]").format(
        #         data_dict
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastEcomFansClubMessage(cls, data: bytes):
        fansClubMessage = EcomFansClubMessage()
        fansClubMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            fansClubMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastFansclubMessage] [🎉粉丝团消息] | [{0}]").format(
        #         data_dict.get("content")
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastRoomStatsMessage(cls, data: bytes):
        statsMessage = RoomStatsMessage()
        statsMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            statsMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(_("[WebcastStatsMessage] [📊统计消息] | [{0}]").format(data_dict))
        return data_dict

    @classmethod
    async def WebcastLiveShoppingMessage(cls, data: bytes):
        liveShoppingMessage = LiveShoppingMessage()
        liveShoppingMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            liveShoppingMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        logger.info(
            _("[WebcastLiveShoppingMessage] [🛒直播购物消息] | [{0}]").format(data_dict)
        )
        return data_dict

    @classmethod
    async def WebcastLiveEcomGeneralMessage(cls, data: bytes):
        liveEcomGeneralMessage = LiveEcomGeneralMessage()
        liveEcomGeneralMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            liveEcomGeneralMessage, preserving_proto_field_name=True
        )

        # logger.info(
        #     _("[WebcastLiveEcomGeneralMessage] [🛍️直播电商通用消息] | [{0}]").format(
        #         data_dict
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastRoomStreamAdaptationMessage(cls, data: bytes):
        roomStreamAdaptationMessage = RoomStreamAdaptationMessage()
        roomStreamAdaptationMessage.ParseFromString(data)
        data_dict = json_format.MessageToDict(
            roomStreamAdaptationMessage, preserving_proto_field_name=True
        )

        # logger.info(
        #     _("[WebcastRoomStreamAdaptationMessage] [📡直播流适配消息] | [{0}]").format(
        #         data_dict
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastRanklistHourEntranceMessage(cls, data: bytes):
        ranklistHourEntranceMessage = RanklistHourEntranceMessage()
        ranklistHourEntranceMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            ranklistHourEntranceMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastRanklistHourEntranceMessage] [🕒小时榜入口消息] | [{0}]").format(
        #         data_dict
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastProductChangeMessage(cls, data: bytes):
        productChangeMessage = ProductChangeMessage()
        productChangeMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            productChangeMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastProductChangeMessage] [🔄商品变更消息] | [{0}]").format(
        #         data_dict
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastNotifyEffectMessage(cls, data: bytes):
        notifyEffectMessage = NotifyEffectMessage()
        notifyEffectMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            notifyEffectMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastNotifyEffectMessage] [📢通知效果消息] | [{0}]").format(data_dict)
        # )
        return data_dict

    @classmethod
    async def WebcastLightGiftMessage(cls, data: bytes):
        lightGiftMessage = LightGiftMessage()
        lightGiftMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            lightGiftMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastLightGiftMessage] [💡轻礼物消息] | [{0}]").format(data_dict)
        # )
        return data_dict

    @classmethod
    async def WebcastProfitInteractionScoreMessage(cls, data: bytes):
        profitInteractionScoreMessage = ProfitInteractionScoreMessage()
        profitInteractionScoreMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            profitInteractionScoreMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastProfitInteractionScoreMessage] [💰互动分数消息] | [{0}]").format(
        #         data_dict
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastRoomRankMessage(cls, data: bytes):
        roomRankMessage = RoomRankMessage()
        roomRankMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            roomRankMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastRoomRankMessage] [🏆房间排行榜消息] | [{0}]").format(data_dict)
        # )
        return data_dict

    @classmethod
    async def WebcastFansclubMessage(cls, data: bytes):
        fansclubMessage = FansclubMessage()
        fansclubMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            fansclubMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastFansclubMessage] [🎉粉丝团消息] | [{0}]").format(data_dict)
        # )
        return data_dict

    @classmethod
    async def WebcastHotRoomMessage(cls, data: bytes):
        hotRoomMessage = HotRoomMessage()
        hotRoomMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            hotRoomMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastHotRoomMessage] [🔥热门房间消息] | [{0}]").format(data_dict)
        # )
        return data_dict

    @classmethod
    async def WebcastInRoomBannerMessage(cls, data: bytes):
        inRoomBannerMessage = InRoomBannerMessage()
        inRoomBannerMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            inRoomBannerMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastInRoomBannerMessage] [🚩房间内横幅消息] | [{0}]").format(data_dict)
        # )
        return data_dict

    @classmethod
    async def WebcastScreenChatMessage(cls, data: bytes):
        screenChatMessage = ScreenChatMessage()
        screenChatMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            screenChatMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastScreenChatMessage] [📺管理员全局聊天消息] | [{0}]").format(data_dict)
        # )
        return data_dict

    @classmethod
    async def WebcastRoomDataSyncMessage(cls, data: bytes):
        roomDataSyncMessage = RoomDataSyncMessage()
        roomDataSyncMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            roomDataSyncMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastRoomDataSyncMessage] [🔄房间数据同步消息] | [{0}]").format(
        #         data_dict
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastLinkerContributeMessage(cls, data: bytes):
        linkerContributeMessage = LinkerContributeMessage()
        linkerContributeMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            linkerContributeMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastLinkerContributeMessage] [🔗连麦贡献消息] | [{0}]").format(
        #         data_dict
        #     )
        # )
        return data_dict

    @classmethod
    async def WebcastEmojiChatMessage(cls, data: bytes):
        emojiChatMessage = EmojiChatMessage()
        emojiChatMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            emojiChatMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        logger.info(
            _("[WebcastEmojiChatMessage] [😊表情聊天消息] | [{0}]").format(data_dict)
        )
        return data_dict

    @classmethod
    async def WebcastLinkMicMethod(cls, data: bytes):
        linkMicMethod = LinkMicMethod()
        linkMicMethod.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            linkMicMethod,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        # logger.info(
        #     _("[WebcastLinkMicMethod] [🎤连麦PK对战消息] | [{0}]").format(data_dict)
        # )
        return data_dict

    @classmethod
    async def WebcastLinkMessage(cls, data: bytes):
        linkMessage = LinkMessage()
        linkMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            linkMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        logger.info(_("[WebcastLinkMessage] [🔗连麦消息] | [{0}]").format(data_dict))
        return data_dict

    @classmethod
    async def WebcastBattleTeamTaskMessage(cls, data: bytes):
        battleTeamTaskMessage = BattleTeamTaskMessage()
        battleTeamTaskMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            battleTeamTaskMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        logger.info(
            _("[WebcastBattleTeamTaskMessage] [🎯战队任务消息] | [{0}]").format(
                data_dict
            )
        )
        return data_dict

    @classmethod
    async def WebcastHotChatMessage(cls, data: bytes):
        hotChatMessage = HotChatMessage()
        hotChatMessage.ParseFromString(data)
        data_dict = json_format.MessageToJson(
            hotChatMessage,
            preserving_proto_field_name=True,
            ensure_ascii=False,
        )

        logger.info(_("[WebcastHotChatMessage] [🔥热聊消息] | [{0}]").format(data_dict))
        return data_dict

    async def __aenter__(self):
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

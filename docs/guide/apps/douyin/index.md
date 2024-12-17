---
outline: [2,3]
---

# 接口列表

::: tip 注意
🟢代表已经实现，🟡代表正在实现或修改，🟤代表暂时不实现，🔵代表未来可能实现，🔴代表将会弃用。
:::

::: details handler接口列表

|     CLI接口          |         方法             |
| :------------------ | :-------------------    |
| 下载单个作品          | `handle_one_video`      |
| 下载用户发布作品       | `handle_user_post`      |
| 下载用户喜欢作品       | `handle_user_like`      |
| 下载用户收藏原声       | `handle_user_music_collection` |
| 下载用户收藏作品       | `handle_user_collection` |
| 下载用户收藏夹作品       | `handle_user_collects` |
| 下载用户合集作品       | `handle_user_mix`       |
| 下载用户直播流         | `handle_user_live`      |
| 下载用户首页推荐作品    | `handle_user_feed`      |
| 下载相似作品          | `handle_related`        |
| 下载好友作品          | `handle_friend_feed`      |
| ~~SSO登录~~             | ~~`handle_sso_login`~~   |

|     数据方法接口     |         方法           | 开发者接口  |
| :------------------ | :-------------------   | :--------: |
| 创建用户记录与目录      | `get_or_add_user_data`   |     🟢  |
| 创建作品下载记录        | `get_or_add_video_data`  |     🟢      |
| 获取用户信息            | `fetch_user_profile`     |     🟢      |
| 单个作品数据          | `fetch_one_video`        |     🟢      |
| 用户发布作品数据       | `fetch_user_post_videos` |     🟢      |
| 用户喜欢作品数据       | `fetch_user_like_videos` |     🟢      |
| 用户收藏原声数据       | `fetch_user_music_collection` |  🟢      |
| 用户收藏作品数据       | `fetch_user_collection_videos` |  🟢      |
| 用户收藏夹数据         | `fetch_user_collects`    |     🟢      |
| 用户收藏夹作品数据     | `fetch_user_collects_videos` |     🟢      |
| 用户合集作品数据       | `fetch_user_mix_videos`  |     🟢      |
| 用户直播流数据         | `fetch_user_live_videos` |     🟢      |
| 用户直播流数据2        | `fetch_user_live_videos_by_room_id` |     🟢      |
| 用户首页推荐作品数据    | `fetch_user_feed_videos` |     🟢      |
| 相似作品数据          | `fetch_related_videos` |     🟢      |
| 好友作品数据          | `fetch_friend_feed_videos` |     🟢      |
| 关注用户数据          | `fetch_user_following` |     🟢      |
| 粉丝用户数据          | `fetch_user_follower` |     🟢      |
| 查询用户数据          | `fetch_query_user`   |     🟢      |
| 查询作品的统计信息     | `fetch_post_stats`   |     🟢      |
| 直播间wss负载数据      | `fetch_live_im`      |     🟢      |
| 直播间wss弹幕         | `fetch_live_danmaku` |     🟢      |
| 关注用户的直播间信息    | `fetch_user_following_lives` |     🟢      |
:::

::: details utils接口列表

| 工具类接口            | 类名                   | 方法                         | 状态 |
| :------------------ | :--------------------- | :-------------------------- | :--: |
| 管理客户端配置        | `ClientConfManager`    |                              |  🟢  |
| 生成真实msToken      | `TokenManager`         | `gen_real_msToken`           |  🟢  |
| 生成虚假msToken      | `TokenManager`         | `gen_false_msToken`          |  🟢  |
| 生成ttwid           | `TokenManager`         | `gen_ttwid`                  |  🟢  |
| 生成webid           | `TokenManager`         | `gen_webid`                  |  🟢  |
| 生成verify_fp       | `VerifyFpManager`      | `gen_verify_fp`              |  🟢  |
| 生成s_v_web_id      | `VerifyFpManager`      | `gen_s_v_web_id`             |  🟢  |
| 生成直播signature    | `DouyinWebcastSignature` | `get_signature`            |  🟢  |
| ~~使用接口模型生成wss签名参数~~ | ~~`WebcastSignatureManager`~~ | ~~`model_2_endpoint`~~      |  🔴  |
| 使用接口地址生成Xb参数 | `XBogusManager`        | `str_2_endpoint`             |  🟢  |
| 使用接口模型生成Xb参数 | `XBogusManager`        | `model_2_endpoint`           |  🟢  |
| 使用接口地址生成Ab参数 | `ABogusManager`        | `str_2_endpoint`             |  🟢  |
| 使用接口模型生成Ab参数 | `ABogusManager`        | `model_2_endpoint`           |  🟢  |
| 提取单个用户id       | `SecUserIdFetcher`     | `get_sec_user_id`            |  🟢  |
| 提取列表用户id       | `SecUserIdFetcher`     | `get_all_sec_user_id`        |  🟢  |
| 提取单个作品id       | `AwemeIdFetcher`       | `get_aweme_id`               |  🟢  |
| 提取列表作品id       | `AwemeIdFetcher`       | `get_all_aweme_id`           |  🟢  |
| 提取单个合集id       | `MixIdFetcher`         | `get_mix_id`                 |  🟢  |
| 提取列表合集id       | `MixIdFetcher`         | `get_all_mix_id`             |  🟢  |
| 提取单个直播间号      | `WebCastIdFetcher`     | `get_webcast_id`             |  🟢  |
| 提取列表直播间号      | `WebCastIdFetcher`     | `get_all_webcast_id`         |  🟢  |
| 全局格式化文件名      | -                      | `format_file_name`           |  🟢  |
| 创建用户目录         | -                      | `create_user_folder`         |  🟢  |
| 重命名用户目录        | -                      | `rename_user_folder`         |  🟢  |
| 创建或重命名用户目录   | -                      | `create_or_rename_user_folder` | 🟢  |
| ~~显示二维码~~         | -                      | ~~`show_qrcode`~~              |  🔴  |
| json歌词转lrc歌词    | -                      | `json_2_lrc`                 |  🟢  |
:::

::: details crawler接口列表

| 爬虫url接口    | 类名       | 方法          | 状态 |
| :----------- | :--------- | :----------  | :--: |
| 用户信息接口地址 | `DouyinCrawler` | `fetch_user_profile` |  🟢  |
| 主页作品接口地址 | `DouyinCrawler` | `fetch_user_post` |  🟢  |
| 喜欢作品接口地址 | `DouyinCrawler` | `fetch_user_like` |  🟢  |
| 收藏作品接口地址 | `DouyinCrawler` | `fetch_user_collection` |  🟢  |
| 收藏夹接口地址 | `DouyinCrawler` | `fetch_user_collects` |  🟢  |
| 收藏夹作品接口地址 | `DouyinCrawler` | `fetch_user_collects_video` |  🟢  |
| 音乐收藏接口地址 | `DouyinCrawler` | `fetch_user_music_collection` |  🟢  |
| 合集作品接口地址 | `DouyinCrawler` | `fetch_user_mix` |  🟢  |
| 作品详情接口地址 | `DouyinCrawler` | `fetch_post_detail` |  🟢  |
| 作品评论接口地址 | `DouyinCrawler` | `fetch_post_comment` |  🟢  |
| 推荐作品接口地址 | `DouyinCrawler` | `fetch_post_feed` |  🟢  |
| 关注作品接口地址 | `DouyinCrawler` | `fetch_follow_feed` |  🟢  |
| 朋友作品接口地址 | `DouyinCrawler` | `fetch_friend_feed` |  🟢  |
| 相关推荐作品接口地址 | `DouyinCrawler` | `fetch_post_related` |  🟢  |
| 直播接口地址 | `DouyinCrawler` | `fetch_live` |  🟢  |
| 直播接口地址（room_id） | `DouyinCrawler` | `fetch_live_room_id` |  🟢  |
| 关注用户直播接口地址 | `DouyinCrawler` | `fetch_following_live` |  🟢  |
| 定位上一次作品接口地址 | `DouyinCrawler` | `fetch_locate_post` |  🟢  |
| ~~SSO获取二维码接口地址~~ | ~~`DouyinCrawler`~~ | ~~`fetch_login_qrcode`~~ |  🔴  |
| ~~SSO检查扫码状态接口地址~~ | ~~`DouyinCrawler`~~ | ~~`fetch_check_qrcode`~~ |  🔴  |
| ~~SSO检查登录状态接口地址~~ | ~~`DouyinCrawler`~~ | ~~`fetch_check_login`~~ |  🔴  |
| 用户关注列表接口地址 | `DouyinCrawler` | `fetch_user_following` |  🟢  |
| 用户粉丝列表接口地址 | `DouyinCrawler` | `fetch_user_follower` |  🟢  |
| 直播弹幕初始化接口地址 | `DouyinCrawler` | `fetch_live_im_fetch` |  🟢  |
| 查询用户接口地址 | `DouyinCrawler` | `fetch_query_user` |  🟢  |
| 直播弹幕接口地址 | `DouyinWebSocketCrawler` | `fetch_live_danmaku` |  🟢  |
| 处理 WebSocket 消息 | `DouyinWebSocketCrawler` | `handle_wss_message` |  🟢  |
| 发送 ack 包 | `DouyinWebSocketCrawler` | `send_ack` |  🟢  |
| 发送 ping 包 | `DouyinWebSocketCrawler` | `send_ping` |  🟢  |
| 直播间房间消息 | `DouyinWebSocketCrawler` | `WebcastRoomMessage` |  🟢  |
| 直播间点赞消息 | `DouyinWebSocketCrawler` | `WebcastLikeMessage` |  🟢  |
| 直播间观众加入消息 | `DouyinWebSocketCrawler` | `WebcastMemberMessage` |  🟢  |
| 直播间聊天消息 | `DouyinWebSocketCrawler` | `WebcastChatMessage` |  🟢  |
| 直播间礼物消息 | `DouyinWebSocketCrawler` | `WebcastGiftMessage` |  🟢  |
| 直播间用户关注消息 | `DouyinWebSocketCrawler` | `WebcastSocialMessage` |  🟢  |
| 直播间用户序列消息| `DouyinWebSocketCrawler` | `WebcastRoomUserSeqMessage` |  🟢  |
| 直播间粉丝票更新消息| `DouyinWebSocketCrawler` | `WebcastUpdateFanTicketMessage` |  🟢  |
| 直播间文本消息 | `DouyinWebSocketCrawler` | `WebcastCommonTextMessage` |  🟢  |
| 直播间对战积分消息 | `DouyinWebSocketCrawler` | `WebcastMatchAgainstScoreMessage` |  🟢  |
| 直播间电商粉丝团消息 | `DouyinWebSocketCrawler` | `WebcastEcomFansClubMessage` |  🟢  |
| 直播间小时榜入口消息 | `DouyinWebSocketCrawler` | `WebcastRanklistHourEntranceMessage` |  🟢  |
| 直播间统计消息 | `DouyinWebSocketCrawler` | `WebcastRoomStatsMessage` |  🟢  |
| 直播间购物消息 | `DouyinWebSocketCrawler` | `WebcastLiveShoppingMessage` |  🟢  |
| 直播间电商通用消息 | `DouyinWebSocketCrawler` | `WebcastLiveEcomGeneralMessage` |  🟢  |
| 直播间商品变更消息 | `DouyinWebSocketCrawler` | `WebcastProductChangeMessage` |  🟢  |
| 直播间流适配消息 | `DouyinWebSocketCrawler` | `WebcastRoomStreamAdaptationMessage` |  🟢  |
| 直播间通知效果消息 | `DouyinWebSocketCrawler` | `WebcastNotifyEffectMessage` |  🟢  |
| 直播间轻礼物消息 | `DouyinWebSocketCrawler` | `WebcastLightGiftMessage` |  🟢  |
| 直播间互动分数消息 | `DouyinWebSocketCrawler` | `WebcastProfitInteractionScoreMessage` |  🟢  |
| 直播间排行榜消息 | `DouyinWebSocketCrawler` | `WebcastRoomRankMessage` |  🟢  |
| 直播间粉丝团消息 | `DouyinWebSocketCrawler` | `WebcastFansclubMessage` |  🟢  |
| 直播间热门房间消息 | `DouyinWebSocketCrawler` | `WebcastHotRoomMessage` |  🟢  |
| 直播间连麦消息 | `DouyinWebSocketCrawler` | `WebcastLinkMicMethod` |  🟢  |
| 直播间连麦贡献消息 | `DouyinWebSocketCrawler` | `WebcastLinkerContributeMessage` |  🟢  |
| 直播间表情聊天消息 | `DouyinWebSocketCrawler` | `WebcastEmojiChatMessage` |  🟢  |
| 直播间全局聊天消息 | `DouyinWebSocketCrawler` | `WebcastScreenChatMessage` |  🟢  |
| 直播间数据同步消息 | `DouyinWebSocketCrawler` | `WebcastRoomDataSyncMessage` |  🟢  |
| 直播间内横幅消息 | `DouyinWebSocketCrawler` | `WebcastInRoomBannerMessage` |  🟢  |
| 直播间连麦消息 | `DouyinWebSocketCrawler` | `WebcastLinkMessage` |  🟢  |
| 直播间战队任务消息 | `DouyinWebSocketCrawler` | `WebcastBattleTeamTaskMessage` |  🟢  |
| 直播间热聊消息 | `DouyinWebSocketCrawler` | `WebcastHotChatMessage` |  🟢  |
:::

::: details dl接口列表

| 下载器接口     | 类名        | 方法          | 状态 |
| :----------- | :--------- | :----------  | :--: |
| 保存最后请求的作品ID | `DouyinDownloader` | `save_last_aweme_id` |  🟢  |
| 创建下载任务   | `DouyinDownloader` | `create_download_task` |  🟢  |
| 处理下载任务   | `DouyinDownloader` | `handler_download` |  🟢  |
| 下载原声      | `DouyinDownloader` | `download_music`   |  🟢  |
| 下载封面      | `DouyinDownloader` | `download_cover`   |  🟢  |
| 下载文案      | `DouyinDownloader` | `download_desc`    |  🟢  |
| 下载视频      | `DouyinDownloader` | `download_video`   |  🟢  |
| 下载图集      | `DouyinDownloader` | `download_images`  |  🟢  |
| 创建原声下载任务 | `DouyinDownloader` | `create_music_download_tasks` |  🟢  |
| 处理原声下载任务 | `DouyinDownloader` | `handler_music_download` |  🟢  |
| 创建直播流下载任务  | `DouyinDownloader` | `create_stream_tasks` |  🟢  |
| 直播流下载     | `DouyinDownloader` | `handler_stream` |  🟢  |
:::

::: tip :bulb: 提示
- 翻页参数都包含在上一次请求的数据中，通过内置的 `filter` 过滤器可以很方便的获取。
- 所有包含翻页参数的接口均使用异步生成器方法，需要通过 `async for` 进行迭代，便于自动处理翻页。
- 当 `max_counts` 设置为 `None` 或不传入时，将会获取所有的作品数据。
- 在一些后端框架 `FastAPI`、`Flask`、`Django` 中可以方便的集成等。
- 使用登录的 `cookie` 可以无视该账号的私密设置，例如该账号设置私密的 `作品`、`主页`、`喜欢`、`收藏` 等。
:::

## handler接口列表

### 创建用户记录与目录 🟢

异步方法，用于获取或创建用户数据同时创建用户目录。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| kwargs | dict | cli字典数据，需获取path参数 |
| sec_user_id| str | 用户ID |
| db | AsyncUserDB | 用户数据库 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_path | Path | 用户目录路径对象 |

<<< @/snippets/douyin/user-get-add.py{12,13,18,21-23}

::: tip :bulb: 提示
- 此为 `cli` 模式的接口，开发者可自行定义创建用户目录的功能。
- 不设置 `mode` 参数时，默认为 `PLEASE_SETUP_MODE` 目录。
:::

### 创建作品下载记录 🟢

异步方法，用于获取或创建作品数据同时创建作品目录。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 作品数据字典 |
| db | AsyncVideoDB | 作品数据库 |
| ignore_fields | list | 忽略的字段列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

<<< @/snippets/douyin/video-get-add.py{6,19-25}

### 获取用户信息 🟢

异步方法，用于获取指定用户的信息。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserProfileFilter | model | 用户数据过滤器，包含用户数据的_to_raw、_to_dict方法 |

<<< @/snippets/douyin/user-profile.py{15,16}

### 单个作品数据 🟢

异步方法，用于获取单个视频。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_id| str | 视频ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| PostDetailFilter | model | 单个作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/one-video.py{15}

### 用户发布作品数据 🟢

异步方法，用于获取用户发布的视频列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |
| min_cursor| int | 最小页码，初始为0 |
| max_cursor| int | 最大页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserPostFilter | AsyncGenerator | 发布作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-post.py{16,18-20}

### 用户喜欢作品数据 🟢

异步方法，用于获取指定用户喜欢的视频列表，需开放喜欢列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserPostFilter | AsyncGenerator | 喜欢作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-like.py{16-20}

### 用户收藏原声数据 🟢

异步方法，用于获取指定用户收藏的音乐列表，只能获取登录了账号的收藏音乐。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserMusicCollectionFilter | AsyncGenerator | 收藏音乐数据过滤器，包含音乐数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-collection.py#user-collection-music-snippet{17-20}

### 用户收藏作品数据 🟢

异步方法，用于获取指定用户收藏的视频列表，只能爬登录了账号的收藏作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserCollectionFilter | AsyncGenerator | 收藏作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-collection.py#user-collection-music-snippet{17-20}

### 用户收藏夹数据 🟢

异步方法，用于获取指定用户的收藏夹列表，不是收藏夹作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserCollectsFilter | AsyncGenerator | 收藏夹数据过滤器，包含收藏夹数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-collects.py#user-collects-snippet{17-21}

### 用户收藏夹作品数据 🟢

异步方法，用于获取指定用户收藏夹的视频列表，收藏夹作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| collect_id| str | 收藏夹ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserCollectsVideosFilter | AsyncGenerator | 收藏夹作品数据过滤器，包含收藏夹作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-collects.py#user-collects-videos-snippet{17-22}

### 用户合集作品数据 🟢

异步方法，用于获取指定用户合集的视频列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| mix_id| str | 合集ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserMixFilter | AsyncGenerator | 合集作品数据过滤器，包含合集作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-mix.py{16,18-23}

::: tip :bulb: 提示
- 合集作品的 `mix_id` 是一致的，使用 `fetch_one_video` 接口获取 `mix_id`。
:::

### 用户直播流数据 🟢

异步方法，用于获取指定用户的直播。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_id| str | 直播间ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_data | dict | 直播数据字典，包含直播ID、直播标题、直播状态、观看人数、子分区、主播昵称等 |

<<< @/snippets/douyin/user-live.py{15}

::: tip :bulb: 提示
- `webcast_id` 与 `room_id` 为2个独立参数，由不同接口解析。
- 例如：`https://live.douyin.com/775841227732` 中 `775841227732` 为直播ID(`webcast_id`/`live_id`)。
- 当你使用 `APP` 端分享的直播链接时，解析完的是`room_id`，需要使用`fetch_user_live_videos_by_room_id`接口。
:::

### 用户直播流数据2 🟢

异步方法，用于获取指定用户的直播。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| room_id| str | 直播间ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_data | dict | 直播数据字典，包含直播ID、直播标题、直播状态、观看人数、子分区、主播昵称等 |

<<< @/snippets/douyin/user-live-room-id.py{15-17}

::: tip :bulb: 提示
- `webcast_id` 与 `room_id` 为2个独立参数，由不同接口解析。
- 例如：`https://webcast.amemv.com/douyin/webcast/reflow/7444223303348144935?xxx=xxx...` 中 `7444223303348144935` 为直播间ID(`room_id`)。
:::

### 用户首页推荐作品数据 🟢

异步方法，用于获取指定用户的首页推荐作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserPostFilter | AsyncGenerator | 首页推荐作品数据过滤器，包含推荐作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-feed.py{17-23}

### 相似作品数据 🟢

异步方法，用于获取指定作品的相似作品，多用于收集扩展相似作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_id| str | 作品ID |
| filterGids| str | 过滤的Gids，初始为空 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| PostRelatedFilter | dict | 相关推荐作品数据过滤器，包含相关作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/aweme-related.py{16-21}

::: tip :bulb: 提示
- `filterGids` 参数用于排除指定作品，置空会有重复推荐数据。
- 例如：`filterGids` 参数为 `7419386765854641442`，多个作品用逗号分隔，如 `7419386765854641442,741938xxxx,74193xxxx`。
- 需要自行过滤每次请求的 `aweme_id` ，并将其添加到 `filterGids` 参数中。
:::

### 好友作品数据 🟢

异步方法，用于获取好友的作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| cursor| str | 页码，初始为0 |
| level| int | 作品级别，初始为1 |
| pull_type| int | 拉取类型，初始为0 |
| max_counts| int | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| FriendFeedFilter | AsyncGenerator | 好友作品数据过滤器，包含好友作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-friend.py{16-21}

::: tip :bulb: 提示
- `pull_type` 的参数有 `0` `2` `18`，未研究具体含义。
:::

### 关注用户数据 🟢

异步方法，用于获取指定用户关注的用户列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_id| str | 用户ID |
| sec_user_id| str | 用户ID |
| offset| int | 页码，初始为0 |
| min_time | int | 最早关注时间戳，秒级，初始为0 |
| max_time | int | 最晚关注时间戳，秒级，初始为0 |
| count| int | 每页关注用户数，初始为20 |
| source_type| int | 排序类型，初始为4 |
| max_counts| float | 最大列表数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserFollowingFilter | AsyncGenerator | 关注用户数据过滤器，包含关注用户数据的_to_raw、_to_dict、_to_list方法 |

#### 偏移量 (**offset**)

- 当 `source_type` 为 `1` 和 `3` 时，`offset` 参数无效。
- 当 `source_type` 为 `4` 时，`offset` 参数有效。

#### 时间范围 (**min_time**/**max_time**)

- 如果未传递 `max_time` 和 `min_time` 参数，`F2` 将自动处理时间范围，确保数据完整性。
- 若需要自定义时间范围，可通过手动设置 `max_time` 和 `min_time` 参数实现。

#### 关注用户数 (**count**)

- `count` 参数控制每页关注用户数，不建议设置过大，建议使用默认值。

#### 排序类型 (**source_type**)

- `1` 表示按最近关注排序。
- `3` 表示按最早关注排序。
- `4` 表示按综合排序。

::: tip :bulb: 但需注意
- 只能获取到用户**公开状态**的关注用户数据。
- 时间间隔过长可能导致数据不完整，不建议采用自定义时间范围，仅适用于获取特定时间段前或后的数据场景。
:::

<<< @/snippets/douyin/user-following.py{18-20,22-31}

### 粉丝用户数据 🟢

异步方法，用于获取指定用户的粉丝列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_id| str | 用户ID |
| sec_user_id| str | 用户ID |
| offset| int | 页码，初始为0 |
| min_time | int | 最早关注时间戳，初始为0 |
| max_time | int | 最晚关注时间戳，初始为0 |
| count| int | 页数，初始为20 |
| source_type| int | 排序类型，初始为1 |
| max_counts| float | 最大粉丝数，默认为无穷大 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserFollowerFilter | AsyncGenerator | 粉丝用户数据过滤器，包含粉丝用户数据的_to_raw、_to_dict、_to_list方法 |

#### 偏移量 (**offset**)

- 当 `source_type` 为 `1` 和 `2` 时，`offset` 参数无效。故粉丝用户接口不需要 `offset` 参数。

#### 时间范围 (**min_time**/**max_time**)

- 如果未传递 `max_time` 和 `min_time` 参数，`F2` 将自动处理时间范围，确保数据完整性。
- 若需要自定义时间范围，可通过手动设置 `max_time` 和 `min_time` 参数实现。

#### 粉丝用户数 (**count**)

- `count` 参数控制每页粉丝用户数，不建议设置过大，建议使用默认值。

#### 排序类型 (**source_type**)

- `1` 表示按综合排序。
- `2` 意义不明确。

::: tip :bulb: 但需注意
- 只能获取到用户**公开状态**的粉丝用户数据。
- 时间间隔过长可能导致数据不完整，不建议采用自定义时间范围，仅适用于获取特定时间段前或后的数据场景。
:::

<<< @/snippets/douyin/user-follower.py{18-20,22-29}

::: info 提示
- `source_type` 的参数控制排序类型，`2` 为综合排序（无效），`1` 为最近粉丝。
- 当选择 `source_type` 为 `1` 时，需要设置 `max_time` 参数选择时间范围。
:::

> [!IMPORTANT] 重要 ❗❗❗
> - 当选择 `source_type` 为 `1` 时 `offset` 参数无效。
> - 当选择 `source_type` 为 `2` 时，不返回数据。

### 查询用户信息 🟢

通过`ttwid`的参数用于查询用户基本信息，若需要获取更多信息请使用`fetch_user_profile`。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| QueryUserFilter | model | 查询用户数据过滤器，包含用户数据的_to_raw、_to_dict方法 |

<<< @/snippets/douyin/query-user.py{18}

### 直播间wss负载数据 🟢

异步方法，用于获取直播间wss负载数据，是弹幕wss的必要参数。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| room_id| str | 直播间ID |
| unique_id| str | 用户ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| LiveImFetchFilter | model | 直播间wss负载数据过滤器，包含直播间wss负载数据的_to_raw、_to_dict方法 |

<<< @/snippets/douyin/user-live-im-fetch.py#user-live-im-snippet{16-18,23-41}

### 直播间wss弹幕 🟢

异步方法，用于获取直播间wss弹幕数据，使用内置回调处理不同类型的消息。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| room_id| str | 直播间ID |
| user_unique_id| str | 用户ID |
| internal_ext| str | 内部扩展参数 |
| cursor| str | 弹幕页码 |
| callback| dict | 自定义弹幕回调函数，键为消息类型，值为处理函数 |

| 回调 | 说明 |
| :--- | :--- |
| WebcastRoomMessage | 直播间房间消息 |
| WebcastLikeMessage | 直播间点赞消息 |
| WebcastMemberMessage | 直播间观众加入消息 |
| WebcastChatMessage | 直播间聊天消息 |
| WebcastGiftMessage | 直播间礼物消息 |
| WebcastSocialMessage | 直播间用户关注消息 |
| WebcastRoomUserSeqMessage | 直播间在线观众排行榜 |
| WebcastUpdateFanTicketMessage | 直播间粉丝票更新消息 |
| WebcastCommonTextMessage | 直播间文本消息 |
| WebcastMatchAgainstScoreMessage | 直播间对战积分消息 |
| WebcastFansclubMessage | 直播间粉丝团消息 |
| WebcastRanklistHourEntranceMessage | 直播间小时榜入口消息 |
| WebcastRoomStatsMessage | 直播间统计消息 |
| WebcastLiveShoppingMessage | 直播间购物消息 |
| WebcastLiveEcomGeneralMessage | 直播间电商通用消息 |
| WebcastProductChangeMessage | 直播间商品变更消息 |
| WebcastRoomStreamAdaptationMessage | 直播间流适配消息 |
| WebcastNotifyEffectMessage | 直播间通知效果消息 |
| WebcastLightGiftMessage | 直播间轻礼物消息 |
| WebcastProfitInteractionScoreMessage | 直播间互动分数消息 |
| WebcastRoomRankMessage | 直播间排行榜消息 |
| WebcastEcomFansClubMessage | 直播间电商粉丝团消息 |
| WebcastHotRoomMessage | 直播间热门房间消息 |
| WebcastLinkMicMethod | 直播间连麦消息 |
| WebcastLinkerContributeMessage | 直播间连麦贡献消息 |
| WebcastEmojiChatMessage | 直播间表情聊天消息 |
| WebcastScreenChatMessage | 直播间全局聊天消息 |
| WebcastRoomDataSyncMessage | 直播间数据同步消息 |
| WebcastInRoomBannerMessage | 直播间内横幅消息 |
| WebcastLinkMessage | 直播间连麦消息 |
| WebcastBattleTeamTaskMessage | 直播间战队任务消息 |
| WebcastHotChatMessage | 直播间热聊消息 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| self.websocket | WebSocket | 弹幕WebSocket对象 |

<<< @/snippets/douyin/user-live-im-fetch.py#user-live-im-fetch-snippet{30-33,36-69,106-113}

### 关注用户的直播间信息 🟢

异步方法，用于获取关注用户的直播间信息列表，需要登录账号后的 `cookie`。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| FollowingUserLiveFilter | model | 关注用户直播间数据过滤器，包含关注用户直播间数据的_to_raw、_to_dict方法 |

<<< @/snippets/douyin/user-follow-live.py{16}

### SSO登录 🔴

异步方法，用于处理用户SSO登录，获取用户的cookie。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| is_login | bool | 是否登录成功 |
| login_cookie | str | 登录cookie |

<<< @/snippets/douyin/sso-login.py{6}

::: danger 警告
该接口已在 `0.0.1.6` 版本之后弃用，由于扫码登录受风控影响最大。为了保障体验，建议使用  `--auto-cookie` 命令自动从浏览器获取 `cookie`，使用帮助参考 `cli命令`。
:::


## utils接口列表

### 管理客户端配置 🟢

类方法，用于管理客户端配置。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| 配置文件值 | Any | 配置文件值 |

<<< @/snippets/douyin/client-config.py{4,5,7,8,10,11}

### 生成真实msToken 🟢

类方法，用于生成真实的msToken，当出现错误时返回虚假的值。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| msToken | str | 真实的msToken |

<<< @/snippets/douyin/mstoken-real.py{4}

### 生成虚假msToken 🟢

类方法，用于生成随机虚假的msToken，不同端点的msToken长度不同。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| msToken | str | 虚假的msToken |

<<< @/snippets/douyin/mstoken-false.py{4}

::: tip :bulb: 提示
默认为126位，也可调用 `from f2.utils.utils import gen_random_str`，生成不同长度的虚假msToken。
:::

### 生成ttwid 🟢

类方法，用于生成ttwid，部分请求必带，游客状态必须有。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| ttwid | str | ttwid参数 |

<<< @/snippets/douyin/ttwid.py{4}

### 生成webid 🟢

类方法，用于生成个性化追踪webid。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webid | str | webid参数 |

<<< @/snippets/douyin/webid.py{4}

### 生成verify_fp 🟢

类方法，用于生成verify_fp，部分请求必带。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| verify_fp | str | verify_Fp与fp参数 |

<<< @/snippets/douyin/verify_fp.py{4}

### 生成s_v_web_id 🟢

类方法，用于生成s_v_web_id，部分请求必带，即verify_fp值。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| s_v_web_id | str | s_v_web_id参数 |

<<< @/snippets/douyin/s_v_web_id.py{4}

### 生成直播signature 🟢

用于生成直播signature，请求弹幕wss必带。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| room_id | str | 直播间ID |
| user_unique_id | str | 用户ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| signature | str | 直播signature |

<<< @/snippets/douyin/webcast-signature.py#webcast-signature-snippet{5-10}

### 使用接口地址生成Xb参数 🟢

类方法，用于直接使用接口地址生成Xbogus参数，部分接口不校验。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_agent | str | 用户代理 |
| endpoint | str | 接口端点 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_endpoint | str | 带Xbogus参数的完整地址 |

<<< @/snippets/douyin/xbogus.py#str-2-endpoint-snippet{7-11}

### 使用接口模型生成Xb参数 🟢

类方法，用于使用不同接口数据模型生成Xbogus参数，部分接口不校验。


| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_agent | str | 用户代理 |
| endpoint | str | 端点 |
| params | dict | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_endpoint | str | 带Xbogus参数的完整地址 |

使用模型生成接口地址，需要先创建一个模型对象，然后调用`model_2_endpoint`方法。

<<< @/snippets/douyin/xbogus.py#model-2-endpoint-snippet{9-13,17-19}

还可以使用爬虫引擎与过滤器采集数据。

<<< @/snippets/douyin/xbogus.py#model-2-endpoint-2-filter-snippet{22-27}

更加抽象的高级方法可以直接调用handler接口的`fetch_user_profile`。


### 使用接口地址生成Ab参数 🟢

类方法，用于直接使用接口地址生成Ab参数，新接口都需要校验。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_agent | str | 用户代理 |
| params | str | 请求参数 |
| request_type | str | 请求类型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_params | str | 带Ab参数的请求参数 |

<<< @/snippets/douyin/abogus.py#str-2-endpoint-snippet{7-13}

### 使用接口模型生成Ab参数 🟢

类方法，用于使用不同接口数据模型生成Ab参数，新接口都需要校验。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_agent | str | 用户代理 |
| base_endpoint | str | 端点 |
| params | dict | 请求参数模型 |
| request_type | str | 请求类型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_params | str | 带Ab参数的请求参数 |

使用模型生成接口地址，需要先创建一个模型对象，然后调用`model_2_endpoint`方法。

<<< @/snippets/douyin/abogus.py#model-2-endpoint-snippet{9-14,18-20}

还可以使用爬虫引擎与过滤器采集数据。

<<< @/snippets/douyin/abogus.py#model-2-endpoint-2-filter-snippet{20-26}

更加抽象的高级方法可以直接调用handler接口的`fetch_user_profile`。

::: tip :bulb: 提示
本项目的残血版Ab算法的UA参数为固定值，`Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0`。
:::

### 提取单个用户id 🟢

类方法，用于提取单个用户id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 用户主页地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id | str | 用户ID |

<<< @/snippets/douyin/sec-user-id.py#single-user-id-snippet{8}

### 提取列表用户id 🟢

类方法，用于提取列表用户id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 用户主页地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_ids | list | 用户ID列表 |

<<< @/snippets/douyin/sec-user-id.py#multi-user-id-snippet{15,18}

### 提取单个作品id 🟢

类方法，用于提取单个作品id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 作品地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_id | str | 作品ID |

<<< @/snippets/douyin/aweme-id.py#single-aweme-id-snippet{9}

### 提取列表作品id 🟢

类方法，用于提取列表作品id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 作品地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_ids | list | 作品ID列表 |

<<< @/snippets/douyin/aweme-id.py#multi-aweme-id-snippet{16,19}

### 提取合集id 🟢

类方法，用于从合集链接中提取合集id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 合集地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| mix_id | str | 合集ID |

<<< @/snippets/douyin/mix-id.py#single-mix-id-snippet{7}

### 提取列表合集id 🟢

类方法，用于从合集链接列表中提取合集id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 合集地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| mix_ids | list | 合集ID列表 |

<<< @/snippets/douyin/mix-id.py#multi-mix-id-snippet{13,16}

### 提取单个直播间号 🟢

类方法，用于提取单个直播间号。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 直播间地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_id | str | 直播间RID |


<<< @/snippets/douyin/webcast-id.py#single-webcast-id-snippet{7}

### 提取列表直播间号 🟢

类方法，用于提取列表直播间号。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 直播间地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_ids | list | 直播间RID列表 |

<<< @/snippets/douyin/webcast-id.py#multi-webcast-id-snippet{16,19}

::: tip 如何分辨r_id与room_id
r_id是直播间的短链标识，room_id是直播间的唯一标识。
如`https://live.douyin.com/775841227732`中的`775841227732`就是r_id，而`https://webcast.amemv.com/douyin/webcast/reflow/7318296342189919011`中的`7318296342189919011`就是room_id。
这2个链接都指向同一个直播间。
:::

::: warning 注意
短链无法使用该接口返回 `rid`，如 `raw_urls` 中的第 `3` 和第 `4` 条链接只会返回 `room_id`。需要使用 `fetch_user_live_videos_by_room_id` 接口获取数据。
:::

### 全局格式化文件名 🟢

根据配置文件的全局格式化文件名。
::: details :page_facing_up: 格式化文件名规则
- `Windows` 文件名长度限制为 `255` 个字符, 开启了长文件名支持后为 `32,767` 个字符。
- `Unix` 文件名长度限制为 `255` 个字符。
- 取去除后的 `20` 个字符, 加上后缀, 一般不会超过 `255` 个字符。
- 开发者可以根据自己的需求自定义 `custom_fields` 字段，实现自定义文件名。
:::

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| naming_template | str | 文件的命名模板 |
| aweme_data | dict | 作品数据的字典 |
| custom_fields | dict | 用户自定义字段, 用于替代默认的字段值 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| file_name | str | 格式化后的文件名 |

<<< @/snippets/douyin/format-file-name.py{13,18,26,30,32-35}

### 创建用户目录 🟢

用于创建用户目录，如果目录已存在则不创建。

::: details :open_file_folder: 用户目录结构
如果未在配置文件中指定路径，则默认为 `Download`。支持绝对与相对路径。
```bash
├── Download
│   ├── douyin
│   │   ├── post
│   │   │   ├── user_nickname
│   │   │   │   ├── 2023-12-31_23-59-59_desc
│   │   │   │   │   ├── 2023-12-31_23-59-59_desc-video.mp4
│   │   │   │   │   ├── 2023-12-31_23-59-59_desc-desc.txt
│   │   │   │   │   └── 2023-12-31_23-59-59_desc-cover.jpg
│   │   │   │   │   └── ......
│   │   ├── like
│   │   ├── ...
```
:::

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| kwargs | dict | cli配置文件 |
| nickname | Union[str, int] | 用户昵称 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_path | Path | 用户目录路径对象 |

<<< @/snippets/douyin/user-folder.py#create-user-folder{17-19}

### 重命名用户目录 🟢

用于重命名用户目录。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| old_path | Path | 旧的用户目录路径对象 |
| new_nickname | str | 新的用户昵称 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| new_path | Path | 新的用户目录路径对象 |

<<< @/snippets/douyin/user-folder.py#rename-user-folder{23-27,29-32}

::: tip :bulb: 提示
如果目录不存在会先创建该用户目录再重命名。
:::

### 创建或重命名用户目录 🟢

用于创建或重命名用户目录。为上面2个接口的组合。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| kwargs | dict | cli配置文件 |
| local_user_data | dict | 本地用户数据 |
| current_nickname | str | 当前用户昵称 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_path | Path | 用户目录路径对象 |

::: tip :bulb: 提示
该接口很好的解决了用户改名之后重复重新下载的问题。集成在 `handler` 接口中。开发者无需关心，直接调用 `handler` 的数据接口即可。
:::


### 显示二维码 🔴

用于将url地址显示为二维码。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| qrcode_url | str | 二维码地址 |
| show_image | bool | 是否以图片文件显示，默认为False |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

<<< @/snippets/douyin/show-qrcode.py{4,5}

::: tip :bulb: 提示
选择是否显示图片，需要额外安装 `Pillow` 库。
:::

::: danger 警告
该接口已在 `0.0.1.6` 版本之后弃用。
:::

### json歌词转lrc歌词 🟢

用于将抖音原声的json格式的歌词转换为lrc格式的歌词。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| data | Union[str, list, dict] | json格式的歌词 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| lrc_lines | str | lrc格式的歌词 |

<<< @/snippets/douyin/json-2-lrc.py{94}

## crawler接口列表

### 用户信息接口 🟢

异步方法，用于获取用户信息数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserProfile | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 用户信息数据 |

### 主页作品接口 🟢

异步方法，用于获取主页作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserPost | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 主页作品数据 |

### 主页喜欢作品接口 🟢

异步方法，用于获取主页喜欢作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserLike | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 喜欢作品数据 |

### 主页收藏作品接口 🟢

异步方法，用于获取主页收藏作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserCollection | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_post_json() | dict | 收藏作品数据 |

### 收藏夹接口 🟢

异步方法，用于获取收藏夹数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserCollects | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 收藏夹数据 |

### 收藏夹作品接口 🟢

异步方法，用于获取收藏夹作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserCollectsVideo | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 收藏夹作品数据 |

### 音乐收藏接口 🟢

异步方法，用于获取音乐收藏数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserMusicCollection | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 音乐收藏数据 |

### 合集作品接口 🟢

异步方法，用于获取合集作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserMix | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 合集作品数据 |

### 作品详情接口 🟢

异步方法，用于获取作品详情数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | PostDetail | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 作品详情数据 |

### 作品评论接口 🟡

异步方法，用于获取作品评论数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | PostDetail | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 作品评论数据 |


### 首页推荐作品接口 🟡

异步方法，用于获取首页推荐作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | PostDetail | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 首页推荐作品数据 |

### 关注作品接口 🟡

异步方法，用于获取关注作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | PostDetail | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 关注作品数据 |

### 朋友作品接口 🟢

异步方法，用于获取朋友作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | PostDetail | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_post_json() | dict | 朋友作品数据 |

### 相关推荐作品接口 🟢

异步方法，用于获取相关推荐作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | PostDetail | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 相关推荐作品数据 |

### 直播信息接口 🟢

异步方法，用于获取直播信息数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserLive | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 直播信息数据 |

### 直播接口地址(room_id) 🟢

异步方法，用于获取直播接口地址数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserLive2 | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 直播接口地址数据 |

### 关注用户直播接口 🟢

异步方法，用于获取关注用户直播数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | FollowingUserLive | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 关注用户直播数据 |

### 定位上一次作品接口 🟡

异步方法，用于定位上一次作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserPost | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 定位上一次作品数据 |

### SSO获取二维码接口 🔴

异步方法，用于获取SSO登录二维码数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | LoginGetQr | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | SSO获取二维码数据 |

### SSO检查扫码状态接口 🔴

异步方法，用于检查SSO登录扫码状态数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | LoginCheckQr | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_response() | dict | SSO检查扫码状态数据 |

### SSO检查登录状态接口 🔴

异步方法，用于检查SSO登录状态数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | LoginCheckQr | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | SSO检查登录状态数据 |

### 用户关注列表接口 🟢

异步方法，用于获取用户关注列表数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserFollowing | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 用户关注列表数据 |

### 用户粉丝列表接口 🟢

异步方法，用于获取用户粉丝列表数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserFollower | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 用户粉丝列表数据 |

### 直播弹幕初始化接口 🟢

异步方法，用于获取直播弹幕初始化数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | LiveImFetch | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 直播弹幕初始化数据 |

### 查询用户接口 🟢

异步方法，用于查询用户数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | QueryUser | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json() | dict | 查询用户数据 |

### 作品统计接口 🟢

异步方法，用于获取作品统计数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | PostStats | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_post_json() | dict | 作品统计数据 |

::: tip :bulb: 提示
- 当不需要使用过滤器时，可以直接调用`crawler`接口，将直接返回数据字典。
:::

## dl接口列表

### 保存最后请求的作品ID 🟢

用于保存最后请求的作品ID，用于下一次请求主页作品的参数。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id | str | 用户ID |
| aweme_id | str | 作品ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |


### 筛选指定日期区间内的作品 🟢

用于筛选指定日期区间内的作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 作品数据的字典 |
| interval | str | 日期区间 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| filtered_aweme_datas | Union[list[dict], dict, None] | 筛选后的作品数据 |

### 创建下载任务 🟢


### 处理下载任务 🟢


### 下载原声 🟢


### 下载封面 🟢


### 下载文案 🟢


### 下载视频🟢


### 下载图集 🟢


### 创建原声下载任务 🟢


### 处理原声下载任务 🟢


### 创建直播流下载任务 🟢


### 直播流下载 🟢

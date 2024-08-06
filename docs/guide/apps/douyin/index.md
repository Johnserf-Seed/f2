---
outline: deep
---

# 接口列表

::: tip 注意
🟢代表已经实现，🟡代表正在实现或修改，🟤代表暂时不实现，🔵代表未来可能实现，🔴代表将会弃用。
:::

::: details handler接口列表

|     CLI接口             |         方法        |
| :------------------ | :-------------------  |
| 下载单个作品          | `handle_one_video`      |
| 下载用户发布作品       | `handle_user_post`      |
| 下载用户喜欢作品       | `handle_user_like`      |
| 下载用户收藏原声       | `handle_user_music_collection` |
| 下载用户收藏作品       | `handle_user_collection` |
| 下载用户合集作品       | `handle_user_mix`       |
| 下载用户直播流         | `handle_user_live`      |
| 下载用户首页推荐作品    | `handle_user_feed`      |
| 下载相似作品          | `handle_related`        |
| 下载好友作品          | `handle_friend_feed`      |

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
| 直播间wss负载数据      | `fetch_live_im`      |     🟢      |
| 直播间wss弹幕         | `fetch_live_danmaku` |     🟢      |
| 关注用户的直播间信息    | `fetch_user_following_lives` |     🟢      |
:::

::: details utils接口列表

| 工具类接口          | 类名            | 方法               | 状态 |
| :---------------- | :-------------- | :------------------  | :--: |
| 管理客户端配置     | `ClientConfManager`   |                  |  🟢  |
| 生成真实msToken    | `TokenManager`     | `gen_real_msToken`       |  🟢  |
| 生成虚假msToken     | `TokenManager`     | `gen_false_msToken`      |  🟢  |
| 生成ttwid          | `TokenManager`     | `gen_ttwid`              |  🟢  |
| 生成webid          | `TokenManager`     | `gen_webid`              |  🟢  |
| 生成verify_fp      | `VerifyFpManager`  | `gen_verify_fp`          |  🟢  |
| 生成s_v_web_id     | `VerifyFpManager`  | `gen_s_v_web_id`         |  🟢  |
| 生成直播signature | `DouyinWebcastSignature` | `get_signature` |  🟢  |
| 使用接口模型生成直播wss签名参数 | `WebcastSignatureManager` | `model_2_endpoint` |  🟢  |
| 使用接口地址生成Xb参数      | `XBogusManager`    | `str_2_endpoint`   |  🟢  |
| 使用接口模型生成Xb参数      | `XBogusManager`    | `model_2_endpoint`   |  🟢  |
| 使用接口地址生成Ab参数      | `ABogusManager`    | `str_2_endpoint`   |  🟢  |
| 使用接口模型生成Ab参数      | `ABogusManager`    | `model_2_endpoint`   |  🟢  |
| 提取单个用户id       | `SecUserIdFetcher` | `get_sec_user_id`         |  🟢  |
| 提取列表用户id       | `SecUserIdFetcher` | `get_all_sec_user_id`     |  🟢  |
| 提取单个作品id       | `AwemeIdFetcher`   | `get_aweme_id`            |  🟢  |
| 提取列表作品id       | `AwemeIdFetcher`   | `get_all_aweme_id`        |  🟢  |
| 提取单个合集id       | `MixIdFetcher`     | `get_mix_id`              |  🟢  |
| 提取列表合集id       | `MixIdFetcher`     | `get_all_mix_id`          |  🟢  |
| 提取单个直播间号      | `WebCastIdFetcher` | `get_webcast_id`          |  🟢  |
| 提取列表直播间号       | `WebCastIdFetcher` | `get_all_webcast_id`      |  🟢  |
| 全局格式化文件名      | -                 | `format_file_name`        |  🟢  |
| 创建用户目录         | -                 | `create_user_folder`      |  🟢  |
| 重命名用户目录       | -                 | `rename_user_folder`      |  🟢  |
| 创建或重命名用户目录   | -                 | `create_or_rename_user_folder` | 🟢 |
| 显示二维码           | -                | `show_qrcode`             |  🟢  |
| json歌词转lrc歌词 | -                | `json_2_lrc`            |  🟢  |
:::

::: details cralwer接口列表

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
| SSO获取二维码接口地址 | `DouyinCrawler` | `fetch_login_qrcode` |  🔴  |
| SSO检查扫码状态接口地址 | `DouyinCrawler` | `fetch_check_qrcode` |  🔴  |
| SSO检查登录状态接口地址 | `DouyinCrawler` | `fetch_check_login` |  🔴  |
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
| 直播间聊天消息 | `DouyinWebSocketCrawler` | `WebcastLeaveMessage` |  🟢  |
| 直播间礼物消息 | `DouyinWebSocketCrawler` | `WebcastGiftMessage` |  🟢  |
| 直播间用户关注消息 | `DouyinWebSocketCrawler` | `WebcastSocialMessage` |  🟢  |
| 直播间用户关注消息 | `DouyinWebSocketCrawler` | `WebcastFollowMessage` |  🟢  |
| 直播间在线观众排行榜 | `DouyinWebSocketCrawler` | `WebcastRoomUserSeqMessage` |  🟢  |
| 直播间粉丝团更新消息 | `DouyinWebSocketCrawler` | `WebcastUpdateFanTicketMessage` |  🟢  |
| 直播间文本消息 | `DouyinWebSocketCrawler` | `WebcastCommonTextMessage` |  🟢  |
| 直播间对战积分消息 | `DouyinWebSocketCrawler` | `WebcastMatchAgainstScoreMessage` |  🟢  |
| 直播间粉丝团消息 | `DouyinWebSocketCrawler` | `WebcastFansclubMessage` |  🟢  |

:::

::: details dl接口列表

| 下载器接口     | 类名        | 方法          | 状态 |
| :----------- | :--------- | :----------  | :--: |
| 保存最后一次请求的aweme_id | `DouyinDownloader` | `save_last_aweme_id` |  🟢  |
| 筛选指定日期区间内的作品 | `DouyinDownloader` | `filter_aweme_datas_by_interval` |  🟢  |
| 创建下载任务   | `DouyinDownloader` | `create_download_task` |  🟢  |
| 处理下载任务   | `DouyinDownloader` | `handler_download` |  🟢  |
| 创建原声下载任务 | `DouyinDownloader` | `create_music_download_tasks` |  🟢  |
| 处理原声下载任务 | `DouyinDownloader` | `handler_music_download` |  🟢  |
| 创建流下载任务  | `DouyinDownloader` | `create_stream_tasks` |  🟢  |
| 处理流下载任务  | `DouyinDownloader` | `handle_stream` |  🟢  |
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

<<< @/snippets/douyin/user-get-add.py{18,20-22}

::: tip 提示
此为cli模式的接口，开发者可自行定义创建用户目录的功能。
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
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserPostFilter | AsyncGenerator | 发布作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-post.py{16-20}

### 用户喜欢作品数据 🟢

异步方法，用于获取指定用户喜欢的视频列表，需开放喜欢列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

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
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserMusicCollectionFilter | AsyncGenerator | 收藏音乐数据过滤器，包含音乐数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-collection.py#user-collection-music-snippet{17}

### 用户收藏作品数据 🟢

异步方法，用于获取指定用户收藏的视频列表，只能爬登录了账号的收藏作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserCollectionFilter | AsyncGenerator | 收藏作品数据过滤器，包含作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-collection.py#user-collection-music-snippet{16}

### 用户收藏夹数据 🟢

异步方法，用于获取指定用户的收藏夹列表，不是收藏夹作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserCollectsFilter | AsyncGenerator | 收藏夹数据过滤器，包含收藏夹数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-collects.py#user-collects-snippet{17}

### 用户收藏夹作品数据 🟢

异步方法，用于获取指定用户收藏夹的视频列表，收藏夹作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| collect_id| str | 收藏夹ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserCollectsVideosFilter | AsyncGenerator | 收藏夹作品数据过滤器，包含收藏夹作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-collects.py#user-collects-videos-snippet{17-20}

### 用户合集作品数据 🟢

异步方法，用于获取指定用户合集的视频列表，合集视频的mix_id是一致的，从单个作品数据接口中获取即可。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| mix_id| str | 合集ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserMixFilter | AsyncGenerator | 合集作品数据过滤器，包含合集作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-mix.py{16,19-21}

### 用户直播流数据 🟢

异步方法，用于获取指定用户的直播。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_id| str | 直播间RID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_data | dict | 直播数据字典，包含直播ID、直播标题、直播状态、观看人数、子分区、主播昵称等 |

<<< @/snippets/douyin/user-live.py{15}

### 用户直播流数据2 🟢

异步方法，用于获取指定用户的直播，webcast_id与room_id为2个独立参数，由不同接口解析。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| room_id| str | 直播间ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_data | dict | 直播数据字典，包含直播ID、直播标题、直播状态、观看人数、子分区、主播昵称等 |

<<< @/snippets/douyin/user-live-room-id.py{15-17}

### 用户首页推荐作品数据 🟢

异步方法，用于获取指定用户的首页推荐作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserPostFilter | AsyncGenerator | 首页推荐作品数据过滤器，包含推荐作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-feed.py{17-20}

### 相似作品数据 🟢

异步方法，用于获取指定作品的相似作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_id| str | 作品ID |
| filterGids| str | 过滤的Gids |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |


| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| PostRelatedFilter | dict | 相关推荐作品数据过滤器，包含相关作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/aweme-related.py{16-18}


### 好友作品数据 🟢

异步方法，用于获取好友的作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| cursor| str | 页码，初始为0 |
| level| int | 作品级别，初始为1 |
| pull_type| int | 拉取类型，初始为0 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| FriendFeedFilter | AsyncGenerator | 好友作品数据过滤器，包含好友作品数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-friend.py{16}

### 关注用户数据 🟢

异步方法，用于获取指定用户关注的用户列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_id| str | 用户ID |
| sec_user_id| str | 用户ID |
| offset| int | 页码，初始为0 |
| count| int | 页数，初始为20 |
| source_type| int | 源类型，初始为4 |
| min_time | int | 最早关注时间戳，初始为0 |
| max_time | int | 最晚关注时间戳，初始为0 |
| max_counts| float | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserFollowingFilter | AsyncGenerator | 关注用户数据过滤器，包含关注用户数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-following.py{18-20,22-29}

### 粉丝用户数据 🟢

异步方法，用于获取指定用户的粉丝列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_id| str | 用户ID |
| sec_user_id| str | 用户ID |
| offset| int | 页码，初始为0 |
| count| int | 页数，初始为20 |
| source_type| int | 源类型，初始为1 |
| min_time | int | 最早关注时间戳，初始为0 |
| max_time | int | 最晚关注时间戳，初始为0 |
| max_counts| float | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserFollowerFilter | AsyncGenerator | 粉丝用户数据过滤器，包含粉丝用户数据的_to_raw、_to_dict、_to_list方法 |

<<< @/snippets/douyin/user-follower.py{18-20,22-29}

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

<<< @/snippets/douyin/user-live-im-fetch.py{5-14,30-42}

### 直播间wss弹幕 🟢

异步方法，用于获取直播间wss弹幕数据，使用内置多个回调处理不同类型的消息。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| room_id| str | 直播间ID |
| user_unique_id| str | 用户ID |
| internal_ext| str | 内部扩展参数 |
| cursor| str | 弹幕页码 |
| callback| dict | 自定义弹幕回调函数（待加入） |

| 回调 | 说明 |
| :--- | :--- |
| WebcastRoomMessage | 直播间房间消息 |
| WebcastLikeMessage | 直播间点赞消息 |
| WebcastMemberMessage | 直播间观众加入消息 |
| WebcastChatMessage | 直播间聊天消息 |
| WebcastGiftMessage | 直播间礼物消息 |
| WebcastSocialMessage | 直播间用户关注消息 |
| WebcastRoomUserSeqMessage | 直播间在线观众排行榜 |
| WebcastUpdateFanTicketMessage | 直播间粉丝团更新消息 |
| WebcastCommonTextMessage | 直播间文本消息 |
| WebcastMatchAgainstScoreMessage | 直播间对战积分消息 |
| WebcastFansclubMessage | 直播间粉丝团消息 |
| TODO: WebcastRanklistHourEntranceMessage | 直播间小时榜消息 |
| TODO: WebcastRoomStatsMessage | 直播间统计消息 |
| TODO: WebcastLiveShoppingMessage | 直播间购物车消息 |
| TODO: WebcastLiveEcomGeneralMessage | 直播间电商消息 |
| TODO: WebcastProductChangeMessage | 直播间商品变更消息 |
| TODO: WebcastRoomStreamAdaptationMessage | 直播间流适配消息 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| self.websocket | WebSocket | 弹幕WebSocket对象 |

<<< @/snippets/douyin/user-live-im-fetch.py{17-26,44-50}

### 关注用户的直播间信息 🟢

异步方法，用于获取关注用户的直播间信息列表，需要登录账号。

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

<<< @/snippets/douyin/sso-login.py{5}

::: danger 警告
由于扫码登录受风控影响较大,多数cookie都无法使用。为了保障体验，建议使用--auto-cookie命令自动从浏览器获取cookie，更多使用帮助参考cli命令。
:::


## utils接口列表

### 管理客户端配置 🟢

类方法，用于管理客户端配置

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

::: tip 提示
默认为126位，也可调用`from f2.utils.utils import gen_random_str`，生成不同长度的虚假msToken。
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

<<< @/snippets/douyin/webcast-signature.py#webcast-signature-snippet{4-8}

### 使用接口模型生成直播wss签名参数 🟢

类方法，用于使用不同接口数据模型生成直播wss签名参数。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_agent | str | 用户代理 |
| base_endpoint | str | 端点 |
| params | dict | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_endpoint | str | 带wss签名参数的完整地址 |

<<< @/snippets/douyin/webcast-signature.py#webcast-signature-manager-snippet{10-14}


### 使用接口地址生成Xb参数 🟢

类方法，用于直接使用接口地址生成Xbogus参数，部分接口不校验。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_agent | str | 用户代理 |
| endpoint | str | 接口端点 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_endpoint | str | 带Xbogus参数的完整地址 |

<<< @/snippets/douyin/xbogus.py#str-2-endpoint-snippet{6,7}

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

::: tip 提示
本项目的残血版Ab算法的UA参数为固定值，`Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0`。
:::

### 提取单个用户id 🟢

类方法，用于提取单个用户id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 用户主页地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id | str | 用户ID |

<<< @/snippets/douyin/sec-user-id.py#single-user-id-snippet{7}

### 提取列表用户id 🟢

类方法，用于提取列表用户id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 用户主页地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_ids | list | 用户ID列表 |

<<< @/snippets/douyin/sec-user-id.py#multi-user-id-snippet{14,17}

### 提取单个作品id 🟢

类方法，用于提取单个作品id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 作品地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_id | str | 作品ID |

<<< @/snippets/douyin/aweme-id.py#single-aweme-id-snippet{5,6}

### 提取列表作品id 🟢

类方法，用于提取列表作品id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 作品地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_ids | list | 作品ID列表 |

<<< @/snippets/douyin/aweme-id.py#multi-aweme-id-snippet{15,18}

### 提取合集id 🟢

类方法，用于从合集链接中提取合集id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 合集地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| mix_id | str | 合集ID |

<<< @/snippets/douyin/mix-id.py#single-mix-id-snippet{6,7}

### 提取列表合集id 🟢

类方法，用于从合集链接列表中提取合集id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 合集地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| mix_ids | list | 合集ID列表 |

<<< @/snippets/douyin/mix-id.py#multi-mix-id-snippet{7-10,13,16}

### 提取单个直播间号 🟢

类方法，用于提取单个直播间号。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 直播间地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_id | str | 直播间RID |


<<< @/snippets/douyin/webcast-id.py#single-webcast-id-snippet{6,7}

### 提取列表直播间号 🟢

类方法，用于提取列表直播间号。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 直播间地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_ids | list | 直播间RID列表 |

<<< @/snippets/douyin/webcast-id.py#multi-webcast-id-snippet{7-13,16,19}

::: tip 如何分辨r_id与room_id
r_id是直播间的短链标识，room_id是直播间的唯一标识。
如`https://live.douyin.com/775841227732`中的`775841227732`就是r_id，而`https://webcast.amemv.com/douyin/webcast/reflow/7318296342189919011`中的`7318296342189919011`就是room_id。
这2个链接都指向同一个直播间。
:::

::: warning 注意
短链无法使用该接口返回Rid，如raw_urls中的第3和第4条链接只会返回room_id。需要搭配使用`fetch_user_live_videos_by_room_id`接口获取数据。
:::

### 全局格式化文件名 🟢

根据配置文件的全局格式化文件名。
::: details 格式化文件名规则
- windows 文件名长度限制为 255 个字符, 开启了长文件名支持后为 32,767 个字符。
- Unix 文件名长度限制为 255 个字符。
- 取去除后的20个字符, 加上后缀, 一般不会超过255个字符。
:::

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| naming_template | str | 文件的命名模板 |
| aweme_data | dict | 作品数据的字典 |
| custom_fields | dict | 用户自定义字段, 用于替代默认的字段值 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| file_name | str | 格式化后的文件名 |

<<< @/snippets/douyin/format-file-name.py{13,19,28,32,34,36-39}

### 创建用户目录 🟢

用于创建用户目录，如果目录已存在则不创建。

::: details 用户目录结构
如果未在配置文件中指定路径，则默认为 `Download`。支持绝对与相对路径。
```bash
├── Download
│   ├── douyin
│   │   ├── post
│   │   │   ├── user_nickname
│   │   │   │   ├── 2023-12-31_23-59-59_desc
│   │   │   │   │   ├── 2023-12-31_23-59-59_desc-video.mp4
│   │   │   │   │   ├── 2023-12-31_23-59-59_desc-desc.txt
│   │   │   │   │   └── 2023-12-31_23-59-59_desc-coder.jpg
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

::: tip 提示
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

::: tip 提示
该接口很好的解决了用户改名之后重复重新下载的问题。集合在handler接口的`get_or_add_user_data`中，开发者无需关心直接调用handler的数据接口即可。
:::


### 显示二维码 🟢

用于将url地址显示为二维码。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| qrcode_url | str | 二维码地址 |
| show_image | bool | 是否显示二维码图片 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

<<< @/snippets/douyin/show-qrcode.py{4,5}

::: tip 提示
show_image (bool): 是否显示图像，True 表示显示，False 表示在控制台显示
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

## crawler接口

### 用户信息接口地址 🟢

异步方法，用于获取用户信息数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserProfile | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| parse_json() | dict | 用户信息数据 |

### 主页作品接口地址 🟢

异步方法，用于获取主页作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserPost | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| parse_json() | dict | 主页作品数据 |

### 喜欢作品接口地址 🟢

异步方法，用于获取喜欢作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserLike | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| parse_json() | dict | 喜欢作品数据 |

### 收藏作品接口地址 🟢

异步方法，用于获取收藏作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserCollection | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| parse_json() | dict | 收藏作品数据 |

### 收藏夹接口地址 🟢

异步方法，用于获取收藏夹数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserCollects | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| parse_json() | dict | 收藏夹数据 |

### 收藏夹作品接口地址 🟢

异步方法，用于获取收藏夹作品数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserCollectsVideo | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| parse_json() | dict | 收藏夹作品数据 |

### 音乐收藏接口地址 🟢

异步方法，用于获取音乐收藏数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserMusicCollection | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| parse_json() | dict | 音乐收藏数据 |

## dl接口

### 保存最后一次请求的aweme_id 🟢

用于保存最后一次请求的aweme_id，用于下一次请求主页作品的参数。

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


### 创建原声下载任务 🟢


### 处理原声下载任务 🟢


### 创建流下载任务 🟢


### 处理流下载任务 🟢
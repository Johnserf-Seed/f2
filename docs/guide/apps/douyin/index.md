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
| 下载单个作品          | handle_one_video      |
| 下载用户发布作品       | handle_user_post      |
| 下载用户喜欢作品       | handle_user_like      |
| 下载用户收藏作品       | handle_user_collect   |
| 下载用户合辑作品       | handle_user_mix       |
| 下载用户直播流         | handle_user_live      |
| 下载用户首页推荐作品    | handle_user_feed      |

|     数据与功能接口     |         方法           | 开发者接口  |
| :------------------ | :-------------------  | :--------: |
| 单个作品数据          | fetch_one_video        |     🟢      |
| 用户发布作品数据       | fetch_user_post_videos |     🟢      |
| 用户喜欢作品数据       | fetch_user_like_videos |     🟢      |
| 用户收藏作品数据       | fetch_user_collect_videos |  🟢      |
| 用户合辑作品数据       | fetch_user_mix_videos  |     🟢      |
| 用户直播流数据         | fetch_user_live_videos |     🟢      |
| 用户直播流数据2        | fetch_user_live_videos_by_room_id |     🟢      |
| 用户首页推荐作品数据    | fetch_user_feed_videos |     🟢      |
| ......               | ......                 |    🔵      |
| 用户信息              | handler_user_profile   |     🟢      |
| 获取指定用户名         | get_user_nickname      |      🔴     |
| 创建用户记录与目录      | get_or_add_user_data   |     🟡🔴  |
| 创建作品下载记录        | get_or_add_video_data  |     🟢      |
| SSO登录              |  handle_sso_login       |     🟢      |
:::

::: details utils接口列表

| 开发者接口          | 类名            | 方法               | 状态 |
| :---------------- | :-------------- | :------------------  | :--: |
| 生成真实msToken    | TokenManager     | gen_real_msToken       |  🟢  |
| 生成虚假msToken     | TokenManager     | gen_false_msToken      |  🟢  |
| 生成ttwid          | TokenManager     | gen_ttwid              |  🟢  |
| 生成verify_fp      | VerifyFpManager  | gen_verify_fp          |  🟢  |
| 生成s_v_web_id     | VerifyFpManager  | gen_s_v_web_id         |  🟢  |
| 生成Xbogus参数      | XBogusManager    | to_complete_endpoint   |  🟢  |
| 提取单个用户id       | SecUserIdFetcher | get_sec_user_id         |  🟢  |
| 提取列表用户id       | SecUserIdFetcher | get_all_sec_user_id     |  🟢  |
| 提取单个作品id       | AwemeIdFetcher   | get_aweme_id            |  🟢  |
| 提取列表作品id       | AwemeIdFetcher   | get_all_aweme_id        |  🟢  |
| 提取合辑id          | MixIdFetcher     | -                       |  🟤  |
| 提取单个直播间号      | WebCastIdFetcher | get_webcast_id          |  🟢  |
| 提取列表直播间号      | WebCastIdFetcher | get_all_webcast_id      |  🟢  |
| 获取请求count数列表  | -                 | get_request_sizes       |  🔴  |
| 全局格式化文件名     | -                 | format_file_name        |  🟢  |
| 创建用户目录         | -                 | create_user_folder      |  🟢  |
| 重命名用户目录       | -                | rename_user_folder      |  🟢  |
| 创建或重命名用户目录  | -                 | create_or_rename_user_folder | 🟢 |
| 提取低版本接口的desc  | -                | extract_desc_from_share_desc | 🔴 |
| 显示二维码           | -                | show_qrcode             |  🟢  |
::: tip 注意
合辑id其实就是作品id，使用`AwemeIdFetcher`即可。
:::

::: details cralwer接口列表

| 爬虫url接口    | 类名       | 方法          | 状态 |
| :----------- | :--------- | :----------  | :--: |
| 用户信息接口地址 | DouyinCrawler | fetch_user_profile |  🟢  |
| 主页作品接口地址 | DouyinCrawler | fetch_user_post |  🟢  |
| 喜欢作品接口地址 | DouyinCrawler | fetch_user_like |  🟢  |
| 收藏作品接口地址 | DouyinCrawler | fetch_user_collect |  🟢  |
| 合辑作品接口地址 | DouyinCrawler | fetch_user_mix |  🟢  |
| 作品详情接口地址 | DouyinCrawler | fetch_post_detail |  🟢  |
| 作品评论接口地址 | DouyinCrawler | fetch_post_comment |  🟡  |
| 推荐作品接口地址 | DouyinCrawler | fetch_post_feed |  🟡  |
| 关注作品接口地址 | DouyinCrawler | fetch_follow_feed |  🟡  |
| 朋友作品接口地址 | DouyinCrawler | fetch_friend_feed |  🟡  |
| 相关推荐作品接口地址 | DouyinCrawler | fetch_post_related |  🟡  |
| 直播接口地址 | DouyinCrawler | fetch_live |  🟢  |
| 直播接口地址（room_id） | DouyinCrawler | fetch_live_room_id |  🟢  |
| 关注用户直播接口地址 | DouyinCrawler | fetch_follow_live |  🟡  |
| 定位上一次作品接口地址 | DouyinCrawler | fetch_locate_post |  🟡  |
| SSO获取二维码接口地址 | DouyinCrawler | fetch_login_qrcode |  🟢  |
| SSO检查扫码状态接口地址 | DouyinCrawler | fetch_check_qrcode |  🟢  |
| SSO检查登录状态接口地址 | DouyinCrawler | fetch_check_login |  🟡  |

:::

::: details dl接口列表

| 下载器接口     | 类名        | 方法          | 状态 |
| :----------- | :--------- | :----------  | :--: |
| 保存最后一次请求的aweme_id | DouyinDownloader | save_last_aweme_id |  🟢  |
| 创建下载任务   | DouyinDownloader | create_download_task |  🟢  |
| 处理下载任务   | DouyinDownloader | handle_download |  🟢  |
| 创建流下载任务  | DouyinDownloader | create_stream_tasks |  🟢  |
| 处理流下载任务  | DouyinDownloader | handle_stream |  🟢  |
:::

## handler接口列表

### 单个作品数据

异步方法，用于获取单个视频。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_id| str | 视频ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| video_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称等 |

<<< @/snippets/douyin/one-video.py{5,7}

### 用户发布作品数据

异步方法，用于获取用户发布的视频列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| video_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/douyin/user-post.py{5,7,12}

### 用户喜欢作品数据

异步方法，用于获取指定用户喜欢的视频列表，需开放喜欢列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/douyin/user-like.py{5,7,12}

### 用户收藏作品数据

异步方法，用于获取指定用户收藏的视频列表，只能爬登录了账号的收藏作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/douyin/user-collect.py{6,11}

### 用户合辑作品数据

异步方法，用于获取指定用户合辑的视频列表，合辑视频的mix_id是一致的，从单个作品数据接口中获取即可。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| mix_id| str | 合集ID |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/douyin/user-mix.py{5,7,12}

### 用户直播流数据

异步方法，用于获取指定用户的直播。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_id| str | 直播间RID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_data | dict | 直播数据字典，包含直播ID、直播标题、直播状态、观看人数、子分区、主播昵称等 |

<<< @/snippets/douyin/user-live.py{5}

### 用户直播流数据2

异步方法，用于获取指定用户的直播，webcast_id与room_id为2个独立参数，由不同接口解析。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| room_id| str | 直播间ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_data | dict | 直播数据字典，包含直播ID、直播标题、直播状态、观看人数、子分区、主播昵称等 |

<<< @/snippets/douyin/user-live-room-id.py{5}

### 用户信息

异步方法，用于获取指定用户的信息，不可以直接解析Filter的数据，需要使用自定义的_to_dict()或_to_list()方法。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserProfileFilter | _to_dict() | 自定义的接口数据过滤器 | 用户数据字典，包含用户ID、用户昵称、用户签名、用户头像等 |

<<< @/snippets/douyin/user-profile.py{5,6}

### 获取指定用户名

异步方法，用于获取指定用户的昵称，如果不存在，则从服务器获取并存储到数据库中。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |
| db | AsyncUserDB | 用户数据库 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_nickname | str | 用户昵称 |

<<< @/snippets/douyin/user-nickname.py{5-7}

### 创建用户记录与目录

异步方法，用于获取或创建用户数据同时创建用户目录。


| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| kwargs | dict | cli字典数据，需获取path参数 |
| sec_user_id| str | 用户ID |
| db | AsyncUserDB | 用户数据库 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_path | Path | 用户目录路径对象 |

<<< @/snippets/douyin/user-get-add.py{5-8}

::: tip 提示
此为cli模式的接口，开发者可自行定义创建用户目录的功能。
:::

### 创建作品下载记录

异步方法，用于获取或创建作品数据同时创建作品目录。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 作品数据字典 |
| db | AsyncVideoDB | 作品数据库 |
| ignore_fields | list | 忽略的字段列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
|None | None | 无 |

<<< @/snippets/douyin/video-get-add.py{5,8-10}

### SSO登录

异步方法，用于处理用户SSO登录，获取用户的cookie。


| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
|None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| is_login | bool | 是否登录成功 |
| login_cookie | str | 登录cookie |

<<< @/snippets/douyin/sso-login.py

::: danger 警告
由于扫码登录受风控影响较大,多数cookie都无法使用。为了保障体验，建议使用--auto-cookie命令自动从浏览器获取cookie，更多使用帮助参考cli命令。
:::

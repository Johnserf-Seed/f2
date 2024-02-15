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
| 创建用户记录与目录      | get_or_add_user_data   |     🟡  |
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
| 使用接口地址生成Xb参数      | XBogusManager    | str_2_endpoint   |  🟢  |
| 使用接口模型生成Xb参数      | XBogusManager    | model_2_endpoint   |  🟢  |
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

### 单个作品数据 🟢

异步方法，用于获取单个视频。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_id| str | 视频ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| video_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称等 |

<<< @/snippets/douyin/one-video.py{15,17}

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
| video_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/douyin/user-post.py{15,17-20,25-28}

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
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/douyin/user-like.py{15,17-20,25-28}

### 用户收藏作品数据 🟢

异步方法，用于获取指定用户收藏的视频列表，只能爬登录了账号的收藏作品。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| max_cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/douyin/user-collect.py{16-17,22-25}

### 用户合辑作品数据 🟢

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

<<< @/snippets/douyin/user-mix.py{16-18,21-24,29-32}

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

<<< @/snippets/douyin/user-live-room-id.py{16-18}

### 用户信息 🟢

异步方法，用于获取指定用户的信息，不可以直接解析Filter的数据，需要使用自定义的_to_dict()或_to_list()方法。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserProfileFilter | _to_dict() | 自定义的接口数据过滤器 | 用户数据字典，包含用户ID、用户昵称、用户签名、用户头像等 |

<<< @/snippets/douyin/user-profile.py{15-16}

### 获取指定用户名 🔴

异步方法，用于获取指定用户的昵称，如果不存在，则从服务器获取并存储到数据库中。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id| str | 用户ID |
| db | AsyncUserDB | 用户数据库 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_nickname | str | 用户昵称 |

<<< @/snippets/douyin/user-nickname.py{17,19-21}

### 创建用户记录与目录 🟡

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
|None | None | 无 |

<<< @/snippets/douyin/video-get-add.py{6,23-25}

### SSO登录 🟢

异步方法，用于处理用户SSO登录，获取用户的cookie。


| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
|None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| is_login | bool | 是否登录成功 |
| login_cookie | str | 登录cookie |

<<< @/snippets/douyin/sso-login.py{5}

::: danger 警告
由于扫码登录受风控影响较大,多数cookie都无法使用。为了保障体验，建议使用--auto-cookie命令自动从浏览器获取cookie，更多使用帮助参考cli命令。
:::

## utils接口列表

### 生成真实msToken 🟢

静态方法，用于生成真实的msToken，当出现错误时返回虚假的值。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| msToken | str | 真实的msToken |

<<< @/snippets/douyin/mstoken-real.py{4}

### 生成虚假msToken 🟢

静态方法，用于生成随机虚假的msToken，不同端点的msToken长度不同。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| msToken | str | 虚假的msToken |

<<< @/snippets/douyin/mstoken-false.py{4}

::: tip 提示
默认为126位，也可调用`from f2.utils.utils import gen_random_str`，生成不同长度的虚假msToken。
:::

### 生成ttwid 🟢

静态方法，用于生成ttwid，部分请求必带。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| ttwid | str | ttwid参数 |

<<< @/snippets/douyin/ttwid.py{4}

### 生成verify_fp 🟢

静态方法，用于生成verify_fp，部分请求必带。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| verify_fp | str | verify_Fp与fp参数 |

<<< @/snippets/douyin/verify_fp.py{4}

### 生成s_v_web_id 🟢

静态方法，用于生成s_v_web_id，部分请求必带，即verify_fp值。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| s_v_web_id | str | s_v_web_id参数 |

<<< @/snippets/douyin/s_v_web_id.py{4}

### 使用接口地址生成Xb参数 🟢

静态方法，用于直接使用接口地址生成Xbogus参数，部分接口不校验。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| endpoint | str | 接口端点 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_endpoint | str | 带Xbogus参数的完整地址 |

<<< @/snippets/douyin/xbogus.py#str-2-endpoint-snippet{6,7}

### 使用接口模型生成Xb参数 🟢

静态方法，用于使用不同接口数据模型生成Xbogus参数，部分接口不校验。


| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| endpoint | str | 端点 |
| params | dict | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_endpoint | str | 带Xbogus参数的完整地址 |

使用模型生成接口地址，需要先创建一个模型对象，然后调用`model_2_endpoint`方法。

<<< @/snippets/douyin/xbogus.py#model-2-endpoint-snippet{8-10,13-15}

还可以使用爬虫引擎与过滤器采集数据。

<<< @/snippets/douyin/xbogus.py#model-2-endpoint-2-filter-snippet{22-27}

更加抽象的高级方法可以直接调用handler接口的`handler_user_profile`。

::: tip 提示
本项目中的UA参数为固定值，`Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
      like Gecko) Chrome/104.0.0.0 Safari/537.36`。
:::

### 提取单个用户id 🟢

静态方法，用于提取单个用户id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 用户主页地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_id | str | 用户ID |

<<< @/snippets/douyin/sec-user-id.py#single-user-id-snippet{7}

### 提取列表用户id 🟢

静态方法，用于提取列表用户id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 用户主页地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_user_ids | list | 用户ID列表 |

<<< @/snippets/douyin/sec-user-id.py#multi-user-id-snippet{14,17}

### 提取单个作品id 🟢

静态方法，用于提取单个作品id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 作品地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_id | str | 作品ID |

<<< @/snippets/douyin/aweme-id.py#single-aweme-id-snippet{5,6}

### 提取列表作品id 🟢

静态方法，用于提取列表作品id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 作品地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_ids | list | 作品ID列表 |

<<< @/snippets/douyin/aweme-id.py#multi-aweme-id-snippet{15,18}

### 提取合辑id 🟤

静态方法，用于提取合辑id，合辑id其实就是作品id，使用`AwemeIdFetcher`即可。


### 提取单个直播间号 🟢

静态方法，用于提取单个直播间号。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 直播间地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_id | str | 直播间RID |


<<< @/snippets/douyin/webcast-id.py#single-webcast-id-snippet{5,6}

### 提取列表直播间号 🟢

静态方法，用于提取列表直播间号。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 直播间地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| webcast_ids | list | 直播间RID列表 |

<<< @/snippets/douyin/webcast-id.py#multi-webcast-id-snippet{15,18}

::: tip 如何分辨Rid与room_id
Rid是直播间的短链标识，room_id是直播间的唯一标识。
如`https://live.douyin.com/775841227732`中的775841227732就是Rid，而`https://webcast.amemv.com/douyin/webcast/reflow/7318296342189919011`中的7318296342189919011就是room_id。
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
该接口很好的解决了用户改名之后重复重新下载的问题。集合在hanlder接口的`get_or_add_user_data`中，开发者无需关心直接调用hanlder的数据接口即可。
:::


### 显示二维码 🟢

用于将url地址显示为二维码。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| qrcode_url | str | 二维码地址 |
| show_image | bool | 是否显示二维码图片 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| None | None | 无 |

<<< @/snippets/douyin/show-qrcode.py{4,5}

::: tip 提示
show_image (bool): 是否显示图像，True 表示显示，False 表示在控制台显示
:::

## crawler接口


## dl接口
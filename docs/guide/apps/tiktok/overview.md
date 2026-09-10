---
outline: [2,3]
---

# 接口列表

::: tip 注意
🟢代表已经实现，🟡代表正在实现或修改，🟤代表暂时不实现，🔵代表未来可能实现，🔴代表将会弃用。
:::

::: details handler接口列表

|     CLI接口            |         方法        |
| :------------------ | :-------------------  |
| 下载单个作品          | `handle_one_video`      |
| 下载用户发布作品       | `handle_user_post`      |
| 下载用户喜欢作品       | `handle_user_like`      |
| 下载用户收藏作品       | `handle_user_collect`   |
| 下载用户合集(播放列表)作品 | `handle_user_mix`    |
| 下载搜索作品          | `handle_search_video`    |
| 下载用户直播流         | `handle_user_live`      |

|     数据与功能接口     |         方法           | 开发者接口  |
| :------------------ | :-------------------  | :--------: |
| 用户信息              | `fetch_user_profile`    |     🟢      |
| 创建用户记录与目录      | `get_or_add_user_data`   |     🟢      |
| 创建作品下载记录        | `get_or_add_video_data`  |     🟢      |
| 单个作品数据          | `fetch_one_video`        |     🟢      |
| 用户发布作品数据       | `fetch_user_post_videos` |     🟢      |
| 用户喜欢作品数据       | `fetch_user_like_videos` |     🟢      |
| 用户收藏作品数据       | `fetch_user_collect_videos` |  🟢      |
| 用户播放列表数据       | `fetch_play_list`        |     🟢      |
| 用户合集(播放列表)作品数据 | `fetch_user_mix_videos`  |    🟢     |
| 搜索作品数据          | `fetch_search_videos`     |     🟢      |
| 用户直播流数据         | `fetch_user_live_videos`  |     🟢      |
| 检查直播流状态         | `fetch_check_live_alive`  |     🟢      |
:::

::: details utils接口列表

| 开发者接口          | 类名            | 方法                 | 状态 |
| :---------------- | :-------------- | :------------------ | :--: |
| 管理客户端配置     | `ClientConfManager`   |                  |  🟢  |
| 生成真实msToken    | `TokenManager`     | `gen_real_msToken`   |  🟢  |
| 获取缓存的真实msToken | `TokenManager`  | `cached_msToken`     |  🟢  |
| 生成虚假msToken     | `TokenManager`     | `gen_false_msToken`  |  🟢  |
| 生成ttwid          | `TokenManager`     | `gen_ttwid`          |  🟢  |
| 生成odin_tt        | `TokenManager`      | `gen_odin_tt`        |  🟢  |
| 使用接口地址生成Xb参数 | `XBogusManager`    | `str_2_endpoint`    |  🟢  |
| 使用接口模型生成Xb参数 | `XBogusManager`    | `model_2_endpoint`   |  🟢  |
| 提取单个用户id       | `SecUserIdFetcher` | `get_secuid`         |  🟢  |
| 提取列表用户id       | `SecUserIdFetcher` | `get_all_secuid`     |  🟢  |
| 提取单个用户唯一id    | `SecUserIdFetcher` | `get_uniqueid`        |  🟢  |
| 提取列表用户唯一id    | `SecUserIdFetcher` | `get_all_uniqueid`    |  🟢  |
| 提取列表用户id       | `SecUserIdFetcher` | `get_all_secUid`   |  🟢  |
| 提取单个作品id       | `AwemeIdFetcher`   | `get_aweme_id`          |  🟢  |
| 提取列表作品id       | `AwemeIdFetcher`   | `get_all_aweme_id`      |  🟢  |
| 生成deviceId       | `DeviceIdManager`  | `gen_device_id`        |  🟢  |
| 生成devideId列表   | `DeviceIdManager`  | `gen_device_ids`   |  🟢  |
| 全局格式化文件名      | -                | `format_file_name`      |  🟢  |
| 创建用户目录         | -                | `create_user_folder`    |  🟢  |
| 重命名用户目录       | -                | `rename_user_folder`     |  🟢  |
| 创建或重命名用户目录  | -                | `create_or_rename_user_folder` |   🟢   |
:::

::: details crawler接口列表

| 爬虫url接口    | 类名           | 方法          | 状态 |
| :-----------  | :---------    | :----------  | :--: |
| 用户信息接口地址 | `TiktokCrawler` | `fetch_user_profile` |  🟢  |
| 主页作品接口地址 | `TiktokCrawler` | `fetch_user_post` |  🟢  |
| 喜欢作品接口地址 | `TiktokCrawler` | `fetch_user_like` |  🟢  |
| 收藏作品接口地址 | `TiktokCrawler` | `fetch_user_collect` |  🟢  |
| 合集列表接口地址 | `TiktokCrawler` | `fetch_user_play_list` |  🟢  |
| 合集作品接口地址 | `TiktokCrawler` | `fetch_user_mix` |  🟢  |
| 作品详情接口地址 | `TiktokCrawler` | `fetch_post_detail` |  🟢  |
| 作品评论接口地址 | `TiktokCrawler` | `fetch_post_comment` |  🟢  |
| 首页推荐作品接口地址 | `TiktokCrawler` | `fetch_post_feed` |  🟢  |
| 搜索作品接口地址 | `TiktokCrawler` | `fetch_post_search` |  🟢  |
| 用户直播接口地址 | `TiktokCrawler` | `fetch_user_live` |  🟢  |
| 检测直播状态接口地址 | `TiktokCrawler` | `fetch_check_live_alive` |  🟢  |
:::

::: details dl接口列表

| 下载器接口    | 类名           | 方法          | 状态 |
| :-----------  | :---------    | :----------  | :--: |
| 保存最后请求的作品ID | `TiktokDownloader` | `save_last_aweme_id` |  🟢  |
| 筛选指定时间区间的作品 | `TiktokDownloader` | `filter_aweme_datas_by_interval` |  🟢  |
| 创建下载任务   | `TiktokDownloader` | `create_download_task` |  🟢  |
| 处理下载任务   | `TiktokDownloader` | `handle_download` |  🟢  |
| 创建流下载任务  | `TiktokDownloader` | `create_stream_tasks` |  🟢  |
| 处理流下载任务  | `TiktokDownloader` | `handle_stream` |  🟢  |
:::

::: tip :bulb: 提示
- 翻页参数都包含在上一次请求的数据中，通过内置的 `filter` 过滤器可以很方便的获取。
- 所有包含翻页参数的接口均使用异步生成器方法，需要通过 `async for` 进行迭代，便于自动处理翻页。
- 当 `max_counts` 设置为 `None` 或不传入时，将会获取所有的作品数据。
- 在一些后端框架 `FastAPI`、`Flask`、`Django` 中可以方便的集成等。
- 使用登录的 `cookie` 可以无视该账号的私密设置，例如该账号设置私密的 `作品`、`主页`、`喜欢`、`收藏` 等。
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

<<< @/snippets/tiktok/one-video.py{15}

### 用户发布作品数据 🟢

异步方法，用于获取用户发布的视频列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid| str | 用户ID |
| cursor| int | 页码，初始为 `0` |
| page_counts| int | 页数，初始为 `20` |
| max_counts| int | 最大页数，初始为 `None` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/tiktok/user-post.py{18,20-22}

### 用户喜欢作品数据 🟢

异步方法，用于获取指定用户点赞的视频列表，需开放喜欢列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid| str | 用户ID |
| cursor| int | 页码，初始为 `0` |
| page_counts| int | 页数，初始为 `20` |
| max_counts| int | 最大页数，初始为 `None` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/tiktok/user-like.py{17-19,21-23}

### 用户收藏作品数据 🟢

异步方法，用于获取指定用户收藏的视频列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid    | str | 用户ID |
| cursor| int | 页码，初始为 `0` |
| page_counts| int | 页数，初始为 `20` |
| max_counts| int | 最大页数，初始为 `None` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/tiktok/user-collect.py{17-19,21-23}

### 用户播放列表作品数据 🟢

异步方法，用于获取指定用户播放列表的作品列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid| str | 合集ID |
| cursor| int | 页码，初始为 `0` |
| page_counts| int | 页数，初始为 `20` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/tiktok/user-playlist.py{17-18}

### 用户合集作品数据 🟢

异步方法，用于获取指定用户合集的视频列表，合集视频的 `mix_id` 是一致的，从单个作品数据接口中获取即可。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| mixId| str | 合集ID |
| cursor| int | 页码，初始为 `0` |
| page_counts| int | 页数，初始为 `20` |
| max_counts| int | 最大页数，初始为 `None` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/tiktok/user-mix.py#playlist-sinppet{18-19,21-22}

::: tip 注意
多个播放列表会包含多个 `mix_id`，使用 `select_playlist` 方法来返回用户输入的合集下标。
:::

<<< @/snippets/tiktok/user-mix.py#select-playlist-sinppet{19-22}

### 用户信息 🟢

异步方法，用于获取指定用户的信息，不可以直接解析 `Filter` 的数据，需要使用自定义的`_to_dict` 或 `_to_list` 方法。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid| str | 用户ID |
| uniqueId| str | 用户ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserProfileFilter | model | 自定义的接口数据过滤器 | 用户数据字典，包含用户ID、用户昵称、用户签名、用户头像等 |

<<< @/snippets/tiktok/user-profile.py{16-20,26}

::: tip :bulb: 提示
`TikTok` 的用户接口支持 `secUid` 和 `uniqueId` 两种用户ID。
:::

### 创建用户记录与目录 🟢

异步方法，用于获取或创建用户数据同时创建用户目录。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| kwargs | dict | `cli` 字典数据，需获取 `path` 参数 |
| secUid| str | 用户ID |
| db | AsyncUserDB | 用户数据库 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_path | Path | 用户目录路径对象 |

<<< @/snippets/tiktok/user-get-add.py{17-23}

::: tip :bulb: 提示
此为 `cli` 模式的接口，开发者可自行定义创建用户目录的功能。
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
|无 | 无 | 无 |

<<< @/snippets/tiktok/video-get-add.py{6,7,23-26}

## utils接口列表

### 管理客户端配置 🟢

类方法，用于管理客户端配置

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| 配置文件值 | Any | 配置文件值 |

<<< @/snippets/tiktok/client-config.py{4,5,7,8,10,11}

### 生成真实msToken 🟢

类方法，用于生成真实的 `msToken`，当出现错误时返回虚假的值。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| msToken | str | 真实的msToken |

<<< @/snippets/tiktok/token-manager.py#mstoken-real-sinppest{4}

### 获取缓存的真实msToken 🟢

类方法，返回进程内缓存的真实 `msToken`，首次调用时才联网生成。请求模型的 `msToken` 字段默认通过它在实例化时获取，因此导入模块不会联网。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| msToken | str | 缓存的真实msToken |

<<< @/snippets/tiktok/token-manager.py#mstoken-cached-sinppest{4}

### 生成虚假msToken 🟢

类方法，用于生成随机虚假的 `msToken`，不同端点的 `msToken` 长度不同。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| msToken | str | 虚假的msToken |

<<< @/snippets/tiktok/token-manager.py#mstoken-false-sinppest{4}

::: tip :bulb: 提示
默认为 `126位`，也可调用 `from from f2.utils.string.generator import gen_random_str`，生成不同长度的虚假msToken。
:::

### 生成ttwid 🟢

类方法，用于生成ttwid，部分请求必带。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| ttwid | str | ttwid参数 |

<<< @/snippets/tiktok/token-manager.py#ttwid-sinppest{4}

::: warning :warning: 注意
配置文件中 `ttwid` 的 `cookie` 参数是一个新的 `ttwid` 值。失效后更换新的 `ttwid` 值即可。
:::

### 生成odin_tt 🟢

类方法，用于生成odin_tt，部分请求必带。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| odin_tt | str | odin_tt参数 |

<<< @/snippets/tiktok/token-manager.py#odin_tt-sinppest{4}

::: warning :warning: 注意
配置文件中的`odin_tt`参数是固定的，不可更改。
:::

### 使用接口地址生成Xb参数 🟢

类方法，用于直接使用接口地址生成`Xbogus`参数，部分接口不校验。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| endpoint | str | 接口端点 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_endpoint | str | 带Xbogus参数的完整地址 |

<<< @/snippets/tiktok/xbogus.py#str-2-endpoint-snippet{8}

### 使用接口模型生成Xb参数 🟢

类方法，用于使用不同接口数据模型生成`Xbogus`参数，部分接口不校验。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| endpoint | str | 端点 |
| params | dict | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_endpoint | str | 带Xbogus参数的完整地址 |

使用模型生成接口地址，需要先创建一个模型对象，然后调用 `model_2_endpoint` 方法。

<<< @/snippets/tiktok/xbogus.py#model-2-endpoint-snippet{9,16}

还可以使用爬虫引擎与过滤器采集数据。

<<< @/snippets/tiktok/xbogus.py#model-2-endpoint-2-filter-snippet{22,24}

更加抽象的高级方法可以直接调用 `handler` 接口的 `fetch_user_profile`。

### 提取单个用户id 🟢

类方法，用于提取单个用户id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 用户主页地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| sec_uid | str | 用户ID |

<<< @/snippets/tiktok/sec-uid.py#single-secuid-snippet{8}

### 提取列表用户id 🟢

类方法，用于提取列表用户id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 用户主页地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| secuids | list | 用户ID列表 |

<<< @/snippets/tiktok/sec-uid.py#multi-secuid-snippet{14,17}

### 提取单个用户唯一id 🟢

类方法，用于提取单个用户唯一id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 用户主页地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| unique_id | str | 用户唯一ID |

<<< @/snippets/tiktok/unique-id.py#single-unique-id-snippet{8}

### 提取列表用户唯一id 🟢

类方法，用于提取列表用户唯一id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 用户主页地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| unique_ids | list | 用户唯一ID列表 |

<<< @/snippets/tiktok/unique-id.py#multi-unique-id-snippet{14,17}

### 提取单个作品id 🟢

类方法，用于提取单个作品id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 作品地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_id | str | 作品ID |

<<< @/snippets/tiktok/aweme-id.py#single-aweme-id-snippet{8}

### 提取列表作品id 🟢

类方法，用于提取列表作品id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 作品地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_ids | list | 作品ID列表 |

<<< @/snippets/tiktok/aweme-id.py#multi-aweme-id-snippet{14,17}

::: tip :bulb: 提示
从网页复制的链接和app分享的链接都是有效的。
:::

### 生成deviceId 🟢

类方法，用于生成 `deviceId` 和 `tt_chain_token`。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| full_cookie | bool | 是否返回完整的 `cookie` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| device_id | dict | 设备ID和 `cookie` 的字典 |

<<< @/snippets/tiktok/device-id.py#device-id-snippet{6,8}

### 生成devideId列表 🟢

类方法，用于生成多个`deviceId`和`tt_chain_token`。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| count | int | 设备ID数量 |
| full_cookie | bool | 是否返回完整的 `cookie` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| device_ids | dict | 设备ID和 `cookie` 的列表字典 |

<<< @/snippets/tiktok/device-id.py#device-ids-snippet{6,8}

::: tip :bulb: 提示
`deviceId` 和 `tt_chain_token`参数绑定配置文件，也影响视频地址的访问，`403` 的情况就是这个问题。
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

<<< @/snippets/tiktok/format-file-name.py{12,20,25,29,31-34}

### 创建用户目录 🟢

用于创建用户目录，如果目录已存在则不创建。

::: details :open_file_folder: 用户目录结构
如果未在配置文件中指定路径，则默认为 `Download`。支持绝对与相对路径。
```bash
├── Download
│   ├── tiktok
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
| kwargs | dict | `cli` 配置文件 |
| nickname | Union[str, int] | 用户昵称 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_path | Path | 用户目录路径对象 |

<<< @/snippets/tiktok/user-folder.py#create-user-folder{17-19}

### 重命名用户目录 🟢

用于重命名用户目录。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| old_path | Path | 旧的用户目录路径对象 |
| new_nickname | str | 新的用户昵称 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| new_path | Path | 新的用户目录路径对象 |

<<< @/snippets/tiktok/user-folder.py#rename-user-folder{20-24,26-29}

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
该接口很好的解决了用户改名之后重复重新下载的问题。集合在handler接口的`get_or_add_user_data`中，开发者无需关心直接调用handler的数据接口即可。
:::

## crawler接口

### 用户信息接口地址 🟢

用于获取用户信息的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserProfile | model | 用户信息接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取用户信息的方法 |

### 主页作品接口地址 🟢

用于获取用户发布作品的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserPost | model | 用户发布作品接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取用户发布作品的方法 |

### 喜欢作品接口地址 🟢

用于获取用户喜欢作品的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserLike | model | 用户喜欢作品接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取用户喜欢作品的方法 |

### 收藏作品接口地址 🟢

用于获取用户收藏作品的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserCollect | model | 用户收藏作品接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取用户收藏作品的方法 |

### 合集列表接口地址 🟢

用于获取用户播放列表的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserPlayList | model | 用户播放列表接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取用户播放列表的方法 |

### 合集作品接口地址 🟢

用于获取用户合集作品的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserMix | model | 用户合集作品接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取用户合集作品的方法 |

### 作品详情接口地址 🟢

用于获取作品详情的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| PostDetail | model | 作品详情接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取作品详情的方法 |

### 作品评论接口地址 🟢

用于获取作品评论的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| PostComment | model | 作品评论接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取作品评论的方法 |

### 首页推荐作品接口地址 🟢

用于获取首页推荐作品的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| PostDetail | model | 首页推荐作品接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取首页推荐作品的方法 |

### 搜索作品接口地址 🟢

用于获取搜索作品的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| PostSearch | model | 搜索作品接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取搜索作品的方法 |

### 用户直播接口地址 🟢

用于获取用户直播的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserLive | model | 用户直播接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 获取用户直播的方法 |

### 检测直播状态接口地址 🟢

用于检测用户直播状态的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| CheckLiveAlive | model | 检测直播状态接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 检测直播状态的方法 |

### 直播弹幕初始化接口地址 🟢

用于获取直播弹幕初始化的接口地址。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| LiveImFetch | model | 直播弹幕初始化接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| payload_package | dict | 直播弹幕初始化的数据包 |

::: tip :bulb: 提示
- 当不需要使用过滤器时，可以直接调用`crawler`接口，将直接返回数据字典。
:::

## dl接口

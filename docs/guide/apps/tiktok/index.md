---
outline: deep
---

# 接口列表

::: tip 注意
🟢代表已经实现，🟡代表正在实现或修改，🟤代表暂时不实现，🔵代表未来可能实现，🔴代表将会弃用。
:::

::: details handler接口列表

|     CLI接口            |         方法        |
| :------------------ | :-------------------  |
| 下载单个作品          | handle_one_video      |
| 下载用户发布作品       | handle_user_post      |
| 下载用户喜欢作品       | handle_user_like      |
| 下载用户收藏作品       | handle_user_collect   |
| 下载用户合辑(播放列表)作品 | handle_user_mix    |
| 下载用户直播流         | handle_user_live      |
| 下载用户首页推荐作品    | handle_user_feed      |

|     数据与功能接口     |         方法           | 开发者接口  |
| :------------------ | :-------------------  | :--------: |
| 单个作品数据          | fetch_one_video        |     🟢      |
| 用户发布作品数据       | fetch_user_post_videos |     🟢      |
| 用户喜欢作品数据       | fetch_user_like_videos |     🟢      |
| 用户收藏作品数据       | fetch_user_collect_videos |  🟢      |
| 用户播放列表作品数据    | fetch_play_list        |     🟢      |
| 用户合辑(播放列表)作品  | fetch_user_mix_videos  |     🟢      |
| ......               | ......                 |    🔵      |
| 用户信息              | handler_user_profile   |     🟢      |
| 获取指定用户名         | get_user_nickname      |      🔴     |
| 创建用户记录与目录      | get_or_add_user_data   |     🟡      |
| 创建作品下载记录        | get_or_add_video_data  |     🟢      |
:::

::: details utils接口列表

| 开发者接口          | 类名            | 方法                 | 状态 |
| :---------------- | :-------------- | :------------------ | :--: |
| 生成真实msToken    | TokenManager     | gen_real_msToken   |  🟢  |
| 生成虚假msToken     | TokenManager     | gen_false_msToken  |  🟢  |
| 生成ttwid          | TokenManager     | gen_ttwid          |  🟢  |
| 生成odin_tt        | TokenManager      | gen_odin_tt        |  🟢  |
| 使用接口地址生成Xb参数 | XBogusManager    | str_2_endpoint    |  🟢  |
| 使用接口模型生成Xb参数 | XBogusManager    | model_2_endpoint   |  🟢  |
| 提取单个用户id       | SecUserIdFetcher | get_secuid         |  🟢  |
| 提取列表用户id       | SecUserIdFetcher | get_all_secuid     |  🟢  |
| 提取单个用户唯一id    | SecUserIdFetcher | get_uniqueid        |  🟢  |
| 提取列表用户唯一id    | SecUserIdFetcher | get_all_uniqueid    |  🟢  |
| 提取列表用户id       | SecUserIdFetcher | get_all_secUid   |  🟢  |
| 提取单个作品id       | AwemeIdFetcher   | get_aweme_id          |  🟢  |
| 提取列表作品id       | AwemeIdFetcher   | get_all_aweme_id      |  🟢  |
| 提取合辑id          | MixIdFetcher     | -                     |  🟤  |
| 全局格式化文件名      | -                | format_file_name      |  🟢  |
| 创建用户目录         | -                | create_user_folder    |  🟢  |
| 重命名用户目录       | -                | rename_user_folder     |  🟢  |
| 创建或重命名用户目录  | -                | create_or_rename_user_folder |   🟢   |

::: details crawler接口列表

| 爬虫url接口    | 类名           | 方法          | 状态 |
| :-----------  | :---------    | :----------  | :--: |
| 用户信息接口地址 | TiktokCrawler | fetch_user_profile |  🟢  |
| 主页作品接口地址 | TiktokCrawler | fetch_user_post |  🟢  |
| 喜欢作品接口地址 | TiktokCrawler | fetch_user_like |  🟢  |
| 收藏作品接口地址 | TiktokCrawler | fetch_user_collect |  🟢  |
| 合辑列表接口地址 | TiktokCrawler | fetch_user_play_list |  🟢  |
| 合辑作品接口地址 | TiktokCrawler | fetch_user_mix |  🟢  |
| 作品详情接口地址 | TiktokCrawler | fetch_post_detail |  🟢  |
| 作品评论接口地址 | TiktokCrawler | fetch_post_comment |  🟡  |
| 推荐作品接口地址 | TiktokCrawler | fetch_post_feed |  🟡  |
:::

::: details dl接口列表

| 下载器接口    | 类名           | 方法          | 状态 |
| :-----------  | :---------    | :----------  | :--: |
| 保存最后一次请求的aweme_id | TiktokDownloader | save_last_aweme_id |  🟢  |
| 创建下载任务   | TiktokDownloader | create_download_task |  🟢  |
| 处理下载任务   | TiktokDownloader | handle_download |  🟢  |
| 创建流下载任务  | TiktokDownloader | create_stream_tasks |  🟢  |
| 处理流下载任务  | TiktokDownloader | handle_stream |  🟢  |
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

<<< @/snippets/tiktok/one-video.py{15,17}

### 用户发布作品数据 🟢

异步方法，用于获取用户发布的视频列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid| str | 用户ID |
| cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/tiktok/user-post.py{16,19-22}

### 用户喜欢作品数据 🟢

异步方法，用于获取指定用户点赞的视频列表，需开放喜欢列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid| str | 用户ID |
| cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/tiktok/user-like.py{16-18,21-25}

### 用户收藏作品数据 🟢

异步方法，用于获取指定用户收藏的视频列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid    | str | 用户ID |
| cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/tiktok/user-collect.py{16-18,21-24}

### 用户播放列表作品数据 🟢

异步方法，用于获取指定用户播放列表的作品列表。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid| str | 合集ID |
| cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/tiktok/user-playlist.py{16-17,21}

### 用户合辑作品数据 🟢

异步方法，用于获取指定用户合辑的视频列表，合辑视频的mix_id是一致的，从单个作品数据接口中获取即可。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| mixId| str | 合集ID |
| cursor| int | 页码，初始为0 |
| page_counts| int | 页数，初始为20 |
| max_counts| int | 最大页数，初始为None |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_data | dict | 视频数据字典，包含视频ID、视频文案、作者昵称、页码等 |

<<< @/snippets/tiktok/user-mix.py#playlist-sinppet{17-18,21-23}

::: tip 注意
多个播放列表会包含多个`mix_id`，使用`select_playlist`方法来返回用户输入的合辑下标。
:::

<<< @/snippets/tiktok/user-mix.py#select-playlist-sinppet{19-21}

### 用户信息 🟢

异步方法，用于获取指定用户的信息，不可以直接解析Filter的数据，需要使用自定义的_to_dict()或_to_list()方法。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid| str | 用户ID |
| uniqueId| str | 用户ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserProfileFilter | _to_dict() | 自定义的接口数据过滤器 | 用户数据字典，包含用户ID、用户昵称、用户签名、用户头像等 |

<<< @/snippets/tiktok/user-profile.py{16,18-19,21}

::: tip 提示
TikTok的用户接口支持`secUid`和`uniqueId`两种用户ID。
:::

### 获取指定用户名 🔴

异步方法，用于获取指定用户的昵称，如果不存在，则从服务器获取并存储到数据库中。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| secUid| str | 用户ID |
| db | AsyncUserDB | 用户数据库 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_nickname | str | 用户昵称 |

<<< @/snippets/tiktok/user-nickname.py{17-20}

### 创建用户记录与目录 🟡

异步方法，用于获取或创建用户数据同时创建用户目录。


| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| kwargs | dict | cli字典数据，需获取path参数 |
| secUid| str | 用户ID |
| db | AsyncUserDB | 用户数据库 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_path | Path | 用户目录路径对象 |

<<< @/snippets/tiktok/user-get-add.py{18-22}

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

<<< @/snippets/tiktok/video-get-add.py{6,23-25}

## utils接口列表

### 生成真实msToken 🟢

静态方法，用于生成真实的msToken，当出现错误时返回虚假的值。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| msToken | str | 真实的msToken |

<<< @/snippets/tiktok/token-manager.py#mstoken-real-sinppest{4}

### 生成虚假msToken 🟢

静态方法，用于生成随机虚假的msToken，不同端点的msToken长度不同。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| msToken | str | 虚假的msToken |

<<< @/snippets/tiktok/token-manager.py#mstoken-false-sinppest{4}

::: tip 提示
默认为`126位`，也可调用`from f2.utils.utils import gen_random_str`，生成不同长度的虚假msToken。
:::

### 生成ttwid 🟢

静态方法，用于生成ttwid，部分请求必带。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| ttwid | str | ttwid参数 |

<<< @/snippets/tiktok/token-manager.py#ttwid-sinppest{4}

::: warning 注意
配置文件中`ttwid`的`cookie`参数是一个新的`ttwid`值。失效后更换新的`ttwid`值即可。
:::

### 生成odin_tt 🟢

静态方法，用于生成odin_tt，部分请求必带。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| None | None | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| odin_tt | str | odin_tt参数 |

<<< @/snippets/tiktok/token-manager.py#odin_tt-sinppest{4}

::: warning 注意
配置文件中的`odin_tt`参数是固定的，不可更改。
:::

### 使用接口地址生成Xb参数 🟢

静态方法，用于直接使用接口地址生成`Xbogus`参数，部分接口不校验。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| endpoint | str | 接口端点 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_endpoint | str | 带Xbogus参数的完整地址 |

<<< @/snippets/tiktok/xbogus.py#str-2-endpoint-snippet{7}

### 使用接口模型生成Xb参数 🟢

静态方法，用于使用不同接口数据模型生成`Xbogus`参数，部分接口不校验。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| endpoint | str | 端点 |
| params | dict | 请求参数 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| final_endpoint | str | 带Xbogus参数的完整地址 |

使用模型生成接口地址，需要先创建一个模型对象，然后调用`model_2_endpoint`方法。

<<< @/snippets/tiktok/xbogus.py#model-2-endpoint-snippet{8-10,13-15}

还可以使用爬虫引擎与过滤器采集数据。

<<< @/snippets/tiktok/xbogus.py#model-2-endpoint-2-filter-snippet{21-26}

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
| sec_uid | str | 用户ID |

<<< @/snippets/tiktok/sec-uid.py#single-secuid-snippet{7}

### 提取列表用户id 🟢

静态方法，用于提取列表用户id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 用户主页地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| secuids | list | 用户ID列表 |

<<< @/snippets/tiktok/sec-uid.py#multi-secuid-snippet{13,16}

### 提取单个用户唯一id 🟢

静态方法，用于提取单个用户唯一id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 用户主页地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| unique_id | str | 用户唯一ID |

<<< @/snippets/tiktok/unique-id.py#single-unique-id-snippet{7}

### 提取列表用户唯一id 🟢

静态方法，用于提取列表用户唯一id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 用户主页地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| unique_ids | list | 用户唯一ID列表 |

<<< @/snippets/tiktok/unique-id.py#multi-unique-id-snippet{13,16}

### 提取单个作品id 🟢

静态方法，用于提取单个作品id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 作品地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_id | str | 作品ID |

<<< @/snippets/tiktok/aweme-id.py#single-aweme-id-snippet{7}

### 提取列表作品id 🟢

静态方法，用于提取列表作品id。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | list | 作品地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| aweme_ids | list | 作品ID列表 |

<<< @/snippets/tiktok/aweme-id.py#multi-aweme-id-snippet{14,17}

::: tip 提示
从网页复制的链接和app分享的链接都是有效的。
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

<<< @/snippets/tiktok/format-file-name.py{18,20,23,25,27-30}

### 创建用户目录 🟢

用于创建用户目录，如果目录已存在则不创建。

::: details 用户目录结构
如果未在配置文件中指定路径，则默认为 `Download`。支持绝对与相对路径。
```bash
├── Download
│   ├── tiktok
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

<<< @/snippets/tiktok/user-folder.py#rename-user-folder{22-24,26-29}

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

## crawler接口


## dl接口
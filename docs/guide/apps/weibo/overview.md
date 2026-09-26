---
outline: [2,3]
---

# 接口列表

::: tip 注意
🟢代表已经实现，🟡代表正在实现或修改，🟤代表暂时不实现，🔵代表未来可能实现，🔴代表将会弃用。
:::

::: details handler接口列表

|     CLI接口          |         方法         |
| :------------------ | :------------------- |
|  下载单个微博         | `handle_one_weibo`   |
|  下载用户微博         | `handle_user_weibo`  |

|     数据方法接口      |         方法           | 开发者接口   |
| :------------------ | :-------------------  | :--------: |
| 创建用户记录与目录      | `get_or_add_user_data`|     🟢    |
| 获取用户信息(uid)      | `fetch_user_info`     |     🟢      |
| 获取用户信息(昵称)     | `fetch_user_info_by_screen_name` |     🟢      |
| 获取用户详情           | `fetch_user_detail`     |     🟢      |
| 提取微博用户id         | `extract_weibo_uid`     |     🟢      |
| 单个微博数据          | `fetch_one_weibo`        |     🟢      |
| 用户微博数据          | `fetch_user_weibo`       |     🟢      |
:::

::: details utils接口列表

| 工具类接口          | 类名                      | 方法                           | 状态 |
| :------------------ | :------------------------ | :---------------------------- | :--: |
| 管理客户端配置       | `ClientConfManager`       |                               |  🟢  |
| 生成访客 Cookie      | `VisitorManager`          | `gen_visitor`                 |  🟢  |
| 提取微博 ID          | `WeiboIdFetcher`          | `get_weibo_id`                |  🟢  |
| 提取列表微博 ID      | `WeiboIdFetcher`          | `get_all_weibo_id`            |  🟢  |
| 提取微博用户 ID      | `WeiboUidFetcher`         | `get_weibo_uid`               |  🟢  |
| 提取列表微博用户 ID  | `WeiboUidFetcher`         | `get_all_weibo_uid`           |  🟢  |
| 提取微博用户昵称     | `WeiboScreenNameFetcher`  | `get_weibo_screen_name`       |  🟢  |
| 提取列表微博用户昵称 | `WeiboScreenNameFetcher`  | `get_all_weibo_screen_name`   |  🟢  |
| 全局格式化文件名     | -                         | `format_file_name`            |  🟢  |
| 创建用户目录         | -                         | `create_user_folder`          |  🟢  |
| 重命名用户目录       | -                         | `rename_user_folder`          |  🟢  |
| 创建或重命名用户目录 | -                         | `create_or_rename_user_folder`|  🟢  |
| 提取微博文案         | -                         | `extract_desc`                |  🟢  |
:::

::: details crawler接口列表

| 爬虫url接口    | 类名       | 方法          | 状态 |
| :----------- | :--------- | :----------  | :----: |
| 用户信息接口 | `WeiboCrawler` | `fetch_user_info` | 🟢 |
| 用户详情接口 | `WeiboCrawler` | `fetch_user_detail` | 🟢 |
| 用户微博接口 | `WeiboCrawler` | `fetch_user_weibo` | 🟢 |
| 单条微博接口 | `WeiboCrawler` | `fetch_weibo_detail` | 🟢 |
:::

::: details dl接口列表
| 下载器接口     | 类名        | 方法          | 状态 |
| :----------- | :--------- | :----------  | :--: |
| 创建下载任务   | `WeiboDownloader` | `create_download_task` |  🟢  |
| 处理下载任务   | `WeiboDownloader` | `handler_download` |  🟢  |
| 下载文案      | `WeiboDownloader` | `download_desc`    |  🟢  |
| 下载视频      | `WeiboDownloader` | `download_video`   |  🟢  |
| 下载图集      | `WeiboDownloader` | `download_images`  |  🟢  |
:::

::: tip :bulb: 提示
- 翻页参数都包含在上一次请求的数据中，通过内置的 `filter` 过滤器可以很方便的获取。
- 所有包含翻页参数的接口均使用异步生成器方法，需要通过 `async for` 进行迭代，便于自动处理翻页。
- 当 `max_counts` 设置为 `None` 或不传入时，将会获取所有的微博数据。
- 在一些后端框架 `FastAPI`、`Flask`、`Django` 中可以方便的集成等。
- 使用登录的 `cookie` 可以无视该账号的私密设置。
:::

## handler接口列表

### 创建用户记录与目录 🟢

异步方法，用于获取或创建用户数据同时创建用户目录。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| kwargs | dict | cli字典数据，需获取path参数 |
| user_id| str | 用户ID |
| db | AsyncUserDB | 用户数据库 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_path | Path | 用户目录路径对象 |

<<< @/snippets/weibo/user-get-add.py{14,15,23-25}

::: tip :bulb: 提示
- 此为 `cli` 模式的接口，开发者可自行定义创建用户目录的功能。
- 不设置 `mode` 参数时，默认为 `PLEASE_SETUP_MODE` 目录。
:::

### 获取用户信息(uid) 🟢

异步方法，用于获取指定用户的信息。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| uid | str | 用户ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserInfoFilter | JsonModel | 用户信息过滤器，包含用户信息的_to_raw、_to_dict方法 |

<<< @/snippets/weibo/user-profile.py{17}

### 获取用户信息(昵称) 🟢

异步方法，通过用户昵称获取用户信息。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| screen_name | str | 用户昵称 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserInfoFilter | JsonModel | 用户信息过滤器，包含用户信息的_to_raw、_to_dict方法 |

<<< @/snippets/weibo/user-profile-by-name.py{17-19}

### 获取用户详情 🟢

异步方法，用于获取指定用户的详细信息。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| uid | str | 用户ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserDetailFilter | JsonModel | 用户详细信息过滤器，包含用户详细信息的_to_raw、_to_dict方法 |

<<< @/snippets/weibo/user-detail.py{17}

### 提取微博用户id 🟢

异步方法，用于从微博链接中提取并返回用户ID。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 微博链接 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| uid | str | 用户ID |

<<< @/snippets/weibo/extract-uid.py{15-17}

### 单个微博数据 🟢

异步方法，用于获取单条微博的数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| weibo_id | str | 微博ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| WeiboDetailFilter | JsonModel | 微博详细信息过滤器，包含微博详细信息的_to_raw、_to_dict方法 |

<<< @/snippets/weibo/one-weibo.py{17}

### 用户微博数据 🟢

异步方法，用于获取用户微博数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| uid | str | 用户ID |
| page | int | 页数 |
| feature | int | 微博类型 |
| since_id | str | 起始微博ID |
| max_counts | int | 最大微博数 |
| interval | tuple | 发布时间区间，秒级时间戳 `(开始, 结束)`，包含首尾，默认不限制 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserWeiboFilter | JsonModel | 用户微博信息过滤器，包含用户微博信息的_to_raw、_to_dict方法 |

<<< @/snippets/weibo/user-weibo.py{17-23}

## utils接口列表

### 管理客户端配置 🟢

类方法，用于管理客户端配置。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| 配置文件值 | Any | 配置文件值 |

<<< @/snippets/weibo/client-config.py{4,5,7,8,10,11}

### 生成访客 Cookie 🟢

类方法，用于生成访客 Cookie。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| visitor_cookie | str | 访客 Cookie |

<<< @/snippets/weibo/visitor-cookie.py{7}

### 提取微博 ID 🟢

类方法，从微博链接中提取微博ID。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 微博链接 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| weibo_id | str | 微博ID |

<<< @/snippets/weibo/weibo-id.py#single-weibo-id-snippet{8}

### 提取列表微博 ID 🟢

类方法，从微博链接列表中提取微博ID。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | List[str] | 微博链接列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| weibo_ids | List[str] | 微博ID列表 |

<<< @/snippets/weibo/weibo-id.py#multi-weibo-id-snippet{19,22}

### 提取微博用户 ID 🟢

类方法，从微博链接中提取用户ID。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 微博主页链接 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| uid | str | 用户ID |

<<< @/snippets/weibo/weibo-uid.py#single-weibo-uid-snippet{8}

::: tip :grey_exclamation: 提示
- 使数据接口方法里的 `extract_weibo_uid` 方法可以更全面的处理微博链接，该方法仅适用与非昵称链接的提取。
:::

### 提取列表微博用户 ID 🟢

类方法，从微博链接列表中提取用户ID。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | List[str] | 微博主页链接列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| uids | List[str] | 用户ID列表 |

<<< @/snippets/weibo/weibo-uid.py#multi-weibo-uid-snippet{27,30}

### 提取微博用户昵称 🟢

类方法，从微博链接中提取用户昵称。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 微博主页链接 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| screen_name | str | 用户昵称 |

<<< @/snippets/weibo/weibo-screen-name.py#single-weibo-screen_name-snippet{8}

### 提取列表微博用户昵称 🟢

类方法，从微博链接列表中提取用户昵称。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | List[str] | 微博主页链接列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| screen_names | List[str] | 用户昵称列表 |

<<< @/snippets/weibo/weibo-screen-name.py#multi-weibo-screen_name-snippet{20,23}

::: tip :information_source: 提示
`F2` 会自动处理编码，无需担心中文字符转义问题。
:::

### 全局格式化文件名 🟢

根据配置文件的全局格式化文件名。
::: details :page_facing_up: 格式化文件名规则
- 文案（`desc`）超过 `200` 字节时截断中间部分，用 `......` 连接。
- 下载时整个文件名连同后缀不超过 `255` 字节，超出时同样截断中间部分。这是 `ext4` 与多数 `NAS` 文件系统的上限，`NTFS`、`APFS` 按字符计算，不会超出。
- `Windows` 下路径超过 `260` 个字符时自动改用扩展长度路径（`\\?\`），不需要开启系统的长路径支持。
- 开发者可以根据自己的需求自定义 `custom_fields` 字段，实现自定义文件名。
:::

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| naming_template | str | 文件的命名模板 |
| weibo_data | dict | 作品数据的字典 |
| custom_fields | dict | 用户自定义字段, 用于替代默认的字段值 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| file_name | str | 格式化后的文件名 |

<<< @/snippets/weibo/format-file-name.py{13,19,24,28,30-33}

### 创建用户目录 🟢

用于创建用户目录，如果目录已存在则不创建。

::: details :open_file_folder: 用户目录结构
如果未在配置文件中指定路径，则默认为 `Download`。支持绝对与相对路径。
```bash
├── Download
│   ├── weibo
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

<<< @/snippets/weibo/user-folder.py#create-user-folder{17,18}

### 重命名用户目录 🟢

用于重命名用户目录。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| old_path | Path | 旧的用户目录路径对象 |
| new_nickname | str | 新的用户昵称 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| new_path | Path | 新的用户目录路径对象 |

<<< @/snippets/weibo/user-folder.py#rename-user-folder{20-24,28,29}

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

::: tip :information_source: 提示
该接口很好的解决了用户改名之后重复创建目录的问题。集成在 `handler` 接口中。开发者无需关心，直接调用 `handler` 的数据接口即可。
:::

### 提取微博文案 🟢

用于提取微博文案，排除最后的链接。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| text | str | 微博文案 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| text | str | 提取后的微博文案 |

<<< @/snippets/weibo/extract-desc.py{18}

## crawler接口列表

### 用户信息接口 🟢

用于获取用户信息。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserInfo | 户信息接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 用户信息数据 |

### 用户详情接口 🟢

用于获取用户详情。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserDetail | 用户详情接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 用户详情数据 |

### 用户微博接口 🟢

用于获取用户微博。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | UserWeibo | 用户微博接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 用户微博数据 |

### 单条微博接口 🟢

用于获取单条微博。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| params | WeiboDetail | 单条微博接口模型 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 单条微博数据 |

## dl接口列表

### 创建下载任务 🟢


### 处理下载任务 🟢


### 下载文案 🟢


### 下载视频🟢


### 下载图集 🟢

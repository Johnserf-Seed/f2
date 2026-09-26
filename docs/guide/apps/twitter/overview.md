---
outline: [2,3]
---

# 接口列表

::: tip 注意
🟢代表已经实现，🟡代表正在实现或修改，🟤代表暂时不实现，🔵代表未来可能实现，🔴代表将会弃用。
:::

::: details handler接口列表

|     CLI接口          |         方法           |
| :------------------ | :-------------------   |
| 下载单个推文           |`handle_one_tweet`     |
| 下载主页推文           |`handle_post_tweet`    |
| 下载喜欢推文           |`handle_like_tweet`    |
| 下载收藏推文           |`handle_bookmark_tweet`|

|     数据方法接口      |         方法            | 开发者接口   |
| :------------------ | :-------------------   | :--------: |
| 创建用户记录与目录      | `get_or_add_user_data`   |    🟢   |
| 获取用户信息           | `fetch_user_profile`     |    🟢   |
| 单个推文数据           | `fetch_one_tweet`        |    🟢   |
| 主页推文数据           | `fetch_post_tweet`       |    🟢   |
| 喜欢推文数据           | `fetch_like_tweet`       |    🟢   |
| 收藏推文数据           | `fetch_bookmark_tweet`   |    🟢   |
:::

::: details utils接口列表

|    工具类接口      |          类名         |              方法           | 状态 |
| :--------------- | :------------------- | :-------------------------- | :--: |
|  管理客户端配置     | `ClientConfManager`  |                            |  🟢  |
|  提取用户唯一ID        | `UniqueIdFetcher`      | `get_unique_id`              |  🟢  |
|  提取列表用户唯一ID     | `UniqueIdFetcher`      | `get_all_unique_ids`         |  🟢  |
|  提取推文ID        | `TweetIdFetcher`     | `get_tweet_id`             |  🟢  |
|  提取列表推文ID     | `TweetIdFetcher`     | `get_all_tweet_ids`        |  🟢  |
|  全局格式化文件名    | -                   | `format_file_name`          |  🟢  |
|  创建用户目录       | -                   | `create_user_folder`        |  🟢  |
|  重命名用户目录      | -                 | `rename_user_folder`          |  🟢  |
|  创建或重命名用户目录 | -                 | `create_or_rename_user_folder` |  🟢  |
|  提取推文文案       | -                    | `extract_desc`              |  🟢  |
:::

::: details crawler接口列表

| 爬虫url接口    | 类名       | 方法          | 状态 |
| :----------- | :--------- | :----------  | :--: |
| 推文详情接口   | `TwitterCrawler` | `fetch_tweet_detail` |  🟢  |
| 用户信息接口   | `TwitterCrawler` | `fetch_user_profile` |  🟢  |
| 主页推文接口   | `TwitterCrawler` | `fetch_post_tweet`    |  🟢  |
| 喜欢推文接口   | `TwitterCrawler` | `fetch_like_tweet`    |  🟢  |
| 收藏推文接口   | `TwitterCrawler` | `fetch_bookmark_tweet`|  🟢  |
:::

::: details dl接口列表

| 下载器接口     | 类名        | 方法         |  状态 |
| :----------- | :--------- | :----------  | :--: |
| 创建下载任务   | `TwitterDownloader` | `create_download_task` |  🟢  |
| 处理下载任务   | `TwitterDownloader` | `handler_download` |  🟢  |
| 下载文案      | `TwitterDownloader` | `download_desc`    |  🟢  |
| 下载视频      | `TwitterDownloader` | `download_video`   |  🟢  |
| 下载图集      | `TwitterDownloader` | `download_images`  |  🟢  |
:::

::: tip :bulb: 提示
- 翻页参数都包含在上一次请求的数据中，通过内置的 `filter` 过滤器可以很方便的获取。
- 所有包含翻页参数的接口均使用异步生成器方法，需要通过 `async for` 进行迭代，便于自动处理翻页。
- 当 `max_counts` 设置为 `None` 或不传入时，将会获取所有的作品数据。
- 在一些后端框架 `FastAPI`、`Flask`、`Django` 中可以方便的集成等。
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

<<< @/snippets/twitter/user-get-add.py{13,14,19,22-24}

::: tip :bulb: 提示
- 此为 `cli` 模式的接口，开发者可自行定义创建用户目录的功能。
- 不设置 `mode` 参数时，默认为 `PLEASE_SETUP_MODE` 目录。
:::

### 获取用户信息 🟢

异步方法，用于获取用户的信息。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| uniqueId | str | 用户ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserProfileFilter | model | 用户数据过滤器，包含用户数据的_to_raw、_to_dict方法 |

<<< @/snippets/twitter/user-profile.py{18}

### 单个推文数据 🟢

异步方法，用于获取推文的数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| tweet_id | str | 推文ID |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| TweetDetailFilter | model | 推文数据，包含推文数据的_to_raw、_to_dict方法 |

<<< @/snippets/twitter/one-tweet.py{17}

### 主页推文数据 🟢

异步方法，用于获取主页推文的数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| userId | str | 用户ID |
| page_counts | int | 页数，初始为 `20` |
| max_cursor | str | 翻页参数，初始为空 |
| max_counts | int | 最大获取数量, 初始为 `None` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| PostTweetFilter | model | 主页推文数据，包含主页推文数据的_to_raw、_to_dict方法 |

<<< @/snippets/twitter/user-tweet.py{18}

### 喜欢推文数据 🟢

异步方法，用于获取喜欢推文的数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| userId | str | 用户ID |
| page_counts | int | 页数，初始为 `20` |
| max_cursor | str | 翻页参数，初始为空 |
| max_counts | int | 最大获取数量, 初始为 `None` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| LikeTweetFilter | model | 喜欢推文数据，包含喜欢推文数据的_to_raw、_to_dict方法 |

<<< @/snippets/twitter/user-like.py{17-22}

### 收藏推文数据 🟢

异步方法，用于获取收藏推文的数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| page_counts | int | 页数，初始为 `20` |
| max_cursor | str | 翻页参数，初始为空 |
| max_counts | int | 最大获取数量, 初始为 `None` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| BookmarkTweetFilter | model | 收藏推文数据，包含收藏推文数据的_to_raw、_to_dict方法 |

<<< @/snippets/twitter/user-bookmark.py{17-21}

## utils接口列表

### 管理客户端配置 🟢

类方法，用于管理客户端配置。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| 配置文件值 | Any | 配置文件值 |

<<< @/snippets/twitter/client-config.py{4,5,7,8,10,11}

### 提取单个用户ID 🟢

类方法，用于提取单个用户ID。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 用户主页地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_id | str | 用户ID |

<<< @/snippets/twitter/user-unique-ids.py#single-user-unique-id-snippet{8}

### 提取列表用户ID 🟢

类方法，用于提取列表用户ID。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | str | 用户主页地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| user_ids | list | 用户ID列表 |

<<< @/snippets/twitter/user-unique-ids.py#multi-user-unique-id-snippet{18}

### 提取单个推文ID 🟢

类方法，用于提取单个推文ID。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| url | str | 推文地址 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| tweet_id | str | 推文ID |

<<< @/snippets/twitter/tweet-ids.py#single-tweet-id-snippet{8}

### 提取列表推文ID 🟢

类方法，用于提取列表推文ID。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| urls | str | 推文地址列表 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| tweet_ids | list | 推文ID列表 |

<<< @/snippets/twitter/tweet-ids.py#multi-tweet-id-snippet{19}

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
| tweet_data | dict | 作品数据的字典 |
| custom_fields | dict | 用户自定义字段, 用于替代默认的字段值 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| file_name | str | 格式化后的文件名 |

<<< @/snippets/twitter/format-file-name.py{13,19,27,31,33-36}

### 创建用户目录 🟢

用于创建用户目录，如果目录已存在则不创建。

::: details :open_file_folder: 用户目录结构
如果未在配置文件中指定路径，则默认为 `Download`。支持绝对与相对路径。
```bash
├── Download
│   ├── twitter
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

<<< @/snippets/twitter/user-folder.py#create-user-folder{18,19}

### 重命名用户目录 🟢

用于重命名用户目录。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| old_path | Path | 旧的用户目录路径对象 |
| new_nickname | str | 新的用户昵称 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| new_path | Path | 新的用户目录路径对象 |

<<< @/snippets/twitter/user-folder.py#rename-user-folder{21-25,29,30}

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

### 提取推文文案 🟢

用于提取推文文案，排除最后的链接。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| text | str | 推文文案 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| text | str | 提取后的推文文案 |

<<< @/snippets/twitter/extract-desc.py{13}

## crawler接口列表

### 推文详情接口 🟢

用于获取推文详情数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| TweetDetailEncode | model | 推文详情数据 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 推文详情数据 |

### 用户信息接口 🟢

用于获取用户信息数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| UserProfileEncode | model | 用户信息数据 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 用户信息数据 |

### 主页推文接口 🟢

用于获取主页推文数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| PostTweetEncode | model | 主页推文数据 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 主页推文数据 |

### 喜欢推文接口 🟢

用于获取喜欢推文数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| LikeTweetEncode | model | 喜欢推文数据 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 喜欢推文数据 |

### 收藏推文接口 🟢

用于获取收藏推文数据。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| BookmarkTweetEncode | model | 收藏推文数据 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| _fetch_get_json | dict | 收藏推文数据 |

## dl接口列表

### 创建下载任务 🟢


### 处理下载任务 🟢


### 下载文案 🟢


### 下载视频 🟢


### 下载图集 🟢

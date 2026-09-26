---
outline: [2,3]
---

# API List

::: tip Note
🟢 Indicates implemented, 🟡 Indicates in progress or being modified, 🟤 Indicates temporarily not implemented, 🔵 Indicates possible future implementation, 🔴 Indicates deprecation.
:::

::: details handler API List

|     CLI Interface      |         Method         |
| :------------------ | :------------------- |
|  Download a Single Weibo  | `handle_one_weibo`   |
|  Download User's Weibo    | `handle_user_weibo`  |

|     Data Methods API    |         Method           | Developer API |
| :------------------ | :-------------------  | :--------: |
| Create User Record & Directory | `get_or_add_user_data`|     🟢    |
| Get User Info (UID)   | `fetch_user_info`     |     🟢      |
| Get User Info (Screen Name) | `fetch_user_info_by_screen_name` |     🟢      |
| Get User Details      | `fetch_user_detail`     |     🟢      |
| Extract Weibo User ID | `extract_weibo_uid`     |     🟢      |
| Fetch Single Weibo Data | `fetch_one_weibo`        |     🟢      |
| Fetch User Weibo Data | `fetch_user_weibo`       |     🟢      |
:::

::: details utils API List

| Utility API       | Class Name              | Method                         | Status |
| :---------------- | :---------------------- | :---------------------------- | :----: |
| Manage Client Config | `ClientConfManager`   |                               |  🟢  |
| Generate Visitor Cookie | `VisitorManager`  | `gen_visitor`                 |  🟢  |
| Extract Weibo ID  | `WeiboIdFetcher`        | `get_weibo_id`                |  🟢  |
| Extract All Weibo IDs | `WeiboIdFetcher`    | `get_all_weibo_id`            |  🟢  |
| Extract Weibo User ID | `WeiboUidFetcher`   | `get_weibo_uid`               |  🟢  |
| Extract All Weibo User IDs | `WeiboUidFetcher` | `get_all_weibo_uid`       |  🟢  |
| Extract Weibo User Screen Name | `WeiboScreenNameFetcher` | `get_weibo_screen_name` |  🟢  |
| Extract All Weibo User Screen Names | `WeiboScreenNameFetcher` | `get_all_weibo_screen_name` |  🟢  |
| Global File Name Formatter | - | `format_file_name` |  🟢  |
| Create User Directory | - | `create_user_folder` |  🟢  |
| Rename User Directory | - | `rename_user_folder` |  🟢  |
| Create or Rename User Directory | - | `create_or_rename_user_folder` |  🟢  |
| Extract Weibo Content | - | `extract_desc` |  🟢  |
:::

::: details crawler API List

| Crawler URL API  | Class Name   | Method           | Status |
| :-------------- | :----------- | :-------------- | :----: |
| User Info API   | `WeiboCrawler` | `fetch_user_info` | 🟢 |
| User Details API | `WeiboCrawler` | `fetch_user_detail` | 🟢 |
| User Weibo API  | `WeiboCrawler` | `fetch_user_weibo` | 🟢 |
| Single Weibo API | `WeiboCrawler` | `fetch_weibo_detail` | 🟢 |
:::

::: details dl API List
| Downloader API   | Class Name     | Method             | Status |
| :-------------- | :------------- | :---------------- | :----: |
| Create Download Task | `WeiboDownloader` | `create_download_task` |  🟢  |
| Handle Download Task | `WeiboDownloader` | `handler_download` |  🟢  |
| Download Content | `WeiboDownloader` | `download_desc` |  🟢  |
| Download Video  | `WeiboDownloader` | `download_video` |  🟢  |
| Download Image Gallery | `WeiboDownloader` | `download_images` |  🟢  |
:::

::: tip :bulb: Tips
- Pagination parameters are included in the previous request data and can be conveniently filtered using the built-in `filter` function.
- All APIs with pagination use asynchronous generator methods, requiring `async for` iteration for automatic pagination handling.
- When `max_counts` is set to `None` or omitted, all available Weibo data will be fetched.
- Easily integrates with backend frameworks such as `FastAPI`, `Flask`, and `Django`.
- Using a logged-in `cookie` can bypass privacy settings of the account.
:::

## handler API List

### Create User Record & Directory 🟢

Asynchronous method to retrieve or create user data while also generating a user directory.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| kwargs | dict | CLI dictionary data, requires path parameter |
| user_id | str | User ID |
| db | AsyncUserDB | User database |

| Returns | Type | Description |
| :--- | :--- | :--- |
| user_path | Path | User directory path object |

<<< @/snippets/weibo/user-get-add.py{14,15,23-25}

::: tip :bulb: Tips
- This is a `CLI` mode interface, developers can define their own user directory creation functionality.
- If `mode` is not set, it defaults to the `PLEASE_SETUP_MODE` directory.
:::

### Fetch User Info (UID) 🟢

Asynchronous method to retrieve user information by UID.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| uid | str | User ID |

| Returns | Type | Description |
| :--- | :--- | :--- |
| UserInfoFilter | JsonModel | User information filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/weibo/user-profile.py{17}

### Fetch User Info (Screen Name) 🟢

Asynchronous method to retrieve user information by screen name.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| screen_name | str | User screen name |

| Returns | Type | Description |
| :--- | :--- | :--- |
| UserInfoFilter | JsonModel | User information filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/weibo/user-profile-by-name.py{17-19}

### Fetch User Details 🟢

Asynchronous method to retrieve detailed user information.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| uid | str | User ID |

| Returns | Type | Description |
| :--- | :--- | :--- |
| UserDetailFilter | JsonModel | User detail filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/weibo/user-detail.py{17}

### Extract Weibo User ID 🟢

Asynchronous method to extract and return user ID from a Weibo link.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| url | str | Weibo link |

| Returns | Type | Description |
| :--- | :--- | :--- |
| uid | str | User ID |

<<< @/snippets/weibo/extract-uid.py{15-17}

### Fetch Single Weibo Data 🟢

Asynchronous method to retrieve a single Weibo post's data.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| weibo_id | str | Weibo ID |

| Returns | Type | Description |
| :--- | :--- | :--- |
| WeiboDetailFilter | JsonModel | Weibo detail filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/weibo/one-weibo.py{17}

### Fetch User Weibo Data 🟢

Asynchronous method to retrieve a user's Weibo posts.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| uid | str | User ID |
| page | int | Page number |
| feature | int | Weibo type |
| since_id | str | Starting Weibo ID |
| max_counts | int | Maximum number of Weibo posts |
| interval | tuple | Publish time range as `(start, end)` UNIX timestamps in seconds, inclusive; unlimited by default |

| Returns | Type | Description |
| :--- | :--- | :--- |
| UserWeiboFilter | JsonModel | User Weibo filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/weibo/user-weibo.py{17-23}

## utils API List

### Manage Client Configuration 🟢

Class method for managing client configuration.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| Config Value | Any | Configuration file value |

<<< @/snippets/weibo/client-config.py{4,5,7,8,10,11}

### Generate Visitor Cookie 🟢

Class method for generating a visitor cookie.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| visitor_cookie | str | Visitor Cookie |

<<< @/snippets/weibo/visitor-cookie.py{7}

### Extract Weibo ID 🟢

Class method to extract a Weibo ID from a Weibo URL.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| url | str | Weibo link |

| Return | Type | Description |
| :--- | :--- | :--- |
| weibo_id | str | Weibo ID |

<<< @/snippets/weibo/weibo-id.py#single-weibo-id-snippet{8}

### Extract Multiple Weibo IDs 🟢

Class method to extract multiple Weibo IDs from a list of Weibo URLs.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| urls | List[str] | List of Weibo links |

| Return | Type | Description |
| :--- | :--- | :--- |
| weibo_ids | List[str] | List of Weibo IDs |

<<< @/snippets/weibo/weibo-id.py#multi-weibo-id-snippet{19,22}

### Extract Weibo User ID 🟢

Class method to extract a Weibo user ID from a Weibo profile URL.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| url | str | Weibo profile link |

| Return | Type | Description |
| :--- | :--- | :--- |
| uid | str | User ID |

<<< @/snippets/weibo/weibo-uid.py#single-weibo-uid-snippet{8}

::: tip :grey_exclamation: Tip
- The `extract_weibo_uid` method in the data interface can more comprehensively process Weibo URLs. However, this method is only applicable for non-nickname-based URLs.
:::

### Extract Multiple Weibo User IDs 🟢

Class method to extract multiple Weibo user IDs from a list of Weibo profile URLs.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| urls | List[str] | List of Weibo profile links |

| Return | Type | Description |
| :--- | :--- | :--- |
| uids | List[str] | List of User IDs |

<<< @/snippets/weibo/weibo-uid.py#multi-weibo-uid-snippet{27,30}

### Extract Weibo Username 🟢

Class method to extract a Weibo username from a Weibo profile URL.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| url | str | Weibo profile link |

| Return | Type | Description |
| :--- | :--- | :--- |
| screen_name | str | Username |

<<< @/snippets/weibo/weibo-screen-name.py#single-weibo-screen_name-snippet{8}

### Extract Multiple Weibo Usernames 🟢

Class method to extract multiple Weibo usernames from a list of Weibo profile URLs.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| urls | List[str] | List of Weibo profile links |

| Return | Type | Description |
| :--- | :--- | :--- |
| screen_names | List[str] | List of Usernames |

<<< @/snippets/weibo/weibo-screen-name.py#multi-weibo-screen_name-snippet{20,23}

::: tip :information_source: Tip
`F2` automatically handles encoding, so you don't have to worry about escaping Chinese characters.
:::

### Global File Name Formatting 🟢

Formats filenames globally based on the configuration file.
::: details :page_facing_up: Filename Formatting Rules
- Captions (`desc`) longer than `200` bytes are shortened in the middle and joined with `......`.
- When downloading, the whole file name including its suffix is kept within `255` bytes and shortened in the middle if needed. This is the limit of `ext4` and most `NAS` file systems; `NTFS` and `APFS` count characters and are never exceeded.
- On `Windows`, paths longer than `260` characters automatically use the extended-length form (`\\?\`), so long path support does not need to be enabled.
- Developers can define custom fields in `custom_fields` to generate custom filenames.
:::

| Parameter | Type | Description |
| :--- | :--- | :--- |
| naming_template | str | File naming template |
| weibo_data | dict | Dictionary of Weibo post data |
| custom_fields | dict | User-defined fields for replacing default values |

| Return | Type | Description |
| :--- | :--- | :--- |
| file_name | str | Formatted file name |

<<< @/snippets/weibo/format-file-name.py{13,19,24,28,30-33}

### Create User Directory 🟢

Creates a user directory if it does not already exist.

::: details :open_file_folder: User Directory Structure
If no path is specified in the configuration file, the default directory is `Download`. Both absolute and relative paths are supported.
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
| Parameter | Type | Description |
| :--- | :--- | :--- |
| kwargs | dict | CLI configuration file |
| nickname | Union[str, int] | User nickname |

| Return | Type | Description |
| :--- | :--- | :--- |
| user_path | Path | User directory path object |

<<< @/snippets/weibo/user-folder.py#create-user-folder{17,18}

### Rename User Directory 🟢

Used to rename a user directory.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| old_path | Path | Old user directory path object |
| new_nickname | str | New user nickname |

| Return | Type | Description |
| :--- | :--- | :--- |
| new_path | Path | New user directory path object |

<<< @/snippets/weibo/user-folder.py#rename-user-folder{20-24,28,29}

::: tip :bulb: Tip
If the directory does not exist, it will first create the user directory before renaming it.
:::

### Create or Rename User Directory 🟢

Used to create or rename a user directory. When the nickname in the local record (`local_user_data["nickname"]`) differs from the current nickname, the directory of the old nickname is renamed to the current nickname and the downloaded files are kept; without a local record, or when the nickname has not changed, the user directory is simply created.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| kwargs | dict | CLI configuration file |
| local_user_data | dict | Local user data |
| current_nickname | str | Current user nickname |

| Return | Type | Description |
| :--- | :--- | :--- |
| user_path | Path | User directory path object |

::: tip :information_source: Tip
- The directories of the old and the new nickname are computed the same way as `create_user_folder` (`path`, app name, `mode`); only the directory of the current download mode is handled.
- If the directory of the old nickname does not exist, a new directory is created. If the directory of the new nickname already exists, both directories are left as they are, nothing is overwritten or merged, and a message is logged.
- If renaming fails (for example because a file in the directory is in use by another program), the old directory is used this time and renaming is retried on the next run.
- It is integrated into `get_or_add_user_data` of the `handler`, so developers only need to call the `handler` data interface.
:::

### Extract Weibo Text 🟢

Used to extract Weibo text while excluding the final link.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| text | str | Weibo text |

| Return | Type | Description |
| :--- | :--- | :--- |
| text | str | Extracted Weibo text |

<<< @/snippets/weibo/extract-desc.py{18}

## Crawler API List

### User Information API 🟢

Used to retrieve user information.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| params | UserInfo | User information API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | User information data |

### User Details API 🟢

Used to retrieve user details.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| params | UserDetail | User details API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | User details data |

### User Weibo API 🟢

Used to retrieve a user's Weibo posts.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| params | UserWeibo | User Weibo API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | User Weibo data |

### Single Weibo API 🟢

Used to retrieve a single Weibo post.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| params | WeiboDetail | Single Weibo API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Single Weibo data |

## DL API List


### Create Download Task 🟢


### Process Download Task 🟢


### Download Text 🟢


### Download Video 🟢


### Download Image Gallery 🟢

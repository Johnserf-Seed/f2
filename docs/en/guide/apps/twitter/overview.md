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
| Download single tweet | `handle_one_tweet`     |
| Download home tweets  | `handle_post_tweet`    |
| Download liked tweets | `handle_like_tweet`    |
| Download bookmarked tweets | `handle_bookmark_tweet` |

|     Data Methods Interface  |         Method            | Developer API |
| :------------------ | :-------------------   | :--------: |
| Create user record and directory | `get_or_add_user_data`   |    🟢   |
| Fetch user profile  | `fetch_user_profile`     |    🟢   |
| Fetch single tweet  | `fetch_one_tweet`        |    🟢   |
| Fetch home tweets   | `fetch_post_tweet`       |    🟢   |
| Fetch liked tweets  | `fetch_like_tweet`       |    🟢   |
| Fetch bookmarked tweets | `fetch_bookmark_tweet`   |    🟢   |
:::

::: details utils Interface List

|    Utility Interface   |          Class         |              Method           | Status |
| :--------------- | :------------------- | :-------------------------- | :--: |
|  Manage client config  | `ClientConfManager`  |                            |  🟢  |
|  Extract unique user ID | `UniqueIdFetcher`      | `get_unique_id`              |  🟢  |
|  Extract multiple user IDs | `UniqueIdFetcher`      | `get_all_unique_ids`         |  🟢  |
|  Extract tweet ID  | `TweetIdFetcher`     | `get_tweet_id`             |  🟢  |
|  Extract multiple tweet IDs | `TweetIdFetcher`     | `get_all_tweet_ids`        |  🟢  |
|  Global filename formatting  | -                   | `format_file_name`          |  🟢  |
|  Create user directory  | -                   | `create_user_folder`        |  🟢  |
|  Rename user directory | -                 | `rename_user_folder`          |  🟢  |
|  Create or rename user directory | -                 | `create_or_rename_user_folder` |  🟢  |
|  Extract tweet text | -                    | `extract_desc`              |  🟢  |
:::

::: details crawler Interface List

| Crawler URL Interface | Class       | Method          | Status |
| :----------- | :--------- | :----------  | :--: |
| Tweet details API   | `TwitterCrawler` | `fetch_tweet_detail` |  🟢  |
| User profile API   | `TwitterCrawler` | `fetch_user_profile` |  🟢  |
| Home tweets API   | `TwitterCrawler` | `fetch_post_tweet`    |  🟢  |
| Liked tweets API   | `TwitterCrawler` | `fetch_like_tweet`    |  🟢  |
| Bookmarked tweets API | `TwitterCrawler` | `fetch_bookmark_tweet`|  🟢  |
:::

::: details dl Interface List

| Downloader Interface | Class        | Method         |  Status |
| :----------- | :--------- | :----------  | :--: |
| Create download task  | `TwitterDownloader` | `create_download_task` |  🟢  |
| Handle download task  | `TwitterDownloader` | `handler_download` |  🟢  |
| Download tweet text  | `TwitterDownloader` | `download_desc`    |  🟢  |
| Download video  | `TwitterDownloader` | `download_video`   |  🟢  |
| Download image gallery | `TwitterDownloader` | `download_images`  |  🟢  |
:::

::: tip :bulb: Tips
- Pagination parameters are included in the previous request’s data, making it easy to retrieve using the built-in `filter`.
- All APIs supporting pagination use asynchronous generator methods and should be iterated using `async for` for seamless handling.
- When `max_counts` is set to `None` or omitted, all tweet data will be fetched.
- These APIs can be easily integrated with backend frameworks like `FastAPI`, `Flask`, and `Django`.
:::

## handler Interface List

### Create User Record and Directory 🟢

Asynchronous method to fetch or create user data while creating a user directory.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| kwargs | dict | CLI dictionary data requiring `path` parameter |
| sec_user_id| str | User ID |
| db | AsyncUserDB | User database |

| Returns | Type | Description |
| :--- | :--- | :--- |
| user_path | Path | User directory path object |

<<< @/snippets/twitter/user-get-add.py{13,14,19,22-24}

::: tip :bulb: Tips
- This is a `CLI`-based interface, and developers can define their own user directory creation functionality.
- If `mode` is not set, it defaults to `PLEASE_SETUP_MODE` directory.
:::

### Fetch User Profile 🟢

Asynchronous method to fetch user profile information.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| uniqueId | str | User ID |

| Returns | Type | Description |
| :--- | :--- | :--- |
| UserProfileFilter | model | User data filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/twitter/user-profile.py{18}

### Fetch Single Tweet Data 🟢

Asynchronous method to fetch data for a single tweet.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| tweet_id | str | Tweet ID |

| Returns | Type | Description |
| :--- | :--- | :--- |
| TweetDetailFilter | model | Tweet data filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/twitter/one-tweet.py{17}

### Fetch Home Tweets Data 🟢

Asynchronous method to fetch data for home tweets.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| userId | str | User ID |
| page_counts | int | Number of pages (default: `20`) |
| max_cursor | str | Pagination parameter (default: empty) |
| max_counts | int | Maximum fetch limit (default: `None`) |

| Returns | Type | Description |
| :--- | :--- | :--- |
| PostTweetFilter | model | Home tweet data filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/twitter/user-tweet.py{18}

### Fetch Liked Tweets Data 🟢

Asynchronous method to fetch liked tweets data.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| userId | str | User ID |
| page_counts | int | Number of pages (default: `20`) |
| max_cursor | str | Pagination parameter (default: empty) |
| max_counts | int | Maximum fetch limit (default: `None`) |

| Returns | Type | Description |
| :--- | :--- | :--- |
| LikeTweetFilter | model | Liked tweet data filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/twitter/user-like.py{17-22}

### Fetch Bookmarked Tweets Data 🟢

Asynchronous method to fetch bookmarked tweets.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| page_counts | int | Number of pages (default: `20`) |
| max_cursor | str | Pagination parameter (default: empty) |
| max_counts | int | Maximum fetch limit (default: `None`) |

| Returns | Type | Description |
| :--- | :--- | :--- |
| BookmarkTweetFilter | model | Bookmarked tweet data filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/twitter/user-bookmark.py{17-21}

## utils Interface List

### Manage Client Configuration 🟢

Class method for managing client configuration.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Returns | Type | Description |
| :--- | :--- | :--- |
| Config value | Any | Configuration file value |

<<< @/snippets/twitter/client-config.py{4,5,7,8,10,11}

### Extract Single User ID 🟢

Class method to extract a single user ID.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| url | str | User profile URL |

| Returns | Type | Description |
| :--- | :--- | :--- |
| user_id | str | User ID |

<<< @/snippets/twitter/user-unique-ids.py#single-user-unique-id-snippet{8}

### Extract List of User IDs 🟢

Class method for extracting user IDs from a list.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| urls | str | List of user profile URLs |

| Return | Type | Description |
| :--- | :--- | :--- |
| user_ids | list | List of user IDs |

<<< @/snippets/twitter/user-unique-ids.py#multi-user-unique-id-snippet{18}

### Extract Single Tweet ID 🟢

Class method for extracting a single tweet ID.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| url | str | Tweet URL |

| Return | Type | Description |
| :--- | :--- | :--- |
| tweet_id | str | Tweet ID |

<<< @/snippets/twitter/tweet-ids.py#single-tweet-id-snippet{8}

### Extract List of Tweet IDs 🟢

Class method for extracting multiple tweet IDs.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| urls | str | List of tweet URLs |

| Return | Type | Description |
| :--- | :--- | :--- |
| tweet_ids | list | List of tweet IDs |

<<< @/snippets/twitter/tweet-ids.py#multi-tweet-id-snippet{19}

### Global Filename Formatting 🟢

Formats filenames globally based on the configuration file.

::: details :page_facing_up: Filename Formatting Rules
- Captions (`desc`) longer than `200` bytes are shortened in the middle and joined with `......`.
- When downloading, the whole file name including its suffix is kept within `255` bytes and shortened in the middle if needed. This is the limit of `ext4` and most `NAS` file systems; `NTFS` and `APFS` count characters and are never exceeded.
- On `Windows`, paths longer than `260` characters automatically use the extended-length form (`\\?\`), so long path support does not need to be enabled.
- Developers can use the `custom_fields` parameter to customize filenames.
:::

| Parameter | Type | Description |
| :--- | :--- | :--- |
| naming_template | str | Naming template for the file |
| tweet_data | dict | Dictionary containing tweet metadata |
| custom_fields | dict | User-defined fields for customizing filenames |

| Return | Type | Description |
| :--- | :--- | :--- |
| file_name | str | Formatted filename |

<<< @/snippets/twitter/format-file-name.py{13,19,27,31,33-36}

### Create User Directory 🟢

Creates a user directory if it does not already exist.

::: details :open_file_folder: User Directory Structure
If no path is specified in the configuration file, defaults to `Download`. Supports both absolute and relative paths.
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
| Parameter | Type | Description |
| :--- | :--- | :--- |
| kwargs | dict | CLI configuration file |
| nickname | Union[str, int] | User nickname |

| Return | Type | Description |
| :--- | :--- | :--- |
| user_path | Path | User directory path object |

<<< @/snippets/twitter/user-folder.py#create-user-folder{18,19}

### Rename User Directory 🟢

Used to rename a user directory.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| old_path | Path | Old user directory path object |
| new_nickname | str | New user nickname |

| Return | Type | Description |
| :--- | :--- | :--- |
| new_path | Path | New user directory path object |

<<< @/snippets/twitter/user-folder.py#rename-user-folder{21-25,29,30}

::: tip :bulb: Note
If the directory does not exist, it will first create the user directory before renaming.
:::

### Create or Rename User Directory 🟢

Used to create or rename a user directory. A combination of the two interfaces above.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| kwargs | dict | CLI configuration file |
| local_user_data | dict | Local user data |
| current_nickname | str | Current user nickname |

| Return | Type | Description |
| :--- | :--- | :--- |
| user_path | Path | User directory path object |

::: tip :information_source: Note
This interface effectively prevents redundant directory creation when a user changes their nickname. Integrated into the `handler` interface, developers do not need to worry about it—just call the data interface of `handler` directly.
:::

### Extract Weibo Text 🟢

Used to extract Weibo text, excluding the final link.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| text | str | Weibo text |

| Return | Type | Description |
| :--- | :--- | :--- |
| text | str | Extracted Weibo text |

<<< @/snippets/twitter/extract-desc.py{13}

## Crawler API List

### Tweet Detail API 🟢

Used to fetch tweet detail data.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| TweetDetailEncode | model | Tweet detail data |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Tweet detail data |

### User Info API 🟢

Used to fetch user information.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| UserProfileEncode | model | User information data |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | User information data |

### Home Tweet API 🟢

Used to fetch tweets from a user's homepage.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| PostTweetEncode | model | Homepage tweet data |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Homepage tweet data |

### Liked Tweet API 🟢

Used to fetch liked tweets.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| LikeTweetEncode | model | Liked tweet data |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Liked tweet data |

### Bookmarked Tweet API 🟢

Used to fetch bookmarked tweets.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| BookmarkTweetEncode | model | Bookmarked tweet data |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Bookmarked tweet data |

## Download API List


### Create Download Task 🟢


### Process Download Task 🟢


### Download Caption 🟢


### Download Video 🟢


### Download Image Gallery 🟢

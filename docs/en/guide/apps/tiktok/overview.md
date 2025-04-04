---
outline: [2,3]
---

# API List

::: tip Note
🟢 Indicates implemented, 🟡 Indicates in progress or being modified, 🟤 Indicates temporarily not implemented, 🔵 Indicates possible future implementation, 🔴 Indicates deprecation.
:::

::: details handler API List

|     CLI Interface        |         Method        |
| :---------------------- | :-------------------  |
| Download a single video | `handle_one_video`    |
| Download user posts     | `handle_user_post`    |
| Download user likes     | `handle_user_like`    |
| Download user favorites | `handle_user_collect` |
| Download user playlist  | `handle_user_mix`     |
| Download search videos  | `handle_search_video` |
| Download user live stream | `handle_user_live` |

|     Data & Function APIs     |         Method           | Developer API |
| :------------------------- | :-------------------  | :--------: |
| User profile               | `fetch_user_profile`    |     🟢      |
| Create user record & folder | `get_or_add_user_data`  |     🟢      |
| Create video download record | `get_or_add_video_data` |     🟢      |
| Fetch single video data     | `fetch_one_video`       |     🟢      |
| Fetch user posts data       | `fetch_user_post_videos` |     🟢      |
| Fetch user liked videos     | `fetch_user_like_videos` |     🟢      |
| Fetch user favorites        | `fetch_user_collect_videos` |  🟢      |
| Fetch user playlists        | `fetch_play_list`        |     🟢      |
| Fetch user playlist videos  | `fetch_user_mix_videos`  |    🟢     |
| Fetch search results        | `fetch_search_videos`    |     🟢      |
| Fetch user live stream      | `fetch_user_live_videos` |     🟢      |
| Check live stream status    | `fetch_check_live_alive` |     🟢      |
:::

::: details utils API List

| Developer API      | Class Name         | Method               | Status |
| :--------------- | :-------------- | :------------------ | :--: |
| Manage client config | `ClientConfManager`   |                  |  🟢  |
| Generate real msToken | `TokenManager`     | `gen_real_msToken`   |  🟢  |
| Generate fake msToken | `TokenManager`     | `gen_false_msToken`  |  🟢  |
| Generate ttwid        | `TokenManager`     | `gen_ttwid`          |  🟢  |
| Generate odin_tt      | `TokenManager`      | `gen_odin_tt`        |  🟢  |
| Generate Xb params from URL | `XBogusManager` | `str_2_endpoint`    |  🟢  |
| Generate Xb params from model | `XBogusManager` | `model_2_endpoint` |  🟢  |
| Extract single user ID | `SecUserIdFetcher` | `get_secuid`        |  🟢  |
| Extract list of user IDs | `SecUserIdFetcher` | `get_all_secuid`   |  🟢  |
| Extract single unique user ID | `SecUserIdFetcher` | `get_uniqueid` |  🟢  |
| Extract list of unique user IDs | `SecUserIdFetcher` | `get_all_uniqueid` |  🟢  |
| Extract list of user IDs | `SecUserIdFetcher` | `get_all_secUid`  |  🟢  |
| Extract single video ID | `AwemeIdFetcher`   | `get_aweme_id`     |  🟢  |
| Extract list of video IDs | `AwemeIdFetcher`   | `get_all_aweme_id` |  🟢  |
| Generate device ID       | `DeviceIdManager`  | `gen_device_id`    |  🟢  |
| Generate list of device IDs | `DeviceIdManager` | `gen_device_ids` |  🟢  |
| Global file name formatting | -                | `format_file_name`  |  🟢  |
| Create user folder       | -                | `create_user_folder` |  🟢  |
| Rename user folder       | -                | `rename_user_folder` |  🟢  |
| Create or rename user folder | -          | `create_or_rename_user_folder` |   🟢   |
:::

::: details crawler API List

| Crawler URL API  | Class Name       | Method               | Status |
| :------------- | :------------- | :------------------ | :--: |
| User profile API | `TiktokCrawler` | `fetch_user_profile` |  🟢  |
| User posts API   | `TiktokCrawler` | `fetch_user_post`    |  🟢  |
| User likes API   | `TiktokCrawler` | `fetch_user_like`    |  🟢  |
| User favorites API | `TiktokCrawler` | `fetch_user_collect` |  🟢  |
| User playlist API | `TiktokCrawler` | `fetch_user_play_list` |  🟢  |
| Playlist videos API | `TiktokCrawler` | `fetch_user_mix` |  🟢  |
| Video details API | `TiktokCrawler` | `fetch_post_detail` |  🟢  |
| Video comments API | `TiktokCrawler` | `fetch_post_comment` |  🟢  |
| Homepage feed API | `TiktokCrawler` | `fetch_post_feed` |  🟢  |
| Search videos API | `TiktokCrawler` | `fetch_post_search` |  🟢  |
| User live stream API | `TiktokCrawler` | `fetch_user_live` |  🟢  |
| Check live stream status API | `TiktokCrawler` | `fetch_check_live_alive` |  🟢  |
:::

::: details dl API List

| Downloader API | Class Name       | Method                | Status |
| :----------- | :------------- | :----------------- | :--: |
| Save last downloaded video ID | `TiktokDownloader` | `save_last_aweme_id` |  🟢  |
| Filter videos by time range | `TiktokDownloader` | `filter_aweme_datas_by_interval` |  🟢  |
| Create download task | `TiktokDownloader` | `create_download_task` |  🟢  |
| Handle download task | `TiktokDownloader` | `handle_download` |  🟢  |
| Create stream download task | `TiktokDownloader` | `create_stream_tasks` |  🟢  |
| Handle stream download task | `TiktokDownloader` | `handle_stream` |  🟢  |
:::

::: tip :bulb: Tip
- Pagination parameters are included in the response from the previous request, making it easy to filter results using the built-in `filter`.
- All APIs with pagination use asynchronous generators, requiring iteration with `async for` for automatic pagination handling.
- If `max_counts` is set to `None` or omitted, all available video data will be fetched.
- These APIs can be easily integrated into backend frameworks like `FastAPI`, `Flask`, and `Django`.
- Using a logged-in `cookie` allows bypassing privacy restrictions, such as private `videos`, `profile`, `likes`, and `favorites`.
:::

## Handler Interface List

### Single Video Data 🟢

Asynchronous method to retrieve a single video.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| aweme_id | str | Video ID |

| Return | Type | Description |
| :--- | :--- | :--- |
| video_data | dict | Dictionary containing video data, including video ID, caption, author nickname, etc. |

<<< @/snippets/tiktok/one-video.py{15}

### User Published Videos 🟢

Asynchronous method to retrieve a list of videos published by a user.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| secUid | str | User ID |
| cursor | int | Page number, default is `0` |
| page_counts | int | Number of pages, default is `20` |
| max_counts | int | Maximum number of pages, default is `None` |

| Return | Type | Description |
| :--- | :--- | :--- |
| aweme_data | dict | Dictionary containing video data, including video ID, caption, author nickname, page number, etc. |

<<< @/snippets/tiktok/user-post.py{18,20-22}

### User Liked Videos 🟢

Asynchronous method to retrieve a list of videos liked by a specified user. The like list must be public.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| secUid | str | User ID |
| cursor | int | Page number, default is `0` |
| page_counts | int | Number of pages, default is `20` |
| max_counts | int | Maximum number of pages, default is `None` |

| Return | Type | Description |
| :--- | :--- | :--- |
| aweme_data | dict | Dictionary containing video data, including video ID, caption, author nickname, page number, etc. |

<<< @/snippets/tiktok/user-like.py{17-19,21-23}

### User Collected Videos 🟢

Asynchronous method to retrieve a list of videos collected by a specified user.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| secUid | str | User ID |
| cursor | int | Page number, default is `0` |
| page_counts | int | Number of pages, default is `20` |
| max_counts | int | Maximum number of pages, default is `None` |

| Return | Type | Description |
| :--- | :--- | :--- |
| aweme_data | dict | Dictionary containing video data, including video ID, caption, author nickname, page number, etc. |

<<< @/snippets/tiktok/user-collect.py{17-19,21-23}

### User Playlist Videos 🟢

Asynchronous method to retrieve a list of videos from a specified user's playlist.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| secUid | str | Collection ID |
| cursor | int | Page number, default is `0` |
| page_counts | int | Number of pages, default is `20` |

| Return | Type | Description |
| :--- | :--- | :--- |
| aweme_data | dict | Dictionary containing video data, including video ID, caption, author nickname, page number, etc. |

<<< @/snippets/tiktok/user-playlist.py{17-18}

### User Collection Videos 🟢

Asynchronous method to retrieve a list of videos from a specified user collection. The `mix_id` for all collection videos remains the same and can be retrieved from the single video data interface.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| mixId | str | Collection ID |
| cursor | int | Page number, default is `0` |
| page_counts | int | Number of pages, default is `20` |
| max_counts | int | Maximum number of pages, default is `None` |

| Return | Type | Description |
| :--- | :--- | :--- |
| aweme_data | dict | Dictionary containing video data, including video ID, caption, author nickname, page number, etc. |

<<< @/snippets/tiktok/user-mix.py#playlist-sinppet{18-19,21-22}

::: tip Note
Multiple playlists may contain multiple `mix_id` values. Use the `select_playlist` method to return the index of the user-selected collection.
:::

<<< @/snippets/tiktok/user-mix.py#select-playlist-sinppet{19-22}

### User Profile 🟢

Asynchronous method to retrieve a specified user's profile information. The data from `Filter` cannot be parsed directly; use custom `_to_dict` or `_to_list` methods.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| secUid | str | User ID |
| uniqueId | str | User ID |

| Return | Type | Description |
| :--- | :--- | :--- |
| UserProfileFilter | model | Custom interface data filter | Dictionary containing user ID, nickname, bio, profile picture, etc. |

<<< @/snippets/tiktok/user-profile.py{16-20,26}

::: tip :bulb: Hint
TikTok's user interface supports both `secUid` and `uniqueId` as user IDs.
:::

### Create User Record and Directory 🟢

Asynchronous method to fetch or create user data while creating a user directory.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| kwargs | dict | `cli` dictionary data, requires the `path` parameter |
| secUid | str | User ID |
| db | AsyncUserDB | User database |

| Return | Type | Description |
| :--- | :--- | :--- |
| user_path | Path | User directory path object |

<<< @/snippets/tiktok/user-get-add.py{17-23}

::: tip :bulb: Hint
This is an interface for `cli` mode. Developers can define their own functions to create user directories.
:::

### Create Video Download Record 🟢

Asynchronous method to fetch or create video data while creating a video directory.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| aweme_data | dict | Video data dictionary |
| db | AsyncVideoDB | Video database |
| ignore_fields | list | List of fields to ignore |

| Return | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

<<< @/snippets/tiktok/video-get-add.py{6,7,23-26}

## Utils Interface List

### Manage Client Configuration 🟢

Class method to manage client configuration.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| Config Value | Any | Configuration file value |

<<< @/snippets/tiktok/client-config.py{4,5,7,8,10,11}

### Generate Real `msToken` 🟢

Class method to generate a real `msToken`. Returns a fake value in case of errors.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| msToken | str | Real `msToken` |

<<< @/snippets/tiktok/token-manager.py#mstoken-real-sinppest{4}

### Generate Fake `msToken` 🟢

Class method to generate a randomly faked `msToken`. The length of `msToken` varies across endpoints.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| msToken | str | Fake `msToken` |

<<< @/snippets/tiktok/token-manager.py#mstoken-false-sinppest{4}

::: tip :bulb: Hint
The default length is `126 characters`. You can also call `from from f2.utils.string.generator import gen_random_str` to generate a fake `msToken` of a different length.
:::

### Generate `ttwid` 🟢

Class method to generate `ttwid`, which is required for certain requests.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| ttwid | str | `ttwid` parameter |

<<< @/snippets/tiktok/token-manager.py#ttwid-sinppest{4}

::: warning :warning: Warning
The `ttwid` value in the configuration file is a new `ttwid` cookie. If it expires, replace it with a new `ttwid` value.
:::

### Generate odin_tt 🟢

Class method for generating `odin_tt`, required for some requests.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| odin_tt | str | The `odin_tt` parameter |

<<< @/snippets/tiktok/token-manager.py#odin_tt-sinppest{4}

::: warning :warning: Note
The `odin_tt` parameter in the configuration file is fixed and cannot be changed.
:::

### Generate Xb Parameter Using API Endpoint 🟢

Class method for directly generating the `Xbogus` parameter using an API endpoint. Some APIs do not require validation.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| endpoint | str | API endpoint |

| Return | Type | Description |
| :--- | :--- | :--- |
| final_endpoint | str | The complete API URL with `Xbogus` parameter |

<<< @/snippets/tiktok/xbogus.py#str-2-endpoint-snippet{8}

### Generate Xb Parameter Using API Model 🟢

Class method for generating the `Xbogus` parameter using different API data models. Some APIs do not require validation.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| endpoint | str | API endpoint |
| params | dict | Request parameters |

| Return | Type | Description |
| :--- | :--- | :--- |
| final_endpoint | str | The complete API URL with `Xbogus` parameter |

To generate an endpoint using a model, create a model object and call the `model_2_endpoint` method.

<<< @/snippets/tiktok/xbogus.py#model-2-endpoint-snippet{9,16}

Data collection is also possible using a crawler engine with a filter.

<<< @/snippets/tiktok/xbogus.py#model-2-endpoint-2-filter-snippet{22,24}

For more advanced use cases, call `fetch_user_profile` from the `handler` interface.

### Extract Single User ID 🟢

Class method to extract a single user ID.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| url | str | User profile URL |

| Return | Type | Description |
| :--- | :--- | :--- |
| sec_uid | str | User ID |

<<< @/snippets/tiktok/sec-uid.py#single-secuid-snippet{8}

### Extract Multiple User IDs 🟢

Class method to extract multiple user IDs.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| urls | list | List of user profile URLs |

| Return | Type | Description |
| :--- | :--- | :--- |
| secuids | list | List of user IDs |

<<< @/snippets/tiktok/sec-uid.py#multi-secuid-snippet{14,17}

### Extract Single Unique User ID 🟢

Class method to extract a single unique user ID.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| url | str | User profile URL |

| Return | Type | Description |
| :--- | :--- | :--- |
| unique_id | str | Unique user ID |

<<< @/snippets/tiktok/unique-id.py#single-unique-id-snippet{8}

### Extract Multiple Unique User IDs 🟢

Class method to extract multiple unique user IDs.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| urls | list | List of user profile URLs |

| Return | Type | Description |
| :--- | :--- | :--- |
| unique_ids | list | List of unique user IDs |

<<< @/snippets/tiktok/unique-id.py#multi-unique-id-snippet{14,17}

### Extract Single Video ID 🟢

Class method to extract a single video ID.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| url | str | Video URL |

| Return | Type | Description |
| :--- | :--- | :--- |
| aweme_id | str | Video ID |

<<< @/snippets/tiktok/aweme-id.py#single-aweme-id-snippet{8}

### Extract Multiple Video IDs 🟢

Class method to extract multiple video IDs.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| urls | list | List of video URLs |

| Return | Type | Description |
| :--- | :--- | :--- |
| aweme_ids | list | List of video IDs |

<<< @/snippets/tiktok/aweme-id.py#multi-aweme-id-snippet{14,17}

::: tip :bulb: Tip
Both web and app-shared links are valid.
:::

### Generate Device ID 🟢

Class method to generate `deviceId` and `tt_chain_token`.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| full_cookie | bool | Whether to return the full `cookie` |

| Return | Type | Description |
| :--- | :--- | :--- |
| device_id | dict | Dictionary containing device ID and `cookie` |

<<< @/snippets/tiktok/device-id.py#device-id-snippet{6,8}

### Generate Multiple Device IDs 🟢

Class method to generate multiple `deviceId` and `tt_chain_token` values.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| count | int | Number of device IDs |
| full_cookie | bool | Whether to return the full `cookie` |

| Return | Type | Description |
| :--- | :--- | :--- |
| device_ids | dict | Dictionary containing multiple device IDs and `cookies` |

<<< @/snippets/tiktok/device-id.py#device-ids-snippet{6,8}

::: tip :bulb: Tip
`deviceId` and `tt_chain_token` parameters are bound to the configuration file and affect video access. A `403` error usually indicates an issue with these parameters.
:::

### Global Filename Formatting 🟢

Formats filenames globally based on the configuration file.

::: details :page_facing_up: Filename Formatting Rules
- `Windows`: Filename length is limited to `255` characters (or `32,767` with long filename support).
- `Unix`: Filename length is limited to `255` characters.
- Truncates to `20` characters, plus suffix, to stay within the `255` limit.
- Developers can customize `custom_fields` to define their own filenames.
:::

| Parameter | Type | Description |
| :--- | :--- | :--- |
| naming_template | str | Filename template |
| aweme_data | dict | Video metadata |
| custom_fields | dict | Custom fields for replacing default values |

| Return | Type | Description |
| :--- | :--- | :--- |
| file_name | str | Formatted filename |

<<< @/snippets/tiktok/format-file-name.py{12,20,25,29,31-34}

### Create User Directory 🟢

Creates a user directory if it does not already exist.

::: details :open_file_folder: User Directory Structure
If no path is specified in the configuration file, the default is `Download`. Both absolute and relative paths are supported.
```bash
├── Download
│   ├── tiktok
│   │   ├── post
│   │   │   ├── user_nickname
│   │   │   │   ├── 2023-12-31_23-59-59_desc
│   │   │   │   │   ├── 2023-12-31_23-59-59_desc-video.mp4
│   │   │   │   │   ├── 2023-12-31_23-59-59_desc-desc.txt
│   │   │   │   │   └── ......
│   │   ├── like
│   │   ├── ...
```
:::

| Parameter | Type | Description |
| :--- | :--- | :--- |
| kwargs | dict | `cli` configuration file |
| nickname | Union[str, int] | User nickname |

| Return | Type | Description |
| :--- | :--- | :--- |
| user_path | Path | User directory path object |

<<< @/snippets/tiktok/user-folder.py#create-user-folder{17-19}

### Rename User Directory 🟢

Used to rename a user directory.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| old_path | Path | Old user directory path object |
| new_nickname | str | New user nickname |

| Return | Type | Description |
| :--- | :--- | :--- |
| new_path | Path | New user directory path object |

<<< @/snippets/tiktok/user-folder.py#rename-user-folder{20-24,26-29}

::: tip :bulb: Note
If the directory does not exist, it will be created before renaming.
:::

### Create or Rename User Directory 🟢

Used to create or rename a user directory. This is a combination of the two interfaces above.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| kwargs | dict | cli configuration file |
| local_user_data | dict | Local user data |
| current_nickname | str | Current user nickname |

| Return | Type | Description |
| :--- | :--- | :--- |
| user_path | Path | User directory path object |

::: tip :bulb: Note
This interface effectively resolves the issue of duplicate downloads when a user changes their nickname. It is integrated into the `get_or_add_user_data` method in the handler interface, so developers can call the handler’s data interface directly without worrying about this issue.
:::

## crawler Interface

### User Profile API Endpoint 🟢

API endpoint for retrieving user profile information.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| UserProfile | model | User profile API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch user profile information |

### User Posts API Endpoint 🟢

API endpoint for retrieving a user's posted videos.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| UserPost | model | User post API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch user posts |

### Liked Posts API Endpoint 🟢

API endpoint for retrieving a user's liked videos.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| UserLike | model | User liked posts API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch liked posts |

### Collected Posts API Endpoint 🟢

API endpoint for retrieving a user's collected videos.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| UserCollect | model | User collected posts API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch collected posts |

### Playlist API Endpoint 🟢

API endpoint for retrieving a user's playlist.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| UserPlayList | model | User playlist API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch user playlists |

### Playlist Videos API Endpoint 🟢

API endpoint for retrieving videos in a user's playlist.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| UserMix | model | User playlist videos API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch playlist videos |

### Post Detail API Endpoint 🟢

API endpoint for retrieving post details.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| PostDetail | model | Post detail API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch post details |

### Post Comments API Endpoint 🟢

API endpoint for retrieving post comments.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| PostComment | model | Post comments API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch post comments |

### Recommended Posts API Endpoint 🟢

API endpoint for retrieving recommended posts.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| PostDetail | model | Recommended posts API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch recommended posts |

### Search Posts API Endpoint 🟢

API endpoint for retrieving search results for posts.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| PostSearch | model | Search posts API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch search results |

### User Live API Endpoint 🟢

API endpoint for retrieving a user's live stream.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| UserLive | model | User live API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to fetch user live streams |

### Check Live Status API Endpoint 🟢

API endpoint for checking if a user is live.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| CheckLiveAlive | model | Check live status API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Method to check live status |

### Live Danmaku Initialization API Endpoint 🟢

API endpoint for initializing live chat messages (danmaku).

| Parameter | Type | Description |
| :--- | :--- | :--- |
| LiveImFetch | model | Live chat initialization API model |

| Return | Type | Description |
| :--- | :--- | :--- |
| payload_package | dict | Data package for live chat initialization |

::: tip :bulb: Note
- If no filter is needed, you can call the `crawler` API directly, which will return the data dictionary.
:::

## dl Interface

---
outline: [2,3]
---

# API List

::: tip Note
🟢 Indicates implemented, 🟡 Indicates in progress or being modified, 🟤 Indicates temporarily not implemented, 🔵 Indicates possible future implementation, 🔴 Indicates deprecation.
:::

::: details handler API List

|     CLI Interface        |         Method             |
| :---------------------- | :----------------------- |
| Download a single video | `handle_one_video`      |
| Download user’s posts   | `handle_user_post`      |
| Download user’s likes   | `handle_user_like`      |
| Download user’s music collection | `handle_user_music_collection` |
| Download user’s collection | `handle_user_collection` |
| Download user’s folders collection | `handle_user_collects` |
| Download user’s mix videos | `handle_user_mix`       |
| Download user’s live stream | `handle_user_live`      |
| Download user’s homepage recommendations | `handle_user_feed`      |
| Download related videos | `handle_related`        |
| Download friend’s posts | `handle_friend_feed`      |

|     Data Method Interface   |         Method           | Developer API |
| :------------------------ | :---------------------- | :----------: |
| Create user record & directory | `get_or_add_user_data`   |     🟢  |
| Create video download record  | `get_or_add_video_data`  |     🟢      |
| Fetch user profile            | `fetch_user_profile`     |     🟢      |
| Fetch single video data        | `fetch_one_video`        |     🟢      |
| Fetch user’s post videos       | `fetch_user_post_videos` |     🟢      |
| Fetch user’s liked videos      | `fetch_user_like_videos` |     🟢      |
| Fetch user’s music collection  | `fetch_user_music_collection` |  🟢      |
| Fetch user’s collected videos  | `fetch_user_collection_videos` |  🟢      |
| Fetch user’s folder collections | `fetch_user_collects`    |     🟢      |
| Fetch videos from user’s folder collections | `fetch_user_collects_videos` |     🟢      |
| Fetch user’s mix videos        | `fetch_user_mix_videos`  |     🟢      |
| Fetch user’s live stream data  | `fetch_user_live_videos` |     🟢      |
| Fetch user’s live stream data (by room ID) | `fetch_user_live_videos_by_room_id` | 🟢 |
| Fetch user’s homepage feed     | `fetch_user_feed_videos` |     🟢      |
| Fetch related videos           | `fetch_related_videos` |     🟢      |
| Fetch friend’s feed videos     | `fetch_friend_feed_videos` |     🟢      |
| Fetch user’s following list    | `fetch_user_following` |     🟢      |
| Fetch user’s followers         | `fetch_user_follower` |     🟢      |
| Query user data                | `fetch_query_user`   |     🟢      |
| Fetch post statistics          | `fetch_post_stats`   |     🟢      |
| Fetch live WSS load data       | `fetch_live_im`      |     🟢      |
| Fetch live WSS danmaku (chat)  | `fetch_live_danmaku` |     🟢      |
| Fetch following users' live stream info | `fetch_user_following_lives` | 🟢 |
| Fetch post danmaku | `fetch_post_danmaku` | 🟢 |
| Fetch post timerange danmaku | `fetch_post_time_danmaku` | 🟢 |
:::

::: details utils API List

| Utility Interface        | Class                   | Method                         | Status |
| :---------------------- | :--------------------- | :-------------------------- | :----: |
| Manage client configuration | `ClientConfManager`    |                              |  🟢  |
| Generate real msToken  | `TokenManager`         | `gen_real_msToken`           |  🟢  |
| Generate fake msToken  | `TokenManager`         | `gen_false_msToken`          |  🟢  |
| Generate ttwid         | `TokenManager`         | `gen_ttwid`                  |  🟢  |
| Generate webid         | `TokenManager`         | `gen_webid`                  |  🟢  |
| Generate verify_fp     | `VerifyFpManager`      | `gen_verify_fp`              |  🟢  |
| Generate s_v_web_id    | `VerifyFpManager`      | `gen_s_v_web_id`             |  🟢  |
| Generate live signature | `DouyinWebcastSignature` | `get_signature`            |  🟢  |
| Generate Xb params using API URL | `XBogusManager`        | `str_2_endpoint`             |  🟢  |
| Generate Xb params using API model | `XBogusManager`        | `model_2_endpoint`           |  🟢  |
| Generate Ab params using API URL | `ABogusManager`        | `str_2_endpoint`             |  🟢  |
| Generate Ab params using API model | `ABogusManager`        | `model_2_endpoint`           |  🟢  |
| Extract single user ID  | `SecUserIdFetcher`     | `get_sec_user_id`            |  🟢  |
| Extract list of user IDs | `SecUserIdFetcher`     | `get_all_sec_user_id`        |  🟢  |
| Extract single video ID | `AwemeIdFetcher`       | `get_aweme_id`               |  🟢  |
| Extract list of video IDs | `AwemeIdFetcher`       | `get_all_aweme_id`           |  🟢  |
| Extract single mix ID   | `MixIdFetcher`         | `get_mix_id`                 |  🟢  |
| Extract list of mix IDs | `MixIdFetcher`         | `get_all_mix_id`             |  🟢  |
| Extract single live room ID | `WebCastIdFetcher`     | `get_webcast_id`             |  🟢  |
| Extract list of live room IDs | `WebCastIdFetcher`     | `get_all_webcast_id`         |  🟢  |
| Global file name formatting | -                      | `format_file_name`           |  🟢  |
| Create user folder     | -                      | `create_user_folder`         |  🟢  |
| Rename user folder     | -                      | `rename_user_folder`         |  🟢  |
| Create or rename user folder | -                      | `create_or_rename_user_folder` | 🟢  |
| Convert JSON lyrics to LRC | -                      | `json_2_lrc`                 |  🟢  |
:::

::: details Crawler API List

| Crawler URL Interface | Class       | Method                          | Status |
|----------------------|---------------|--------------------------------|--------|
| User Info API       | `DouyinCrawler` | `fetch_user_profile`          | 🟢 |
| User Posts API      | `DouyinCrawler` | `fetch_user_post`             | 🟢 |
| User Likes API      | `DouyinCrawler` | `fetch_user_like`             | 🟢 |
| User Collection API | `DouyinCrawler` | `fetch_user_collection`       | 🟢 |
| User Playlist API   | `DouyinCrawler` | `fetch_user_collects`         | 🟢 |
| Playlist Videos API | `DouyinCrawler` | `fetch_user_collects_video`   | 🟢 |
| Music Collection API | `DouyinCrawler` | `fetch_user_music_collection` | 🟢 |
| User Mix API        | `DouyinCrawler` | `fetch_user_mix`              | 🟢 |
| Video Detail API    | `DouyinCrawler` | `fetch_post_detail`           | 🟢 |
| Video Comments API  | `DouyinCrawler` | `fetch_post_comment`          | 🟢 |
| Recommended Videos API | `DouyinCrawler` | `fetch_post_feed`          | 🟢 |
| Followed Users' Videos API | `DouyinCrawler` | `fetch_follow_feed`    | 🟢 |
| Friends' Videos API | `DouyinCrawler` | `fetch_friend_feed`           | 🟢 |
| Related Videos API  | `DouyinCrawler` | `fetch_post_related`          | 🟢 |
| Livestream API      | `DouyinCrawler` | `fetch_live`                  | 🟢 |
| Livestream API (room_id) | `DouyinCrawler` | `fetch_live_room_id` | 🟢 |
| Following Users' Livestream API | `DouyinCrawler` | `fetch_following_live` | 🟢 |
| Locate Last Video API | `DouyinCrawler` | `fetch_locate_post` | 🟢 |
| User Following List API | `DouyinCrawler` | `fetch_user_following` | 🟢 |
| User Followers List API | `DouyinCrawler` | `fetch_user_follower` | 🟢 |
| Livestream Danmaku Init API | `DouyinCrawler` | `fetch_live_im_fetch` | 🟢 |
| Query User API | `DouyinCrawler` | `fetch_query_user` | 🟢 |
| Livestream Danmaku API | `DouyinWebSocketCrawler` | `fetch_live_danmaku` | 🟢 |
| Handle WebSocket Messages | `DouyinWebSocketCrawler` | `handle_wss_message` | 🟢 |
| Send ACK Packet | `DouyinWebSocketCrawler` | `send_ack` | 🟢 |
| Send Ping Packet | `DouyinWebSocketCrawler` | `send_ping` | 🟢 |
Live room message | `DouyinWebSocketCrawler` | `WebcastRoomMessage` | 🟢
Live room like message | `DouyinWebSocketCrawler` | `WebcastLikeMessage` | 🟢
Live Room Viewer Join Message | `DouyinWebSocketCrawler` | `WebcastMemberMessage` | 🟢
Live room chat message | `DouyinWebSocketCrawler` | `WebcastChatMessage` | 🟢
Live Room Gift Message | `DouyinWebSocketCrawler` | `WebcastGiftMessage` | 🟢
Live Room User Focus Message | `DouyinWebSocketCrawler` | `WebcastSocialMessage` | 🟢
Live Room User Sequence Message | `DouyinWebSocketCrawler` | `WebcastRoomUserSeqMessage` | 🟢
Live room fan ticket update message | `DouyinWebSocketCrawler` | `WebcastUpdateFanTicketMessage` | 🟢
Live room text message | `DouyinWebSocketCrawler` | `WebcastCommonTextMessage` | 🟢
| Live room battle score message | `DouyinWebSocketCrawler` | `WebcastMatchAgainstScoreMessage` | 🟢 |
Live room e-commerce fans club message | `DouyinWebSocketCrawler` | `WebcastEcomFansClubMessage` | 🟢
Live room hourly leaderboard entrance message | `DouyinWebSocketCrawler` | `WebcastRanklistHourEntranceMessage` | 🟢
Live Room Statistics Message | `DouyinWebSocketCrawler` | `WebcastRoomStatsMessage` | 🟢
Live Room Shopping Message | `DouyinWebSocketCrawler` | `WebcastLiveShoppingMessage` | 🟢
Live Room E-commerce General Message | `DouyinWebSocketCrawler` | `WebcastLiveEcomGeneralMessage` | 🟢
Live room product change notification | `DouyinWebSocketCrawler` | `WebcastProductChangeMessage` | 🟢
Live room stream adaptation message | `DouyinWebSocketCrawler` | `WebcastRoomStreamAdaptationMessage` | 🟢
Live room notification effect message | `DouyinWebSocketCrawler` | `WebcastNotifyEffectMessage` | 🟢
Live room light gift message | `DouyinWebSocketCrawler` | `WebcastLightGiftMessage` | 🟢
Live room interaction score message | `DouyinWebSocketCrawler` | `WebcastProfitInteractionScoreMessage` | 🟢
Live room leaderboard message | `DouyinWebSocketCrawler` | `WebcastRoomRankMessage` | 🟢
Live room fan club message | `DouyinWebSocketCrawler` | `WebcastFansclubMessage` | 🟢
Live Room Hot Room Messages | `DouyinWebSocketCrawler` | `WebcastHotRoomMessage` | 🟢
Live room link-mic message | `DouyinWebSocketCrawler` | `WebcastLinkMicMethod` | 🟢
Live room cross-linking contribution message | `DouyinWebSocketCrawler` | `WebcastLinkerContributeMessage` | 🟢
Live room emoji chat messages | `DouyinWebSocketCrawler` | `WebcastEmojiChatMessage` | 🟢
Live room global chat messages | `DouyinWebSocketCrawler` | `WebcastScreenChatMessage` | 🟢
Live room data synchronization message | `DouyinWebSocketCrawler` | `WebcastRoomDataSyncMessage` | 🟢
| Banner message inside live room | `DouyinWebSocketCrawler` | `WebcastInRoomBannerMessage` | 🟢 |
Live room cross-mic message | `DouyinWebSocketCrawler` | `WebcastLinkMessage` | 🟢
Live room team task message | `DouyinWebSocketCrawler` | `WebcastBattleTeamTaskMessage` | 🟢
Live Room Hot Chat Messages | `DouyinWebSocketCrawler` | `WebcastHotChatMessage` | 🟢
:::

::: details dl Interface List

| Downloader Interface | Class | Method | Status |
| :------------------- | :--------------- | :---------------------- | :--: |
| Save Last Requested Work ID | `DouyinDownloader` | `save_last_aweme_id` | 🟢 |
| Create Download Task | `DouyinDownloader` | `create_download_task` | 🟢 |
| Handle Download Task | `DouyinDownloader` | `handler_download` | 🟢 |
| Download Original Sound | `DouyinDownloader` | `download_music` | 🟢 |
| Download Cover | `DouyinDownloader` | `download_cover` | 🟢 |
| Download Caption | `DouyinDownloader` | `download_desc` | 🟢 |
| Download Video | `DouyinDownloader` | `download_video` | 🟢 |
| Download Image Gallery | `DouyinDownloader` | `download_images` | 🟢 |
| Create Original Sound Download Task | `DouyinDownloader` | `create_music_download_tasks` | 🟢 |
| Handle Original Sound Download Task | `DouyinDownloader` | `handler_music_download` | 🟢 |
| Create Livestream Download Task | `DouyinDownloader` | `create_stream_tasks` | 🟢 |
| Handle Livestream Download | `DouyinDownloader` | `handler_stream` | 🟢 |
:::

::: tip :bulb: Tips
- Pagination parameters are included in the previous request data and can be easily retrieved using the built-in `filter` function.
- All interfaces with pagination parameters use asynchronous generator methods and should be iterated with `async for` for automatic pagination handling.
- If `max_counts` is set to `None` or omitted, all available work data will be retrieved.
- Can be conveniently integrated with backend frameworks like `FastAPI`, `Flask`, and `Django`.
- Using a logged-in `cookie` bypasses the account's privacy settings, allowing access to private `works`, `homepage`, `likes`, `collections`, etc.
:::

## Handler Interface List

### Create User Record and Directory 🟢

Asynchronous method to retrieve or create user data while also creating a user directory.

| Parameter    | Type        | Description                          |
| :---------- | :---------- | :---------------------------------- |
| kwargs      | dict        | CLI dictionary data, requires path parameter |
| sec_user_id | str        | User ID                             |
| db          | AsyncUserDB | User database                       |

| Return    | Type  | Description                      |
| :-------- | :---- | :------------------------------ |
| user_path | Path  | User directory path object      |

<<< @/snippets/douyin/user-get-add.py{12,13,18,21-23}

::: tip :bulb: Note
- This is a `CLI` mode interface, and developers can define their own user directory creation functionality.
- If the `mode` parameter is not set, it defaults to the `PLEASE_SETUP_MODE` directory.
:::

### Create Video Download Record 🟢

Asynchronous method to retrieve or create video data while also creating a video directory.

| Parameter     | Type         | Description                       |
| :----------- | :----------- | :--------------------------------- |
| aweme_data   | dict         | Video data dictionary             |
| db           | AsyncVideoDB | Video database                    |
| ignore_fields | list        | List of fields to ignore          |

| Return | Type | Description |
| :------ | :-- | :--------- |
| None   | None | None       |

<<< @/snippets/douyin/video-get-add.py{6,19-25}

### Get User Information 🟢

Asynchronous method to retrieve information of a specific user.

| Parameter    | Type | Description |
| :---------- | :---- | :---------- |
| sec_user_id | str  | User ID     |

| Return             | Type   | Description |
| :---------------- | :----- | :---------- |
| UserProfileFilter | model  | User data filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/douyin/user-profile.py{15,16}

### Get Single Video Data 🟢

Asynchronous method to retrieve a single video.

| Parameter | Type | Description |
| :-------- | :---- | :---------- |
| aweme_id  | str  | Video ID    |

| Return           | Type   | Description |
| :-------------- | :----- | :---------- |
| PostDetailFilter | model  | Single video data filter containing `_to_raw`, `_to_dict`, `_to_list` methods |

<<< @/snippets/douyin/one-video.py{15}

### Get User's Posted Videos 🟢

Asynchronous method to retrieve a list of videos posted by a user.

| Parameter    | Type  | Description                     |
| :---------- | :---- | :----------------------------- |
| sec_user_id | str   | User ID                         |
| min_cursor  | int   | Minimum page number, default 0 |
| max_cursor  | int   | Maximum page number, default 0 |
| page_counts | int   | Number of pages, default 20    |
| max_counts  | int   | Maximum list count, default None |

| Return          | Type           | Description |
| :------------- | :------------- | :---------- |
| UserPostFilter | AsyncGenerator | Posted video data filter containing `_to_raw`, `_to_dict`, `_to_list` methods |

<<< @/snippets/douyin/user-post.py{16,18-20}

### Get User's Liked Videos 🟢

Asynchronous method to retrieve a list of videos liked by a specific user (requires the likes list to be public).

| Parameter    | Type  | Description                     |
| :---------- | :---- | :----------------------------- |
| sec_user_id | str   | User ID                         |
| max_cursor  | int   | Page number, default 0         |
| page_counts | int   | Number of pages, default 20    |
| max_counts  | int   | Maximum list count, default None |

| Return          | Type           | Description |
| :------------- | :------------- | :---------- |
| UserPostFilter | AsyncGenerator | Liked video data filter containing `_to_raw`, `_to_dict`, `_to_list` methods |

<<< @/snippets/douyin/user-like.py{16-20}

### Get User's Favorite Sounds 🟢

Asynchronous method to retrieve a list of music favorited by a specific user (requires login).

| Parameter    | Type  | Description                     |
| :---------- | :---- | :----------------------------- |
| max_cursor  | int   | Page number, default 0         |
| page_counts | int   | Number of pages, default 20    |
| max_counts  | int   | Maximum list count, default None |

| Return                   | Type           | Description |
| :----------------------- | :------------- | :---------- |
| UserMusicCollectionFilter | AsyncGenerator | Favorite music data filter containing `_to_raw`, `_to_dict`, `_to_list` methods |

<<< @/snippets/douyin/user-collection.py#user-collection-music-snippet{17-20}

### Get User's Favorite Videos 🟢

Asynchronous method to retrieve a list of videos favorited by a specific user (requires login).

| Parameter    | Type  | Description                     |
| :---------- | :---- | :----------------------------- |
| max_cursor  | int   | Page number, default 0         |
| page_counts | int   | Number of pages, default 20    |
| max_counts  | int   | Maximum list count, default None |

| Return              | Type           | Description |
| :----------------- | :------------- | :---------- |
| UserCollectionFilter | AsyncGenerator | Favorite video data filter containing `_to_raw`, `_to_dict`, `_to_list` methods |

<<< @/snippets/douyin/user-collection.py#user-collection-music-snippet{17-20}

### Get User's Collections 🟢

Asynchronous method to retrieve a user's collection list (not the videos inside the collection).

| Parameter    | Type  | Description                     |
| :---------- | :---- | :----------------------------- |
| max_cursor  | int   | Page number, default 0         |
| page_counts | int   | Number of pages, default 20    |
| max_counts  | int   | Maximum list count, default None |

| Return            | Type           | Description |
| :--------------- | :------------- | :---------- |
| UserCollectsFilter | AsyncGenerator | Collection data filter containing `_to_raw`, `_to_dict`, `_to_list` methods |

<<< @/snippets/douyin/user-collects.py#user-collects-snippet{17-21}

### Get Videos from User's Collection 🟢

Asynchronous method to retrieve a list of videos inside a specific user's collection.

| Parameter   | Type  | Description                     |
| :--------- | :---- | :----------------------------- |
| collect_id | str   | Collection ID                  |
| max_cursor | int   | Page number, default 0         |
| page_counts | int   | Number of pages, default 20    |
| max_counts | int   | Maximum list count, default None |

| Return                  | Type           | Description |
| :---------------------- | :------------- | :---------- |
| UserCollectsVideosFilter | AsyncGenerator | Collection video data filter containing `_to_raw`, `_to_dict`, `_to_list` methods |

<<< @/snippets/douyin/user-collects.py#user-collects-videos-snippet{17-22}

### Get Videos from User's Playlist 🟢

Asynchronous method to retrieve a list of videos from a specific user's playlist.

| Parameter   | Type  | Description                     |
| :--------- | :---- | :----------------------------- |
| mix_id     | str   | Playlist ID                    |
| max_cursor | int   | Page number, default 0         |
| page_counts | int   | Number of pages, default 20    |
| max_counts | int   | Maximum list count, default None |

| Return        | Type           | Description |
| :----------- | :------------- | :---------- |
| UserMixFilter | AsyncGenerator | Playlist video data filter containing `_to_raw`, `_to_dict`, `_to_list` methods |

<<< @/snippets/douyin/user-mix.py{16,18-23}

::: tip :bulb: Note
- The `mix_id` for a playlist's videos remains the same. Use the `fetch_one_video` API to obtain `mix_id`.
:::

### User Livestream Data 🟢

Asynchronous method to fetch a specified user's livestream.

| Parameter  | Type | Description |
| :-------- | :-- | :---------- |
| webcast_id | str | Livestream ID |

| Return  | Type | Description |
| :------ | :-- | :---------- |
| webcast_data | dict | Dictionary containing livestream details such as ID, title, status, viewer count, subcategory, and host nickname |

<<< @/snippets/douyin/user-live.py{15}

::: tip :bulb: Tip
- `webcast_id` and `room_id` are two separate parameters parsed by different APIs.
- Example: In `https://live.douyin.com/775841227732`, `775841227732` is the livestream ID (`webcast_id`/`live_id`).
- If using a livestream link shared from the `APP`, it will resolve to `room_id`. Use the `fetch_user_live_videos_by_room_id` API instead.
:::

### User Livestream Data 2 🟢

Asynchronous method to fetch a specified user's livestream.

| Parameter  | Type | Description |
| :-------- | :-- | :---------- |
| room_id | str | Livestream Room ID |

| Return  | Type | Description |
| :------ | :-- | :---------- |
| webcast_data | dict | Dictionary containing livestream details such as ID, title, status, viewer count, subcategory, and host nickname |

<<< @/snippets/douyin/user-live-room-id.py{15-17}

::: tip :bulb: Tip
- `webcast_id` and `room_id` are two separate parameters parsed by different APIs.
- Example: In `https://webcast.amemv.com/douyin/webcast/reflow/7444223303348144935?xxx=xxx...`, `7444223303348144935` is the livestream Room ID (`room_id`).
:::

### User Homepage Recommended Posts 🟢

Asynchronous method to fetch a specified user's homepage recommended posts.

| Parameter  | Type | Description |
| :-------- | :-- | :---------- |
| sec_user_id | str | User ID |
| max_cursor | int | Page number, initially 0 |
| page_counts | int | Number of pages, initially 20 |
| max_counts | int | Maximum list count, initially None |

| Return  | Type | Description |
| :------ | :-- | :---------- |
| UserPostFilter | AsyncGenerator | Filter for recommended posts, containing `_to_raw`, `_to_dict`, and `_to_list` methods |

<<< @/snippets/douyin/user-feed.py{17-23}

### Related Posts Data 🟢

Asynchronous method to fetch similar posts to a specified post, commonly used for expanding related content.

| Parameter  | Type | Description |
| :-------- | :-- | :---------- |
| aweme_id | str | Post ID |
| filterGids | str | Filtered Gids, default empty |
| page_counts | int | Number of pages, initially 20 |
| max_counts | int | Maximum list count, initially None |

| Return  | Type | Description |
| :------ | :-- | :---------- |
| PostRelatedFilter | dict | Filter for related posts, containing `_to_raw`, `_to_dict`, and `_to_list` methods |

<<< @/snippets/douyin/aweme-related.py{16-21}

::: tip :bulb: Tip
- `filterGids` is used to exclude specific posts. Leaving it empty may result in duplicate recommendations.
- Example: Setting `filterGids` to `7419386765854641442` excludes that post. Multiple posts can be separated by commas: `7419386765854641442,741938xxxx,74193xxxx`.
- You should manually filter the `aweme_id` in each request and add it to `filterGids`.
:::

### Friend Posts Data 🟢

Asynchronous method to fetch posts from friends.

| Parameter  | Type | Description |
| :-------- | :-- | :---------- |
| cursor | str | Page number, initially 0 |
| level | int | Post level, initially 1 |
| pull_type | int | Fetch type, initially 0 |
| max_counts | int | Maximum list count, initially None |

| Return  | Type | Description |
| :------ | :-- | :---------- |
| FriendFeedFilter | AsyncGenerator | Filter for friend posts, containing `_to_raw`, `_to_dict`, and `_to_list` methods |

<<< @/snippets/douyin/user-friend.py{16-21}

::: tip :bulb: Tip
- `pull_type` options include `0`, `2`, and `18`, but their exact meaning is unknown.
:::

### Following Users Data 🟢

Asynchronous method to fetch the list of users followed by a specified user.

| Parameter  | Type | Description |
| :-------- | :-- | :---------- |
| user_id | str | User ID |
| sec_user_id | str | Secure User ID |
| offset | int | Page number, initially 0 |
| min_time | int | Earliest follow timestamp (seconds), initially 0 |
| max_time | int | Latest follow timestamp (seconds), initially 0 |
| count | int | Number of users per page, initially 20 |
| source_type | int | Sorting type, initially 4 |
| max_counts | float | Maximum number of followings, initially None |

| Return  | Type | Description |
| :------ | :-- | :---------- |
| UserFollowingFilter | AsyncGenerator | Filter for following users, containing `_to_raw`, `_to_dict`, and `_to_list` methods |

#### Offset (**offset**)

- When `source_type` is `1` or `3`, `offset` is ignored.
- When `source_type` is `4`, `offset` is valid.

#### Time Range (**min_time**/**max_time**)

- If `max_time` and `min_time` are not provided, `F2` automatically processes the time range for data completeness.
- Custom time ranges can be set manually using `max_time` and `min_time`.

#### Number of Followed Users (**count**)

- Controls the number of followed users per page. The default value is recommended.

#### Sorting Type (**source_type**)

- `1` = Sort by most recent follows.
- `3` = Sort by earliest follows.
- `4` = Sort by a mixed order.

::: tip :bulb: Note
- Only publicly visible follow lists can be accessed.
- Long time intervals may result in incomplete data. Custom time ranges are only recommended for fetching data from specific past periods.
:::

<<< @/snippets/douyin/user-following.py{18-20,22-31}

### Followers Data 🟢

Asynchronous method to fetch the followers of a specified user.

| Parameter  | Type | Description |
| :-------- | :-- | :---------- |
| user_id | str | User ID |
| sec_user_id | str | Secure User ID |
| offset | int | Page number, initially 0 |
| min_time | int | Earliest follow timestamp, initially 0 |
| max_time | int | Latest follow timestamp, initially 0 |
| count | int | Number of followers per page, initially 20 |
| source_type | int | Sorting type, initially 1 |
| max_counts | float | Maximum number of followers, default is unlimited |

| Return  | Type | Description |
| :------ | :-- | :---------- |
| UserFollowerFilter | AsyncGenerator | Filter for followers, containing `_to_raw`, `_to_dict`, and `_to_list` methods |

#### Offset (**offset**)

- When `source_type` is `1` or `2`, `offset` is ignored.

#### Time Range (**min_time**/**max_time**)

- If `max_time` and `min_time` are not provided, `F2` automatically processes the time range for data completeness.
- Custom time ranges can be set manually using `max_time` and `min_time`.

#### Number of Followers (**count**)

- Controls the number of followers per page. The default value is recommended.

#### Sorting Type (**source_type**)

- `1` = Sort by recent followers.
- `2` = Undefined behavior.

::: tip :bulb: Note
- Only publicly visible follower lists can be accessed.
- Long time intervals may result in incomplete data. Custom time ranges are only recommended for fetching data from specific past periods.
:::

<<< @/snippets/douyin/user-follower.py{18-20,22-29}

::: info Tips
The `source_type` parameter controls the sorting type, `2` is comprehensive sorting (invalid), and `1` is the most recent fans.
When `source_type` is set to `1`, you need to set the `max_time` parameter to select the time range.
:::

> [!IMPORTANT] Important ❗❗❗
> When `source_type` is set to `1`, the `offset` parameter is invalid.
> When `source_type` is set to `2`, no data is returned.

### Query User Info 🟢

Queries basic user information using `ttwid`. Use `fetch_user_profile` for more detailed data.

| Parameter  | Type | Description |
| :-------- | :-- | :---------- |
| None | None | None |

| Return  | Type | Description |
| :------ | :-- | :---------- |
| QueryUserFilter | model | Filter for user data, containing `_to_raw` and `_to_dict` methods |

<<< @/snippets/douyin/query-user.py{18}

### Livestream WSS Load Data 🟢

Asynchronous method to fetch livestream WSS load data, required for handling chat messages.

| Parameter  | Type | Description |
| :-------- | :-- | :---------- |
| room_id | str | Livestream Room ID |
| unique_id | str | User ID |

| Return  | Type | Description |
| :------ | :-- | :---------- |
| LiveImFetchFilter | model | Filter for livestream WSS load data, containing `_to_raw` and `_to_dict` methods |

<<< @/snippets/douyin/user-live-im-fetch.py#user-live-im-snippet{16-18,23-41}

### Livestream WSS Danmaku 🟢

Asynchronous method for retrieving livestream WSS danmaku (chat messages), using built-in callbacks to handle different message types.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| room_id | str | Livestream room ID |
| user_unique_id | str | User ID |
| internal_ext | str | Internal extension parameters |
| cursor | str | Danmaku page number |
| callback | dict | Custom danmaku callback functions, where keys are message types and values are handler functions |

| Callback | Description |
| :--- | :--- |
| WebcastRoomMessage | Livestream room message |
| WebcastLikeMessage | Livestream like message |
| WebcastMemberMessage | Viewer join message |
| WebcastChatMessage | Livestream chat message |
| WebcastGiftMessage | Livestream gift message |
| WebcastSocialMessage | User follow message |
| WebcastRoomUserSeqMessage | Online viewer ranking message |
| WebcastUpdateFanTicketMessage | Fan ticket update message |
| WebcastCommonTextMessage | Text message |
| WebcastMatchAgainstScoreMessage | Battle score message |
| WebcastFansclubMessage | Fan club message |
| WebcastRanklistHourEntranceMessage | Hourly ranking leaderboard message |
| WebcastRoomStatsMessage | Livestream statistics message |
| WebcastLiveShoppingMessage | Livestream shopping message |
| WebcastLiveEcomGeneralMessage | E-commerce general message |
| WebcastProductChangeMessage | Product change message |
| WebcastRoomStreamAdaptationMessage | Stream adaptation message |
| WebcastNotifyEffectMessage | Notification effect message |
| WebcastLightGiftMessage | Light gift message |
| WebcastProfitInteractionScoreMessage | Interaction score message |
| WebcastRoomRankMessage | Room ranking message |
| WebcastEcomFansClubMessage | E-commerce fan club message |
| WebcastHotRoomMessage | Hot room message |
| WebcastLinkMicMethod | LinkMic message |
| WebcastLinkerContributeMessage | LinkMic contribution message |
| WebcastEmojiChatMessage | Emoji chat message |
| WebcastScreenChatMessage | Global chat message |
| WebcastRoomDataSyncMessage | Room data sync message |
| WebcastInRoomBannerMessage | In-room banner message |
| WebcastLinkMessage | Link message |
| WebcastBattleTeamTaskMessage | Battle team task message |
| WebcastHotChatMessage | Hot chat message |

| Return | Type | Description |
| :--- | :--- | :--- |
| self.websocket | WebSocket | WebSocket object for danmaku |

<<< @/snippets/douyin/user-live-im-fetch.py#user-live-im-fetch-snippet{30-33,36-69,106-113}

### Following Users' Livestream Information 🟢

Asynchronous method to retrieve a list of livestream information for followed users. Requires `cookie` after logging in.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| FollowingUserLiveFilter | model | A filter for followed users' livestream data, containing `_to_raw` and `_to_dict` methods |

<<< @/snippets/douyin/user-follow-live.py{16}

### Post Danmaku 🟢

Asynchronous method to retrieve the danmaku (bullet comments) list for a specified work.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| aweme_id| str | Aweme ID |
| offset| int | Starting page number, initially 0 |
| count| int | Number of pages, initially 20 |
| format| str | Return format, default is json |
| max_counts| int | Maximum list count, default is None |

| Return | Type | Description |
| :--- | :--- | :--- |
| PostDanmakuFilter | AsyncGenerator | Post danmaku data filter, containing `_to_raw`, `_to_dict`, and `_to_list` methods |

<<< @/snippets/douyin/post-danmaku.py#post-danmaku-snippet{17,19-21}

### Post Time Danmaku Data 🟢

Asynchronous method to retrieve the danmaku (bullet comments) list for a specified work.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| aweme_id| str | Aweme ID |
| start_time| int | Start timestamp, in seconds |
| end_time| int | End timestamp, in seconds |
| authentication_token| str | Recognition token for the work |
| duration| int | Video duration, in milliseconds |
| format| str | Return format, default is json |

| Return | Type | Description |
| :--- | :--- | :--- |
| PostTimeDanmakuFilter | model | Post time danmaku data filter, containing `_to_raw`, `_to_dict`, and `_to_list` methods |

<<< @/snippets/douyin/post-danmaku.py#post-time-danmaku-snippet{17,19,21-28}

## Utils API List

### Manage Client Configuration 🟢

Class method for managing client configuration.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| Config value | Any | The configuration file value |

<<< @/snippets/douyin/client-config.py{4,5,7,8,10,11}

### Generate Real msToken 🟢

Class method to generate a real `msToken`. Returns a fake value if an error occurs.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| msToken | str | The real `msToken` |

<<< @/snippets/douyin/token-manager.py#mstoken-real-sinppest{4}

### Generate Fake msToken 🟢

Class method to generate a random fake `msToken`. The length varies by endpoint.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| msToken | str | The fake `msToken` |

<<< @/snippets/douyin/token-manager.py#mstoken-false-sinppest{4}

::: tip 💡 Tip
Default length is 126 characters.You can also use `from from f2.utils.string.generator import gen_random_str` to generate fake `msToken` of different lengths.
:::

### Generate ttwid 🟢

Class method to generate `ttwid`. Required for some requests and necessary in guest mode.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| ttwid | str | The `ttwid` parameter |

<<< @/snippets/douyin/token-manager.py#ttwid-sinppest{4}

### Generate webid 🟢

Class method to generate a personalized tracking `webid`.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| webid | str | The `webid` parameter |

<<< @/snippets/douyin/token-manager.py#webid-sinppest{4}

### Generate verify_fp 🟢

Class method to generate `verify_fp`, which is required for some requests.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| verify_fp | str | The `verify_fp` and `fp` parameter |

<<< @/snippets/douyin/token-manager.py#verify_fp-sinppest{4}

### Generate s_v_web_id 🟢

Class method to generate `s_v_web_id`, which is required for some requests.This is equivalent to `verify_fp`.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| s_v_web_id | str | The `s_v_web_id` parameter |

<<< @/snippets/douyin/token-manager.py#s-v-web-id-sinppest{4}

### Generate Livestream Signature 🟢

Generates the `signature` required for requesting live chat WebSocket.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| room_id | str | Livestream Room ID |
| user_unique_id | str | User ID |

| Return | Type | Description |
| :--- | :--- | :--- |
| signature | str | The livestream `signature` |

<<< @/snippets/douyin/webcast-signature.py#webcast-signature-snippet{5-10}

### Generate Xb Parameter from Endpoint 🟢

Class method to generate the `Xbogus` parameter directly using an API endpoint.Some endpoints do not require verification.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| user_agent | str | User agent |
| endpoint | str | API endpoint |

| Return | Type | Description |
| :--- | :--- | :--- |
| final_endpoint | str | Full URL with `Xbogus` parameter |

<<< @/snippets/douyin/xbogus.py#str-2-endpoint-snippet{7-11}

### Generate Xb Parameter from API Model 🟢

Class method to generate `Xbogus` parameters using different API data models.Some endpoints do not require verification.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| user_agent | str | User agent |
| endpoint | str | API endpoint |
| params | dict | Request parameters |

| Return | Type | Description |
| :--- | :--- | :--- |
| final_endpoint | str | Full URL with `Xbogus` parameter |

To generate an API endpoint from a model, first create a model object, then call `model_2_endpoint`.

<<< @/snippets/douyin/xbogus.py#model-2-endpoint-snippet{9-13,17-19}

Data can also be collected using a web scraping engine and filters.

<<< @/snippets/douyin/xbogus.py#model-2-endpoint-2-filter-snippet{22-27}

A more advanced abstract method can directly call the handler API's `fetch_user_profile`.

### Generate Ab Parameter from API Endpoint 🟢

Class method to generate the `Ab` parameter directly using an API endpoint.Newer endpoints require verification.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| user_agent | str | User agent |
| params | str | Request parameters |
| request_type | str | Request type |

| Return | Type | Description |
| :--- | :--- | :--- |
| final_params | str | Request parameters with `Ab` parameter |

<<< @/snippets/douyin/abogus.py#str-2-endpoint-snippet{7-13}

### Generate Ab Parameters Using API Models 🟢

Class method used to generate Ab parameters using different API data models. All new APIs require validation.

| Parameter      | Type  | Description |
| :------------ | :---- | :---------- |
| user_agent    | str   | User agent  |
| base_endpoint | str   | Endpoint    |
| params        | dict  | Request parameter model |
| request_type  | str   | Request type |

| Return       | Type  | Description |
| :---------- | :---- | :---------- |
| final_params | str  | Request parameters with Ab parameters |

To generate an API endpoint using a model, first create a model object and then call the `model_2_endpoint` method.

<<< @/snippets/douyin/abogus.py#model-2-endpoint-snippet{9-14,18-20}

You can also use the crawler engine and filters to collect data.

<<< @/snippets/douyin/abogus.py#model-2-endpoint-2-filter-snippet{20-26}

A more abstract high-level method can directly call the `fetch_user_profile` handler interface.

::: tip :bulb: Tip
The UA parameter of the lite version Ab algorithm in this project is fixed:`Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0`
:::

### Extract Single User ID 🟢

Class method used to extract a single user ID.

| Parameter | Type | Description |
| :-------- | :--- | :---------- |
| url       | str  | User profile URL |

| Return      | Type | Description |
| :--------- | :--- | :---------- |
| sec_user_id | str  | User ID |

<<< @/snippets/douyin/sec-user-id.py#single-user-id-snippet{8}

### Extract List of User IDs 🟢

Class method used to extract a list of user IDs.

| Parameter | Type  | Description          |
| :-------- | :---- | :------------------- |
| urls      | list  | List of user profile URLs |

| Return       | Type  | Description  |
| :---------- | :---- | :----------- |
| sec_user_ids | list  | List of user IDs |

<<< @/snippets/douyin/sec-user-id.py#multi-user-id-snippet{15,18}

### Extract Single Post ID 🟢

Class method used to extract a single post ID.

| Parameter | Type | Description |
| :-------- | :--- | :---------- |
| url       | str  | Post URL    |

| Return    | Type | Description |
| :-------- | :--- | :---------- |
| aweme_id  | str  | Post ID     |

<<< @/snippets/douyin/aweme-id.py#single-aweme-id-snippet{9}

### Extract List of Post IDs 🟢

Class method used to extract a list of post IDs.

| Parameter | Type  | Description  |
| :-------- | :---- | :----------- |
| urls      | list  | List of post URLs |

| Return     | Type  | Description  |
| :--------- | :---- | :----------- |
| aweme_ids  | list  | List of post IDs |

<<< @/snippets/douyin/aweme-id.py#multi-aweme-id-snippet{16,19}

### Extract Single Collection ID 🟢

Class method used to extract a collection ID from a collection URL.

| Parameter | Type | Description |
| :-------- | :--- | :---------- |
| url       | str  | Collection URL |

| Return   | Type | Description |
| :------- | :--- | :---------- |
| mix_id   | str  | Collection ID |

<<< @/snippets/douyin/mix-id.py#single-mix-id-snippet{7}

### Extract List of Collection IDs 🟢

Class method used to extract collection IDs from a list of collection URLs.

| Parameter | Type  | Description  |
| :-------- | :---- | :----------- |
| urls      | list  | List of collection URLs |

| Return   | Type  | Description  |
| :------- | :---- | :----------- |
| mix_ids  | list  | List of collection IDs |

<<< @/snippets/douyin/mix-id.py#multi-mix-id-snippet{13,16}

### Extract Single Livestream Room ID 🟢

Class method used to extract a single livestream room ID.

| Parameter | Type | Description |
| :-------- | :--- | :---------- |
| url       | str  | Livestream URL |

| Return      | Type | Description  |
| :---------- | :--- | :----------- |
| webcast_id  | str  | Livestream room RID |

<<< @/snippets/douyin/webcast-id.py#single-webcast-id-snippet{7}

### Extract List of Livestream Room IDs 🟢

Class method used to extract a list of livestream room IDs.

| Parameter | Type  | Description  |
| :-------- | :---- | :----------- |
| urls      | list  | List of livestream URLs |

| Return      | Type  | Description  |
| :---------- | :---- | :----------- |
| webcast_ids | list  | List of livestream room RIDs |

<<< @/snippets/douyin/webcast-id.py#multi-webcast-id-snippet{16,19}

::: tip How to Distinguish r_id and room_id
- `r_id` is a short link identifier for a livestream room.
- `room_id` is the unique identifier for a livestream room.For example, in `https://live.douyin.com/775841227732`, `775841227732` is the `r_id`.Meanwhile, in `https://webcast.amemv.com/douyin/webcast/reflow/7318296342189919011`, `7318296342189919011` is the `room_id`.Both links point to the same livestream room.
:::

::: warning Note
Short links cannot return the `rid` using this interface.
For example, the 3rd and 4th links in `raw_urls` will only return `room_id`.To retrieve data, use the `fetch_user_live_videos_by_room_id` interface.
:::

### Global Filename Formatting 🟢

Format filenames globally according to the configuration file.

::: details :page_facing_up: Filename Formatting Rules
- `Windows` filename length limit: `255` characters (or `32,767` if long filenames are enabled).
- `Unix` filename length limit: `255` characters.
- Extracts up to `20` characters after sanitization, plus the file extension, ensuring filenames generally remain within `255` characters.
- Developers can customize the `custom_fields` parameter to define custom filenames.
:::

| Parameter       | Type  | Description                        |
| :------------- | :---- | :--------------------------------- |
| naming_template | str   | Filename template                 |
| aweme_data      | dict  | Dictionary of post data           |
| custom_fields   | dict  | User-defined fields for custom naming |

| Return     | Type | Description           |
| :--------- | :--- | :-------------------- |
| file_name  | str  | Formatted filename |

<<< @/snippets/douyin/format-file-name.py{13,18,26,30,32-35}

### Create User Directory 🟢

Used to create a user directory. If the directory already exists, it will not be created again.

::: details :open_file_folder: User Directory Structure
If the path is not specified in the configuration file, it defaults to `Download`. Both absolute and relative paths are supported.
```bash
├── Download
│   ├── douyin
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

| Parameter  | Type                 | Description            |
| :-------- | :------------------- | :--------------------- |
| kwargs    | dict                 | CLI configuration file |
| nickname  | Union[str, int]      | User nickname         |

| Return    | Type  | Description                |
| :-------- | :---- | :------------------------- |
| user_path | Path  | User directory path object |

<<< @/snippets/douyin/user-folder.py#create-user-folder{17-19}

### Rename User Directory 🟢

Used to rename a user directory.

| Parameter   | Type  | Description                        |
| :---------- | :---- | :-------------------------------- |
| old_path    | Path  | Old user directory path object   |
| new_nickname | str  | New user nickname               |

| Return    | Type  | Description                     |
| :-------- | :---- | :----------------------------- |
| new_path  | Path  | New user directory path object |

<<< @/snippets/douyin/user-folder.py#rename-user-folder{23-27,29-32}

::: tip :bulb: Note
If the directory does not exist, it will be created first before renaming.
:::

### Create or Rename User Directory 🟢

Used to create or rename a user directory. It is a combination of the two interfaces above.

| Parameter          | Type  | Description            |
| :---------------- | :---- | :--------------------- |
| kwargs            | dict  | CLI configuration file |
| local_user_data   | dict  | Local user data        |
| current_nickname  | str   | Current user nickname  |

| Return    | Type  | Description                |
| :-------- | :---- | :------------------------- |
| user_path | Path  | User directory path object |

::: tip :bulb: Note
This interface effectively solves the issue of duplicate downloads when a user changes their nickname. It is integrated into the `handler` interface, so developers only need to call the `handler` data interface.
:::

### Convert JSON Lyrics to LRC Lyrics 🟢

Used to convert Douyin's original JSON-format lyrics into LRC format.

| Parameter  | Type                     | Description                 |
| :--------- | :----------------------- | :-------------------------- |
| data       | Union[str, list, dict]   | JSON-format lyrics          |

| Return     | Type  | Description           |
| :--------- | :---- | :-------------------- |
| lrc_lines  | str   | LRC-format lyrics     |

<<< @/snippets/douyin/json-2-lrc.py{94}

## Crawler Interface List

### User Info Interface 🟢

Asynchronous method to retrieve user profile data.

| Parameter | Type        | Description     |
| :-------- | :--------- | :-------------- |
| params    | UserProfile | Request parameters |

| Return            | Type  | Description            |
| :--------------- | :---- | :--------------------- |
| _fetch_get_json() | dict  | User profile data     |

### Homepage Posts Interface 🟢

Asynchronous method to retrieve homepage post data.

| Parameter | Type       | Description       |
| :-------- | :--------- | :--------------- |
| params    | UserPost   | Request parameters |

| Return            | Type  | Description        |
| :--------------- | :---- | :----------------- |
| _fetch_get_json() | dict  | Homepage post data |

### Liked Posts Interface 🟢

Asynchronous method to retrieve liked posts data.

| Parameter | Type       | Description       |
| :-------- | :--------- | :--------------- |
| params    | UserLike   | Request parameters |

| Return            | Type  | Description       |
| :--------------- | :---- | :---------------- |
| _fetch_get_json() | dict  | Liked posts data |

### Collection Posts Interface 🟢

Asynchronous method to retrieve collection posts data.

| Parameter | Type            | Description       |
| :-------- | :-------------- | :--------------- |
| params    | UserCollection  | Request parameters |

| Return            | Type  | Description          |
| :--------------- | :---- | :------------------- |
| _fetch_post_json() | dict  | Collection post data |

### Collections Interface 🟢

Asynchronous method to retrieve collection folders data.

| Parameter | Type         | Description       |
| :-------- | :----------- | :--------------- |
| params    | UserCollects | Request parameters |

| Return            | Type  | Description        |
| :--------------- | :---- | :----------------- |
| _fetch_get_json() | dict  | Collection data   |

### Collection Videos Interface 🟢

Asynchronous method to retrieve videos within a collection.

| Parameter | Type                | Description       |
| :-------- | :------------------ | :--------------- |
| params    | UserCollectsVideo   | Request parameters |

| Return            | Type  | Description          |
| :--------------- | :---- | :------------------- |
| _fetch_get_json() | dict  | Collection video data |

### Music Collection Interface 🟢

Asynchronous method to retrieve music collection data.

| Parameter | Type                 | Description       |
| :-------- | :------------------- | :--------------- |
| params    | UserMusicCollection  | Request parameters |

| Return            | Type  | Description          |
| :--------------- | :---- | :------------------- |
| _fetch_get_json() | dict  | Music collection data |

### Mix Posts Interface 🟢

Asynchronous method to retrieve mix (album) posts data.

| Parameter | Type    | Description       |
| :-------- | :------ | :--------------- |
| params    | UserMix | Request parameters |

| Return            | Type  | Description      |
| :--------------- | :---- | :--------------- |
| _fetch_get_json() | dict  | Mix posts data   |

### Post Details Interface 🟢

Asynchronous method to retrieve post details.

| Parameter | Type        | Description       |
| :-------- | :--------- | :--------------- |
| params    | PostDetail | Request parameters |

| Return            | Type  | Description        |
| :--------------- | :---- | :----------------- |
| _fetch_get_json() | dict  | Post details data |

### Create User Directory 🟢

### Post Comments API 🟡

Asynchronous method to fetch post comment data.

| Parameter | Type       | Description       |
| :-------- | :-------- | :--------------- |
| params    | PostDetail | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | Post comment data |

### Homepage Recommended Posts API 🟡

Asynchronous method to fetch homepage recommended post data.

| Parameter | Type       | Description       |
| :-------- | :-------- | :--------------- |
| params    | PostDetail | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | Homepage recommended post data |

### Followed Posts API 🟡

Asynchronous method to fetch followed post data.

| Parameter | Type       | Description       |
| :-------- | :-------- | :--------------- |
| params    | PostDetail | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | Followed post data |

### Friends' Posts API 🟢

Asynchronous method to fetch friends' post data.

| Parameter | Type       | Description       |
| :-------- | :-------- | :--------------- |
| params    | PostDetail | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_post_json() | dict | Friends' post data |

### Recommended Posts API 🟢

Asynchronous method to fetch recommended post data.

| Parameter | Type       | Description       |
| :-------- | :-------- | :--------------- |
| params    | PostDetail | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | Recommended post data |

### Livestream Information API 🟢

Asynchronous method to fetch livestream information.

| Parameter | Type      | Description       |
| :-------- | :------- | :--------------- |
| params    | UserLive | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | Livestream information data |

### Livestream API URL (room_id) 🟢

Asynchronous method to fetch livestream API URL data.

| Parameter | Type       | Description       |
| :-------- | :-------- | :--------------- |
| params    | UserLive2 | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | Livestream API URL data |

### Followed Users' Livestream API 🟢

Asynchronous method to fetch followed users' livestream data.

| Parameter | Type                | Description       |
| :-------- | :----------------- | :--------------- |
| params    | FollowingUserLive   | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | Followed users' livestream data |

### Locate Last Post API 🟡

Asynchronous method to locate last post data.

| Parameter | Type     | Description       |
| :-------- | :------ | :--------------- |
| params    | UserPost | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | Last post data |

### User Following List API 🟢

Asynchronous method to fetch user following list data.

| Parameter | Type           | Description       |
| :-------- | :------------ | :--------------- |
| params    | UserFollowing | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | User following list data |

### User Followers List API 🟢

Asynchronous method to fetch user followers list data.

| Parameter | Type          | Description       |
| :-------- | :----------- | :--------------- |
| params    | UserFollower | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | User followers list data |

### Livestream Chat Initialization API 🟢

Asynchronous method to fetch livestream chat initialization data.

| Parameter | Type       | Description       |
| :-------- | :-------- | :--------------- |
| params    | LiveImFetch | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | Livestream chat initialization data |

### Query User API 🟢

Asynchronous method to query user data.

| Parameter | Type      | Description       |
| :-------- | :------- | :--------------- |
| params    | QueryUser | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_get_json() | dict | Queried user data |

### Post Statistics API 🟢

Asynchronous method to fetch post statistics data.

| Parameter | Type      | Description       |
| :-------- | :------- | :--------------- |
| params    | PostStats | Request parameters |

| Return       | Type  | Description       |
| :---------- | :---  | :--------------- |
| _fetch_post_json() | dict | Post statistics data |

::: tip :bulb: Tip
- When filters are not needed, you can call the `crawler` API directly, which will return the data dictionary.
:::

## dl API List

### Save Last Requested Post ID 🟢

Used to save the last requested post ID for the next homepage post request.

| Parameter    | Type  | Description  |
| :---------- | :---  | :----------- |
| sec_user_id | str   | User ID      |
| aweme_id    | str   | Post ID      |

| Return | Type | Description |
| :----- | :--- | :--------- |
| None   | None | None       |

### Filter Posts Within a Specific Date Range 🟢

Used to filter posts within a specific date range.

| Parameter   | Type                 | Description       |
| :---------- | :------------------ | :--------------- |
| aweme_data  | dict                 | Dictionary of post data |
| interval    | str                  | Date range       |

| Return               | Type                                | Description            |
| :------------------ | :-------------------------------- | :-------------------- |
| filtered_aweme_datas | Union[list[dict], dict, None]    | Filtered post data    |

### Create Download Task 🟢


### Process Download Task 🟢


### Download Original Sound 🟢


### Download Cover Image 🟢


### Download Caption 🟢


### Download Video 🟢


### Download Image Collection 🟢


### Create Original Sound Download Task 🟢


### Process Original Sound Download Task 🟢


### Create Livestream Download Task 🟢


### Livestream Download 🟢

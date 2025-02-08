---
outline: deep
---

# API Examples

This page demonstrates some of the APIs provided by `F2`.

Before using them, ensure that you have completed the `F2` configuration, [configuration file](/site-config).

### F2

For complete API examples, refer to the [`F2 Developer API`](apps/f2/overview).

::: details :link: Example: Generate Related Parameters :wrench:
> **Generate Random String**

> **Get Current Timezone Timestamp**

> **Convert Timestamp to Date String**

> **Convert Date String to Timestamp**

> **Convert Date Range to Timestamp Range**

> **Convert Timestamp Range to Date Range**
:::

::: details :link: Example: Cookie Related :cookie:
> **Split Set-Cookie**

> **Concatenate Cookies**

> **Get Cookie from a Specific Browser**
:::

::: details :link: Example: Extract Valid Links :link:
> **Extract Links**
:::

::: details :link: Example: Get File Resource Paths :file_folder:
> **Get Resource File Path**
:::

::: details :link: Example: Replace Invalid Characters :no_entry_sign:
> **Replace Invalid Characters**
:::

::: details :link: Example: Limit Filename Length Based on OS :file_folder:
> **Limit Filename Length**
:::

::: details :link: Example: Return Path Object :file_folder:
> **Return Path Object**
:::

::: details :link: Example: Check Filename Template :file_folder:
> **Check Filename Template**
:::

::: details :link: Example: Merge Configuration Files :key:
> **Merge Configuration Files**
:::

::: details :link: Example: Unescape JSON String :key:
> **Unescape JSON String**
:::

::: details :link: Example: Check Proxy Availability :spider_web:
> **Check Proxy Availability**
:::

::: details :link: Example: AES Encryption and Decryption :key:
> **AES Encryption**

> **AES Decryption**
:::

::: details :link: Example: RSA Encryption and Decryption :key:
> **RSA Encryption**

> **RSA Decryption**
:::

### Bark

For complete API examples, refer to the [`Bark Developer API`](apps/bark/overview).

::: details :link: Example: Generate Related Parameters :wrench:
> **Generate Digital Bits**

<<< @/snippets/bark/generate-bytes.py{7}
:::

::: details :link: Example: Send Notification :bell:
<<< @/snippets/bark/notification.py{15}
:::

### Douyin

For complete API examples, refer to the [`Douyin Developer API`](apps/douyin/overview).

::: details :link: Example: Generate Related Parameters :wrench:
> **Generate Abogus Parameters**

<<< @/snippets/douyin/abogus.py#str-2-endpoint-snippet{9-13}

> **Generate Xbogus Parameters**

<<< @/snippets/douyin/xbogus.py#str-2-endpoint-snippet{8-11}

> **Generate Danmaku Signature Parameters**

<<< @/snippets/douyin/webcast-signature.py#webcast-signature-snippet{7-10}

> **msToken Related**

<<< @/snippets/douyin/token-manager.py#mstoken-real-sinppest{4}
---
<<< @/snippets/douyin/token-manager.py#mstoken-false-sinppest{4}

> **ttwid**

<<< @/snippets/douyin/token-manager.py#ttwid-sinppest{4}

> **webid**

<<< @/snippets/douyin/token-manager.py#webid-sinppest{4}

> **verify_fp**

<<< @/snippets/douyin/token-manager.py#verify_fp-sinppest{4}

> **s_v_web_id**

<<< @/snippets/douyin/token-manager.py#s-v-web-id-sinppest{4}
:::

::: details :link: Example: Batch Extract User SecUid
<<< @/snippets/douyin/sec-user-id.py#multi-user-id-snippet{15,18}
:::

::: details :link: Example: Batch Extract AwemeId
<<< @/snippets/douyin/aweme-id.py#multi-aweme-id-snippet{16,19}
:::

::: details :link: Example: Batch Extract Webcast ID :game_die:
<<< @/snippets/douyin/webcast-id.py#multi-webcast-id-snippet{16,19}
:::

::: details :link: Example: Batch Extract Mix ID :package:
<<< @/snippets/douyin/mix-id.py#multi-mix-id-snippet{13,16}
:::

::: details :link: Example: Get User Profile :people_holding_hands:
<<< @/snippets/douyin/user-profile.py#user-profile-snippet{16}
:::

::: details :link: Example: Get User Posts :clapper:
<<< @/snippets/douyin/user-post.py{18-20}
:::

::: details :link: Example: Get User Live Stream :tv:
<<< @/snippets/douyin/user-live.py{15}
:::

::: details :link: Example: Get User Followers :busts_in_silhouette:
<<< @/snippets/douyin/user-follower.py{25-30}
:::

### Tiktok

For complete API examples, refer to the [`Tiktok Developer API`](apps/tiktok/overview).

::: details :link: Example: Generate Related Parameters :wrench:
> **Generate Xbogus Parameters**

<<< @/snippets/tiktok/xbogus.py#str-2-endpoint-snippet{8-11}

> **msToken Related**

<<< @/snippets/tiktok/token-manager.py#mstoken-real-sinppest{4}
---
<<< @/snippets/tiktok/token-manager.py#mstoken-false-sinppest{4}

> **ttwid**

<<< @/snippets/tiktok/token-manager.py#ttwid-sinppest{4}

> **odin_tt**

<<< @/snippets/tiktok/token-manager.py#odin_tt-sinppest{4}
:::

::: details :link: Example: Batch Extract User SecUid
<<< @/snippets/tiktok/sec-uid.py#multi-uid-snippet{15,18}
:::

::: details :link: Example: Batch Extract AwemeId
<<< @/snippets/tiktok/aweme-id.py#multi-aweme-id-snippet{16,19}
:::

::: details :link: Example: Get User Profile :people_holding_hands:
<<< @/snippets/tiktok/user-profile.py#user-profile-snippet{16}
:::

::: details :link: Example: Get User Posts :clapper:
<<< @/snippets/tiktok/user-post.py{18-20}
:::

::: details :link: Example: Get User Collected Posts :bookmark:
<<< @/snippets/tiktok/user-collect.py{21-23}
:::

### Twitter

For complete API examples, refer to the [`Twitter Developer API`](apps/twitter/overview).

::: details :link: Example: Batch Extract User Unique IDs :blue_book:
<<< @/snippets/twitter/user-unique-ids.py#multi-user-unique-id-snippet{18}
:::

::: details :link: Example: Batch Extract Tweet IDs :tada:
<<< @/snippets/twitter/tweet-ids.py#multi-tweet-id-snippet{19}
:::

::: details :link: Example: Get User Profile :people_holding_hands:
<<< @/snippets/twitter/user-profile.py#user-profile-snippet{18}
:::

::: details :link: Example: Get User Tweets :clapper:
<<< @/snippets/twitter/user-tweet.py{18-23}
:::

::: details :link: Example: Get User Liked Tweets :heart:
<<< @/snippets/twitter/user-like.py{17-22}
:::

::: details :link: Example: Get User Bookmarked Tweets :bookmark:
<<< @/snippets/twitter/user-bookmark.py{17-21}
:::

### Weibo

For complete API examples, refer to the [`Weibo Developer API`](apps/weibo/overview).

::: details :link: Example: Generate Related Parameters :wrench:
> **Generate Visitor Cookie**

<<< @/snippets/weibo/visitor-cookie.py{7}
:::

::: details :link: Example: Batch Extract User Unique IDs :blue_book:
<<< @/snippets/weibo/weibo-uid.py#multi-weibo-uid-snippet{27,30}
:::

::: details :link: Example: Batch Extract User Screen Names :calling:
<<< @/snippets/weibo/weibo-screen-name.py#multi-weibo-screen_name-snippet{20,23}
:::

::: details :link: Example: Batch Extract Weibo IDs :tada:
<<< @/snippets/weibo/weibo-id.py#multi-weibo-id-snippet{19,22}
:::

::: details :link: Example: Get User Profile :people_holding_hands:
<<< @/snippets/weibo/user-profile.py#user-profile-snippet{17}
:::

::: details :link: Example: Get User Weibo Posts :clapper:
<<< @/snippets/weibo/user-weibo.py{17-23}
:::

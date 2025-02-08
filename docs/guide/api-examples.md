---
outline: deep
---

# API 示例

本页演示了 `F2` 提供的一些 `API` 的用法。

使用前请先确保完成了 `F2` 配置，[配置文件](/site-config)。

### F2

完整的 `API` 示例请参考 [`F2开发者接口`](apps/f2/overview)。

::: details :link: 示例：生成相关参数 :wrench:
> **生成随机字符串**

> **获取当前时区时间戳**

> **时间戳转换为日期字符串**

> **日期字符串转换为时间戳**

> **日期区间转换为时间戳区间**

> **时间戳区间转换为日期区间**
:::

::: details :link: 示例：Cookie相关 :cookie:
> **拆分Set-Cookie**

> **拼接Cookie**

> **指定浏览器获取Cookie**
:::

::: details :link: 示例：提取有效链接 :link:
> **提取链接**
:::

::: details :link: 示例：获取包资源文件路径 :file_folder:
> **获取资源文件路径**
:::

::: details :link: 示例：替换非法字符 :no_entry_sign:
> **替换非法字符**
:::

::: details :link: 示例：根据操作系统限制文件名长度 :file_folder:
> **限制文件名长度**
:::

::: details :link: 示例：返回Path对象 :file_folder:
> **返回Path对象**
:::

::: details :link: 示例：检查文件名模板 :file_folder:
> **检查文件名模板**
:::

::: details :link: 示例：合并配置文件 :key:
> **合并配置文件**
:::

::: details :link: 示例：反转义JSON字符串 :key:
> **反转义JSON字符串**
:::

::: details :link: 示例：检查代理是否可用 :spider_web:
> **检查代理是否可用**
:::

::: details :link: 示例：AES加密解密 :key:
> **AES加密**

> **AES解密**
:::

::: details :link: 示例：RSA加密解密 :key:
> **RSA加密**

> **RSA解密**
:::

### Bark

完整的 `API` 示例请参考 [`Bark开发者接口`](apps/bark/overview)。

::: details :link: 示例：生成相关参数 :wrench:
> **生成数字比特**

<<< @/snippets/bark/generate-bytes.py{7}
:::

::: details :link: 示例：发送通知 :bell:
<<< @/snippets/bark/notification.py{15}
:::

### Douyin

完整的 `API` 示例请参考 [`Douyin开发者接口`](apps/douyin/overview)。

::: details :link: 示例：生成相关参数 :wrench:
> **生成Abogus参数**

<<< @/snippets/douyin/abogus.py#str-2-endpoint-snippet{9-13}

> **生成Xbogus参数**

<<< @/snippets/douyin/xbogus.py#str-2-endpoint-snippet{8-11}

> **生成弹幕signature参数**

<<< @/snippets/douyin/webcast-signature.py#webcast-signature-snippet{7-10}

> **msToken相关**

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

::: details :link: 示例：批量提取用户SecUid
<<< @/snippets/douyin/sec-user-id.py#multi-user-id-snippet{15,18}
:::

::: details :link: 示例：批量提取作品AwemeId
<<< @/snippets/douyin/aweme-id.py#multi-aweme-id-snippet{16,19}
:::

::: details :link: 示例：批量提取直播id :game_die:
<<< @/snippets/douyin/webcast-id.py#multi-webcast-id-snippet{16,19}
:::

::: details :link: 示例：批量提取合集id :package:
<<< @/snippets/douyin/mix-id.py#multi-mix-id-snippet{13,16}
:::

::: details :link: 示例：获取用户概况 :people_holding_hands:
<<< @/snippets/douyin/user-profile.py#user-profile-snippet{16}
:::

::: details :link: 示例：获取用户作品 :clapper:
<<< @/snippets/douyin/user-post.py{18-20}
:::

::: details :link: 示例：获取用户直播 :tv:
<<< @/snippets/douyin/user-live.py{15}
:::

::: details :link: 示例：获取用户粉丝 :busts_in_silhouette:
<<< @/snippets/douyin/user-follower.py{25-30}
:::

### Tiktok

完整的 `API` 示例请参考 [`Tiktok开发者接口`](apps/tiktok/overview)。

::: details :link: 示例：生成相关参数 :wrench:
> **生成Xbogus参数**

<<< @/snippets/tiktok/xbogus.py#str-2-endpoint-snippet{8-11}

> **msToken相关**

<<< @/snippets/tiktok/token-manager.py#mstoken-real-sinppest{4}
---
<<< @/snippets/tiktok/token-manager.py#mstoken-false-sinppest{4}

> **ttwid**

<<< @/snippets/tiktok/token-manager.py#ttwid-sinppest{4}

> **odin_tt**

<<< @/snippets/tiktok/token-manager.py#odin_tt-sinppest{4}
:::

::: details :link: 示例：批量提取用户SecUid
<<< @/snippets/tiktok/sec-uid.py#multi-uid-snippet{15,18}
:::

::: details :link: 示例：批量提取作品AwemeId
<<< @/snippets/tiktok/aweme-id.py#multi-aweme-id-snippet{16,19}
:::

::: details :link: 示例：获取用户概况 :people_holding_hands:
<<< @/snippets/tiktok/user-profile.py#user-profile-snippet{16}
:::

::: details :link: 示例：获取用户作品 :clapper:
<<< @/snippets/tiktok/user-post.py{18-20}
:::

::: details :link: 示例：获取用户收藏作品 :bookmark:
<<< @/snippets/tiktok/user-collect.py{21-23}
:::

### Twitter

完整的 `API` 示例请参考 [`Twitter开发者接口`](apps/twitter/overview)。

::: details :link: 示例：批量提取用户唯一id :blue_book:
<<< @/snippets/twitter/user-unique-ids.py#multi-user-unique-id-snippet{18}
:::

::: details :link: 示例：批量提取推文id :tada:
<<< @/snippets/twitter/tweet-ids.py#multi-tweet-id-snippet{19}
:::

::: details :link: 示例：获取用户概况 :people_holding_hands:
<<< @/snippets/twitter/user-profile.py#user-profile-snippet{18}
:::

::: details :link: 示例：获取用户推文 :clapper:
<<< @/snippets/twitter/user-tweet.py{18-23}
:::

::: details :link: 示例：获取用户喜欢推文 :heart:
<<< @/snippets/twitter/user-like.py{17-22}
:::

::: details :link: 示例：获取用户收藏推文 :bookmark:
<<< @/snippets/twitter/user-bookmark.py{17-21}
:::

### Weibo

完整的 `API` 示例请参考 [`Weibo开发者接口`](apps/weibo/overview)。

::: details :link: 示例：生成相关参数 :wrench:
> **生成游客Cookie**

<<< @/snippets/weibo/visitor-cookie.py{7}
:::

::: details :link: 示例：批量提取用户唯一id :blue_book:
<<< @/snippets/weibo/weibo-uid.py#multi-weibo-uid-snippet{27,30}
:::

::: details :link: 示例：批量提取用户昵称 :calling:
<<< @/snippets/weibo/weibo-screen-name.py#multi-weibo-screen_name-snippet{20,23}
:::

::: details :link: 示例：批量提取微博id :tada:
<<< @/snippets/weibo/weibo-id.py#multi-weibo-id-snippet{19,22}
:::

::: details :link: 示例：获取用户概况 :people_holding_hands:
<<< @/snippets/weibo/user-profile.py#user-profile-snippet{17}
:::

::: details :link: 示例：获取用户微博 :clapper:
<<< @/snippets/weibo/user-weibo.py{17-23}
:::

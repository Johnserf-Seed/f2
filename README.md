
<p align="center">
  <img src="https://github.com/Johnserf-Seed/f2/raw/main/docs/public/f2-logo-with-shadow-svg@0.5x.svg" alt="Logo">
</p>

[![Downloads](https://pepy.tech/badge/f2/month)](https://pepy.tech/project/f2)
[![PyPI version](https://badge.fury.io/py/f2.svg)](https://badge.fury.io/py/f2)
[![Dev Branch](https://badgen.net/badge/branch/v0.0.1.6-pw2/blue)](https://github.com/Johnserf-Seed/f2/tree/v0.0.1.6-pw2)
[![Discord](https://img.shields.io/discord/1146473603450282004?label=Discord)](https://discord.gg/3PhtPmgHf8)
[![codecov](https://codecov.io/gh/Johnserf-Seed/f2/graph/badge.svg?token=T9DH4QPZSS)](https://codecov.io/gh/Johnserf-Seed/f2)
[![TikHub](https://img.shields.io/badge/%E8%B5%9E%E5%8A%A9%E5%95%86-TikHub-orange?style=flat-square&logo=tiktok)](https://beta-web.tikhub.io/users/signup?referral_code=6hLcGD94)
[![APACHE-2.0](https://img.shields.io/github/license/johnserf-seed/f2)](https://github.com/Johnserf-Seed/f2/blob/main/LICENSE)


[简体中文 readme](https://github.com/Johnserf-Seed/f2/blob/main/README.md)
 • [English readme](https://github.com/Johnserf-Seed/f2/blob/main/README.en.md)


`F2` 是一个 [`Python` 库](https://pypi.org/project/f2/)，提供多平台的作品下载与接口数据处理。支持`抖音`、`TikTok`、`Twitter`、`Instagram`等平台，且方便适配更多平台。

<img src='https://github.com/Johnserf-Seed/f2/assets/40727745/82644596-7eca-48ec-91b0-3c5e4c24ee90'>

## 🚀 快速开始

### ⚙️ 安装

- [必备条件](https://f2.wiki/install#%E5%BF%85%E5%A4%87%E6%9D%A1%E4%BB%B6)
- [包管理器安装](https://f2.wiki/install#%E5%8C%85%E7%AE%A1%E7%90%86%E5%99%A8%E5%AE%89%E8%A3%85)
- [编译安装](https://f2.wiki/install#%E7%BC%96%E8%AF%91%E5%AE%89%E8%A3%85)

### ⚡ 快速使用

- [启动和运行](https://f2.wiki/quick-start#%E5%90%AF%E5%8A%A8%E5%92%8C%E8%BF%90%E8%A1%8C)

### 📋 配置文件

- [主配置文件（高频）](https://f2.wiki/site-config#%E4%B8%BB%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6)
- [初始化配置文件](https://f2.wiki/site-config#%E5%88%9D%E5%A7%8B%E5%8C%96%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6)
- [自定义配置文件](https://f2.wiki/site-config#%E8%87%AA%E5%AE%9A%E4%B9%89%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6)
- [配置Cookie](https://f2.wiki/site-config#%E9%85%8D%E7%BD%AECookie)
- [配置文件的位置](https://f2.wiki/site-config#%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E7%9A%84%E4%BD%8D%E7%BD%AE)

### 💻 命令行

- [CLI临时配置](https://f2.wiki/cli#cli%E4%B8%B4%E6%97%B6%E9%85%8D%E7%BD%AE)

### 📘 开发指南

- [开发者必看](https://f2.wiki/guide/what-is-f2)

### 🧩 调用示例

- [DouYin](https://f2.wiki/guide/apps/douyin/)

- [TikTok](https://f2.wiki/guide/apps/tiktok/)


## ✨ 新变化

当下载或升级到`F2`的不同版本时，请注意以下关键的版本更新。

<details>
  <summary> 📡 v0.0.1.6-pw2 </summary>

  - 配置文件格式已经更新，如果你使用了旧的配置文件，请注意迁移。
  - 所有时间戳的默认时区为（`UTC/GMT+08:00`）。
  - `douyin`直播流文件名调整为`flv`，图集调整回`webp`。
  - `tiktok`视频地址`403`的错误已经修复。[TikTok视频地址403解决办法](https://f2.wiki/question-answer/qa#tiktok-403-forbidden)
  - 现在`douyin`默认会使用`ab`算法来请求。（满血版ab算法待时开源）。
  - 更多变化查看[ChangeLog](https://github.com/Johnserf-Seed/f2/blob/main/CHANGELOG.md#0016---2024-05-04)。
</details>

<details>
  <summary> 📡 v0.0.1.5-pw2 </summary>

  - `0.0.1.5`的`XBogus`参数支持了自定义UA，请注意UA规范。
  - 重建的数据库包含接口的原始数据，所以你需要删除旧的数据库文件。如果你想保留记录请注意迁移。
  - 所有的`fetch`方法返回的类型已统一为过滤器类型，所以你需要注意这个变化。
  - 过滤器添加了`_to_raw`方法，可以将过滤器转换为原始接口数据。
  - 文件名模板已经更新，如果你的文件名不符合规范，将会抛出异常。
  - `douyin`合集页链接无法解析的查看[抖音合集作品](#抖音合集作品)。
  - 更多变化查看[ChangeLog](https://github.com/Johnserf-Seed/f2/blob/main/CHANGELOG.md#0015---2024-04-04)。
</details>


## 📑 文档

`F2`的目标是提供一个简单易用的接口，让用户可以快速获取作品数据。
在`preview`版本中很多功能没有完善，如果你发现了问题，请在`F2`项目中提交`issue`。[项目文档](https://f2.wiki/)还在完善中，存在滞后的情况，请保持关注。


## 🛠️ Q&A

[常见的问题与解决办法](https://f2.wiki/question-answer/qa)


## 🗓️ Todo

- 将在`0.0.1.7`版本中添加本地转发功能。
- 将在`0.0.1.7`版本中添加更多`douyin`，`tiktok`，`weibo`，`x`的接口。
- 将在`0.0.1.7`版本中修复`x`已知的问题。


## 🐛 更新

[ChangeLog](https://github.com/Johnserf-Seed/f2/blob/main/CHANGELOG.md)


## 💡 应用&功能

功能状态：🟢代表已经实现，🟡代表正在实现，🟤代表暂时不实现，🔵代表未来实现，🔴代表将会弃用。
账号状态：⚪代表未知，🟣代表需要登录（无视自己账号隐私设置），⚫代表不需要登录（游客状态能看到的）。

<details>
  <summary> 🎶 DouYin </summary>

  - 🟣 表示需要登录才可以下载仅自己可见的作品、收藏作品、收藏夹作品或点赞作品等。（登录后无视自己的私密设置、可获取个性化内容）
  - ⚫ 表示不需要登录下载公开的作品、收藏夹作品、点赞作品等。（仅下载他人公开可见作品与页面）

  |功能|账号状态|接口|功能状态|
  |---|---|---|---|
  |用户信息|🟣⚫|`fetch_user_profile`|🟢|
  |单个作品（视频、图集、日常）|🟣⚫|`fetch_one_video`|🟢|
  |主页作品|🟣⚫|`fetch_user_post_videos`|🟢|
  |点赞作品|🟣⚫|`fetch_user_like_videos`|🟢|
  |收藏夹作品|🟣⚫|`fetch_user_collects_videos`|🟢|
  |收藏作品|🟣|`fetch_user_collection_videos`|🟢|
  |收藏原声|🟣|`fetch_user_music_collection`|🟢|
  |收藏合集|🟣|`fetch_user_mix_collection`|🔵|
  |收藏短剧|🟣|`fetch_user_series_collection`|🟤|
  |合集作品|⚫|`fetch_user_mix_videos`|🟢|
  |首页推荐作品|🟣⚫|`fetch_user_feed_videos`|🟢|
  |相似推荐作品|⚫|`fetch_related_videos`|🟢|
  |直播间信息（流下载）|⚫|`fetch_user_live_videos`、`fetch_user_live_videos_by_room_id`|🟢|
  |直播间弹幕负载|⚫|`fetch_live_im`|🟢|
  |直播间弹幕|⚫|`fetch_user_live_danmu`|🟢|
  |关注用户开播|🟣⚫|`fetch_user_following_lives`|🟢|
  |关注用户信息|🟣⚫|`fetch_user_following`|🟢|
  |粉丝用户信息|🟣⚫|`fetch_user_follower`|🟢|
  |关注用户作品|🟣⚫|`fetch_user_following_videos`|🟤|
  |粉丝用户作品|🟣⚫|`fetch_user_follower_videos`|🟤|
  |朋友作品|🟣|`fetch_friend_feed_videos`|🟢|
  |搜索视频|⚫|`fetch_search_videos`|🔵|
  |搜索用户|⚫|`fetch_search_users`|🔵|
  |搜索直播|⚫|`fetch_search_lives`|🔵|
  |猜你想搜（相关搜索）|⚫|`fetch_search_suggest`|🟤|
  |抖音热点|⚫|`fetch_hot_search`|🟤|
  |作品评论|🟣⚫|`fetch_video_comments`|🔵|
  |观看历史|🟣|`fetch_user_history_read`|🟤|
  |稍后再看|🟣|`fetch_user_watch_later`|🟤|
  |...|...|...|...|

  |工具类|类名|接口|功能状态|
  |---|---|---|---|
  | 管理客户端配置     | `ClientConfManager`   |                  |  🟢  |
  | 生成真实msToken    | `TokenManager`     | `gen_real_msToken`       |  🟢  |
  | 生成虚假msToken     | `TokenManager`     | `gen_false_msToken`      |  🟢  |
  | 生成ttwid          | `TokenManager`     | `gen_ttwid`              |  🟢  |
  | 生成webid          | `TokenManager`     | `gen_webid`              |  🟢  |
  | 生成verify_fp      | `VerifyFpManager`  | `gen_verify_fp`          |  🟢  |
  | 生成s_v_web_id     | `VerifyFpManager`  | `gen_s_v_web_id`         |  🟢  |
  | 生成直播signature | `DouyinWebcastSignature` | `get_signature` |  🟢  |
  | 使用接口模型生成直播wss签名参数 | `WebcastSignatureManager` | `model_2_endpoint` |  🟢  |
  | 使用接口地址生成Xb参数      | `XBogusManager`    | `str_2_endpoint`   |  🟢  |
  | 使用接口模型生成Xb参数      | `XBogusManager`    | `model_2_endpoint`   |  🟢  |
  | 使用接口地址生成Ab参数      | `ABogusManager`    | `str_2_endpoint`   |  🟢  |
  | 使用接口模型生成Ab参数      | `ABogusManager`    | `model_2_endpoint`   |  🟢  |
  | 提取单个用户id       | `SecUserIdFetcher` | `get_sec_user_id`         |  🟢  |
  | 提取列表用户id       | `SecUserIdFetcher` | `get_all_sec_user_id`     |  🟢  |
  | 提取单个作品id       | `AwemeIdFetcher`   | `get_aweme_id`            |  🟢  |
  | 提取列表作品id       | `AwemeIdFetcher`   | `get_all_aweme_id`        |  🟢  |
  | 提取单个合集id       | `MixIdFetcher`     | `get_mix_id`              |  🟢  |
  | 提取列表合集id       | `MixIdFetcher`     | `get_all_mix_id`          |  🟢  |
  | 提取单个直播间号      | `WebCastIdFetcher` | `get_webcast_id`          |  🟢  |
  | 提取列表直播间号       | `WebCastIdFetcher` | `get_all_webcast_id`      |  🟢  |
 </details>

<details>
  <summary> 🎶 TikTok </summary>

  - 🟣 表示需要登录才可以下载仅自己可见的作品、收藏作品、收藏夹作品或点赞作品等。（登录后无视自己的私密设置、可获取个性化内容）
  - ⚫ 表示不需要登录下载公开的作品、收藏夹作品、点赞作品等。（仅下载他人公开可见作品与页面）

  |功能|账号状态|接口|功能状态|
  |---|---|---|---|
  |用户信息|🟣⚫|`fetch_user_profile`|🟢|
  |单个作品|🟣⚫|`fetch_one_video`|🟢|
  |主页作品|🟣⚫|`fetch_user_post_videos`|🟢|
  |点赞作品|🟣⚫|`fetch_user_like_videos`|🟢|
  |收藏作品|🟣⚫|`fetch_user_collect_videos`|🟢|
  |播放列表|🟣⚫|`fetch_play_list`|🟢|
  |播放列表作品|🟣⚫|`fetch_user_mix_videos`|🟢|
  |作品搜索|🟣⚫|`fetch_search_videos`|🟢|
  |直播间信息（流下载）|⚫|`fetch_user_live_videos`|🟢|
  |检查开播|🟣⚫|`fetch_check_live_alive`|🟢|
  |...|...|...|...|
 </details>


## 📸 截图

<details>
  <summary> 🎬 DouYin </summary>

  ### 抖音单个作品

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/3e7c685e-0a0e-4d3a-a605-56eccb71c467'>

  ### 抖音主页作品

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/0743627d-4f03-43c9-94f0-653903382685'>

  ### 抖音点赞作品

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/95c588f7-45ab-4713-8102-7cd84452c0b8'>

  ### 抖音收藏作品

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/66951156-43df-4152-9b0c-4ee4f58a1e38'>

  ### 抖音收藏夹作品

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/37e2354b-3548-4ade-afa4-f8bb8108c565'>

  ### 抖音收藏原声

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/e0837eff-a7c2-4e6e-99fb-71e85ace83dc'>

  ### 抖音合集作品

  支持合集里任意作品链接解析
  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/fa79c123-2552-49ed-b37f-0931489dcdad'>

  合集链接解析
  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/1dd41daa-f375-448f-a3aa-55c14eb28d2c'>

  ### 抖音直播录制

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/c5276410-89aa-4bed-99f0-1dcf9c34cd4f'>

  ### 抖音相关推荐

  <img src="https://github.com/Johnserf-Seed/f2/assets/40727745/e36fb510-39ef-486e-b944-7dbf8cf25c36">

  ### 抖音好友作品

  <img src="https://github.com/Johnserf-Seed/f2/assets/40727745/437fa0ad-9524-4674-9d73-56db815113ef">

  ### 抖音直播弹幕

  https://github.com/Johnserf-Seed/f2/assets/40727745/500d1eaf-59ba-44ba-849b-666c0ddf8469

</details>

<details>
  <summary> 🎬 TikTok </summary>

  ### TikTok单个作品

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/34758692-203d-4982-8c08-9efc70acee4e'>

  ### TikTok主页作品

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/ddeae039-502d-4390-b35b-23147210707b'>

  ### TikTok点赞作品

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/230e1443-2fa3-47a8-aaeb-4ad0977e6291'>

  ### TikTok收藏作品

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/7594e664-2f24-4e82-8e8a-ed872cc4e483'>

  ### TikTok播放列表作品

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/653d33cc-ba7f-4abf-8f6f-7c3f5a0b3cd1'>

  ### TikTok作品搜索
  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/091e66d5-f123-4883-9360-db3dad359d7d'>

 </details>


## 📦 结构

<details>
  <summary>📁 项目目录</summary>

  ```bash
  .
  ├── CHANGELOG.md
  ├── CODE_OF_CONDUCT.md
  ├── CONTRIBUTING.md
  ├── CONTRIBUTORS.md
  ├── LICENSE
  ├── README.en.md
  ├── README.md
  ├── SECURITY.md
  ├── babel.cfg
  ├── coverage.xml
  ├── docs
  │   ├── advance-guide.md
  │   ├── cli.md
  │   ├── en
  │   │   ├── advance-guide.md
  │   │   ├── api-examples.md
  │   │   ├── cli.md
  │   │   ├── guide
  │   │   │   └── what-is-f2.md
  │   │   ├── index.md
  │   │   ├── install.md
  │   │   ├── markdown-examples.md
  │   │   ├── quick-start.md
  │   │   └── site-config.md
  │   ├── guide
  │   │   ├── api-examples.md
  │   │   ├── apps
  │   │   │   ├── douyin
  │   │   │   │   └── index.md
  │   │   │   ├── tiktok
  │   │   │   │   └── index.md
  │   │   │   ├── weibo
  │   │   │   │   └── index.md
  │   │   │   └── x
  │   │   │       └── index.md
  │   │   └── what-is-f2.md
  │   ├── index.md
  │   ├── package-lock.json
  │   ├── package.json
  │   ├── public
  │   │   ├── douyin
  │   │   │   ├── cli-start-2.png
  │   │   │   ├── cli-start.png
  │   │   │   ├── code-start-2.png
  │   │   │   ├── code-start.png
  │   │   │   ├── log-2-console.png
  │   │   │   ├── pytest-ok.png
  │   │   │   └── set-debug.png
  │   │   ├── f2-help.png
  │   │   ├── f2-logo-with-no-shadow.png
  │   │   ├── f2-logo-with-shadow-mini.png
  │   │   ├── f2-logo-with-shadow-svg@0.25x.svg
  │   │   ├── f2-logo-with-shadow-svg@0.5x.svg
  │   │   ├── f2-logo-with-shadow-svg@0.75x.svg
  │   │   ├── f2-logo-with-shadow-svg@1.0x.svg
  │   │   ├── f2-logo-with-shadow-svg@1.5x.svg
  │   │   ├── f2-logo-with-shadow-svg@2.0x.svg
  │   │   ├── f2-logo-with-shadow.png
  │   │   └── f2-logo.ico
  │   ├── question-answer
  │   │   └── qa.md
  │   ├── quick-start.md
  │   ├── reference
  │   │   └── runtime-api.md
  │   ├── site-config.md
  │   ├── snippets
  │   │   ├── QA.md
  │   │   ├── douyin
  │   │   │   ├── abogus.py
  │   │   │   ├── aweme-id.py
  │   │   │   ├── aweme-related.py
  │   │   │   ├── client-config.py
  │   │   │   ├── format-file-name.py
  │   │   │   ├── json-2-lrc.py
  │   │   │   ├── mix-id.py
  │   │   │   ├── mstoken-false.py
  │   │   │   ├── mstoken-real.py
  │   │   │   ├── one-video.py
  │   │   │   ├── query-user.py
  │   │   │   ├── s_v_web_id.py
  │   │   │   ├── sec-user-id.py
  │   │   │   ├── show-qrcode.py
  │   │   │   ├── sso-login.py
  │   │   │   ├── support-link.md
  │   │   │   ├── ttwid.py
  │   │   │   ├── user-collection.py
  │   │   │   ├── user-collects.py
  │   │   │   ├── user-feed.py
  │   │   │   ├── user-folder.py
  │   │   │   ├── user-follow-live.py
  │   │   │   ├── user-follower.py
  │   │   │   ├── user-following.py
  │   │   │   ├── user-friend.py
  │   │   │   ├── user-get-add.py
  │   │   │   ├── user-like.py
  │   │   │   ├── user-live-im-fetch.py
  │   │   │   ├── user-live-room-id.py
  │   │   │   ├── user-live.py
  │   │   │   ├── user-mix.py
  │   │   │   ├── user-post.py
  │   │   │   ├── user-profile.py
  │   │   │   ├── verify_fp.py
  │   │   │   ├── video-get-add.py
  │   │   │   ├── webcast-id.py
  │   │   │   ├── webcast-signature.py
  │   │   │   ├── webid.py
  │   │   │   └── xbogus.py
  │   │   ├── set-debug.py
  │   │   ├── tiktok
  │   │   │   ├── aweme-id.py
  │   │   │   ├── check-live-alive.py
  │   │   │   ├── client-config.py
  │   │   │   ├── device-id.py
  │   │   │   ├── format-file-name.py
  │   │   │   ├── one-video.py
  │   │   │   ├── sec-uid.py
  │   │   │   ├── support-link.md
  │   │   │   ├── token-manager.py
  │   │   │   ├── unique-id.py
  │   │   │   ├── user-collect.py
  │   │   │   ├── user-folder.py
  │   │   │   ├── user-get-add.py
  │   │   │   ├── user-like.py
  │   │   │   ├── user-mix.py
  │   │   │   ├── user-playlist.py
  │   │   │   ├── user-post.py
  │   │   │   ├── user-profile.py
  │   │   │   ├── video-get-add.py
  │   │   │   └── xbogus.py
  │   │   ├── twitter
  │   │   └── weibo
  │   │       ├── user-profile.py
  │   │       └── user-weibo.py
  │   └── vite-.zip
  ├── f2
  │   ├── __init__.py
  │   ├── __main__.py
  │   ├── apps
  │   │   ├── __apps__.py
  │   │   ├── __init__.py
  │   │   ├── douyin
  │   │   │   ├── algorithm
  │   │   │   │   ├── webcast_signature.js
  │   │   │   │   └── webcast_signature.py
  │   │   │   ├── api.py
  │   │   │   ├── cli.py
  │   │   │   ├── crawler.py
  │   │   │   ├── db.py
  │   │   │   ├── dl.py
  │   │   │   ├── filter.py
  │   │   │   ├── handler.py
  │   │   │   ├── help.py
  │   │   │   ├── model.py
  │   │   │   ├── proto
  │   │   │   │   ├── douyin_webcast.proto
  │   │   │   │   └── douyin_webcast_pb2.py
  │   │   │   ├── test
  │   │   │   │   ├── test_douyin_apps_model.py
  │   │   │   │   ├── test_douyin_aweme_id.py
  │   │   │   │   ├── test_douyin_crawler.py
  │   │   │   │   ├── test_douyin_handler.py
  │   │   │   │   ├── test_douyin_lrc.py
  │   │   │   │   ├── test_douyin_room_id.py
  │   │   │   │   ├── test_douyin_sec_user_id.py
  │   │   │   │   ├── test_douyin_token.py
  │   │   │   │   ├── test_douyin_webcast_id.py
  │   │   │   │   └── test_douyin_webcast_signature.py
  │   │   │   └── utils.py
  │   │   ├── tiktok
  │   │   │   ├── api.py
  │   │   │   ├── cli.py
  │   │   │   ├── crawler.py
  │   │   │   ├── db.py
  │   │   │   ├── dl.py
  │   │   │   ├── filter.py
  │   │   │   ├── handler.py
  │   │   │   ├── help.py
  │   │   │   ├── model.py
  │   │   │   ├── test
  │   │   │   │   ├── test_tiktok_crawler.py
  │   │   │   │   ├── test_tiktok_device_id.py
  │   │   │   │   └── test_tiktok_token.py
  │   │   │   └── utils.py
  │   │   ├── twitter
  │   │   │   ├── api.py
  │   │   │   ├── cli.py
  │   │   │   ├── crawler.py
  │   │   │   ├── db.py
  │   │   │   ├── dl.py
  │   │   │   ├── filter.py
  │   │   │   ├── handler.py
  │   │   │   ├── help.py
  │   │   │   ├── model.py
  │   │   │   ├── test
  │   │   │   │   ├── test_model.py
  │   │   │   │   ├── test_tweet_id.py
  │   │   │   │   └── ttt.py
  │   │   │   └── utils.py
  │   │   └── weibo
  │   │       ├── api.py
  │   │       ├── cli.py
  │   │       ├── crawler.py
  │   │       ├── db.py
  │   │       ├── dl.py
  │   │       ├── filter.py
  │   │       ├── handler.py
  │   │       ├── help.py
  │   │       ├── model.py
  │   │       ├── test
  │   │       │   ├── test_gen_visitor.py
  │   │       │   ├── test_handler.py
  │   │       │   ├── test_weibo_id.py
  │   │       │   └── test_weibo_uid.py
  │   │       └── utils.py
  │   ├── cli
  │   │   ├── __init__.py
  │   │   ├── cli_commands.py
  │   │   └── cli_console.py
  │   ├── conf
  │   │   ├── app.yaml
  │   │   ├── conf.yaml
  │   │   ├── defaults.yaml
  │   │   └── test.yaml
  │   ├── crawlers
  │   │   └── base_crawler.py
  │   ├── db
  │   │   └── base_db.py
  │   ├── dl
  │   │   └── base_downloader.py
  │   ├── exceptions
  │   │   ├── __init__.py
  │   │   ├── api_exceptions.py
  │   │   ├── db_exceptions.py
  │   │   └── file_exceptions.py
  │   ├── helps.py
  │   ├── i18n
  │   │   └── translator.py
  │   ├── languages
  │   │   ├── en_US
  │   │   │   └── LC_MESSAGES
  │   │   │       └── en_US.mo
  │   │   └── zh_CN
  │   │       └── LC_MESSAGES
  │   │           └── zh_CN.mo
  │   ├── log
  │   │   └── logger.py
  │   └── utils
  │       ├── __init__.py
  │       ├── _dl.py
  │       ├── _signal.py
  │       ├── _singleton.py
  │       ├── abogus.py
  │       ├── abogus_async.py
  │       ├── abogus_full.py
  │       ├── conf_manager.py
  │       ├── decorators.py
  │       ├── json_filter.py
  │       ├── utils.py
  │       └── xbogus.py
  ├── messages.pot
  ├── package-lock.json
  ├── package.json
  ├── pyproject.toml
  ├── pytest.ini
  ├── tests
  │   ├── test_cli_console.py
  │   ├── test_desc_limit.py
  │   ├── test_dl.py
  │   ├── test_excetions.py
  │   ├── test_i18n.py
  │   ├── test_logger.py
  │   ├── test_signal.py
  │   ├── test_singleton.py
  │   ├── test_timestamp.py
  │   ├── test_utils.py
  │   └── test_xbogus.py

  ```

</details>


## 💰 赞助商

<a href="https://tikhub.io/"><img style="border-radius:20px" src="https://github.com/Johnserf-Seed/f2/assets/40727745/70a67dd1-dccb-44a9-b635-c29a950f1daf"></a>

[TikHub](https://tikhub.io/) 是一家提供优质数据接口服务的供应商。通过每日签到，可以获取免费额度。可以使用我的注册邀请链接：[https://beta-web.tikhub.io/users/signup?referral_code=6hLcGD94](https://beta-web.tikhub.io/users/signup?referral_code=6hLcGD94) 或 邀请码：`6hLcGD94`，注册并充值即可获得`$2`额度。

[TikHub](https://tikhub.io/) 提供以下服务：

- 丰富的数据接口
- 每日签到免费获取额度
- 高质量的API服务
- 官网：https://tikhub.io/
- 项目地址：https://github.com/TikHubIO/


## 👨‍💻 贡献

如果你有兴趣为`F2`做拓展新应用，请查看[贡献指南](https://github.com/Johnserf-Seed/f2/blob/main/.github/CONTRIBUTING.md)。


## 🙏 鸣谢

- [Windows Terminal](https://aka.ms/terminal)
- [Python](https://www.python.org/)
- [click](https://github.com/pallets/click)
- [rich](https://github.com/Textualize/rich)
- [httpx](https://github.com/encode/httpx)
- [aiofiles](https://github.com/Tinche/aiofiles)
- [aiosqlite](https://github.com/omnilib/aiosqlite)
- [jsonpath-ng](https://github.com/h2non/jsonpath-ng)
- [m3u8](https://github.com/globocom/m3u8)
- [pyyaml](https://github.com/yaml/pyyaml)
- [pytest](https://github.com/pytest-dev/pytest)
- [browser_cookie3](https://github.com/borisbabic/browser_cookie3)
- [pydantic](https://github.com/samuelcolvin/pydantic)
- [qrcode](https://github.com/lincolnloop/python-qrcode)
- [vitepress](https://github.com/vuejs/vitepress)
- [websockets](https://github.com/python-websockets/websockets)
- [protobuf](https://github.com/protocolbuffers/protobuf)
- [PyExecJS](https://github.com/doloopwhile/PyExecJS)

没有这些库和程序，`F2`将无法实现这些功能，对于他们的贡献和努力，表示由衷的感谢。


## ⚖️ 协议&声明

- **请严格遵守爬虫规范，不要使用此项目进行任何违法行为。**
- **不出售、共享、加密、上传、研究和传播任何个人信息。**
- **项目及其相关代码仅供学习与研究使用，不构成任何明示或暗示的保证。**
- **使用者因使用此项目及其代码可能造成的任何形式的损失，使用者应当自行承担一切风险。**
- **请遵守Apache-2.0开源协议，不要删除或修改代码中的任何版权信息。**
- **使用者不得将此项目及其代码用于任何形式的商业用途和商业行为。**
- **如果使用者使用此项目及其代码，即代表使用者同意遵守上述规定。**


## 📜 许可

[Apache-2.0 license](https://www.apache.org/licenses/LICENSE-2.0.html)

Copyright (c) 2023 JohnserfSeed


## 📧 联系

只回答关于`F2`的问题，可以通过以下方式联系我，请耐心等待，会尽快回复你。

- Mail：[johnserf-seed@foxmail.com](mailto:johnserf-seed@foxmail.com)
- Discord：[F2](https://discord.gg/3PhtPmgHf8)
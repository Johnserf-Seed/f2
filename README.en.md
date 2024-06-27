<p align="center">
  <img src="https://github.com/Johnserf-Seed/f2/raw/main/docs/public/f2-logo-with-shadow-svg@0.5x.svg" alt="Logo">
</p>

[![Downloads](https://pepy.tech/badge/f2/month)](https://pepy.tech/project/f2)
[![PyPI version](https://badge.fury.io/py/f2.svg)](https://badge.fury.io/py/f2)
[![Dev Branch](https://badgen.net/badge/branch/v0.0.1.6-pw2/blue)](https://github.com/Johnserf-Seed/f2/tree/v0.0.1.6-pw2)
[![Discord](https://img.shields.io/discord/1146473603450282004?label=Discord)](https://discord.gg/3PhtPmgHf8)
[![codecov](https://codecov.io/gh/Johnserf-Seed/f2/graph/badge.svg?token=T9DH4QPZSS)](https://codecov.io/gh/Johnserf-Seed/f2)
[![APACHE-2.0](https://img.shields.io/github/license/johnserf-seed/f2)](https://github.com/Johnserf-Seed/f2/blob/main/LICENSE)


[🇨🇳 简体中文 readme](https://github.com/Johnserf-Seed/f2/blob/main/README.md)
 • [🇬🇧 English readme](https://github.com/Johnserf-Seed/f2/blob/main/README.en.md)


`F2` is a [`Python` library](https://pypi.org/project/f2/) that provides multi-platform content downloading and API data processing. It supports platforms like `DouYin`, `TikTok`, `Twitter`, `Instagram`, and is easily adaptable to more platforms.

<img src='https://github.com/Johnserf-Seed/f2/assets/40727745/82644596-7eca-48ec-91b0-3c5e4c24ee90'>

## 🚀 Quick Start

### ⚙️ Installation

- [Prerequisites](https://johnserf-seed.github.io/f2/install.html#%E5%BF%85%E5%A4%87%E6%9D%A1%E4%BB%B6)
- [Package Manager Installation](https://johnserf-seed.github.io/f2/install.html#%E5%8C%85%E7%AE%A1%E7%90%86%E5%99%A8%E5%AE%89%E8%A3%85)
- [Compiled Installation](https://johnserf-seed.github.io/f2/install.html#%E7%BC%96%E8%AF%91%E5%AE%89%E8%A3%85)

### ⚡ Quick Use

- [Startup and Execution](https://johnserf-seed.github.io/f2/quick-start.html#%E5%90%AF%E5%8A%A8%E5%92%8C%E8%BF%90%E8%A1%8C)

### 📋 Configuration File

- [Main Configuration File (Frequent)](https://johnserf-seed.github.io/f2/site-config.html#%E4%B8%BB%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6)
- [Initialize Configuration File](https://johnserf-seed.github.io/f2/site-config.html#%E5%88%9D%E5%A7%8B%E5%8C%96%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6)
- [Custom Configuration File](https://johnserf-seed.github.io/f2/site-config.html#%E8%87%AA%E5%AE%9A%E4%B9%89%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6)
- [Cookie Configuration](https://johnserf-seed.github.io/f2/site-config.html#%E9%85%8D%E7%BD%AEcookie)
- [Configuration File Location](https://johnserf-seed.github.io/f2/site-config.html#%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E7%9A%84%E4%BD%8D%E7%BD%AE)

### 💻 Command Line

- [CLI Temporary Configuration](https://johnserf-seed.github.io/f2/cli.html#cli%E4%B8%B4%E6%97%B6%E9%85%8D%E7%BD%AE)

### 📘 Developer Guide

- [A Must-Read for Developers](https://johnserf-seed.github.io/f2/guide/what-is-f2.html)

### 🧩 Calling Examples

- [DouYin](https://johnserf-seed.github.io/f2/guide/apps/douyin/)

- [TikTok](https://johnserf-seed.github.io/f2/guide/apps/tiktok/)


## ✨ New Changes

When downloading or upgrading to a different version of `F2`, please note the following critical version updates.

<details>
  <summary> 📡 v0.0.1.6-pw2 </summary>

  - The configuration file format has been updated. If you are using an old configuration file, please migrate accordingly.
  - The default timezone for all timestamps is now (`UTC/GMT+08:00`).
  - The `douyin` live stream filenames have been adjusted to `flv`, and albums have been reverted to `webp`.
  - The 403 error for `tiktok` video URLs has been fixed. [Solution for TikTok video URL 403](https://johnserf-seed.github.io/f2/question-answer/qa.html#tiktok-403-forbidden)
  - `douyin` now defaults to using the `ab` algorithm for requests. (The full-powered ab algorithm will be open-sourced later).
  - For more changes, see [ChangeLog](https://github.com/Johnserf-Seed/f2/blob/main/CHANGELOG.md#0015---2024-04-04).
</details>

<details>
  <summary> 📡 v0.0.1.5-pw2 </summary>

  - `XBogus` parameter in `0.0.1.5` version now supports custom User-Agent (UA), please pay attention to UA specification.
  - The rebuilt database contains original data of interfaces, so you need to delete the old database file. If you want to retain records, please pay attention to migration.
  - The return types of all `fetch` methods have been unified to filter types, so you need to pay attention to this change.
  - Filter has added the `_to_raw` method, which can convert the filter to original interface data.
  - The file name template has been updated, and if your file name does not meet the specifications, an exception will be thrown.
  - `douyin` collection page links cannot be resolved, see [Douyin Collection Works](#抖音合集作品).
  - For more changes, see [ChangeLog](https://github.com/Johnserf-Seed/f2/blob/main/CHANGELOG.md#0015---2024-04-04).
</details>


## 📑 Documentation

The goal of `F2` is to provide a simple and easy-to-use interface for users to quickly obtain content data.
Many features are not fully developed in the `preview` version. If you find any issues, please submit an `issue` in the `F2` project. The [project documentation](https://johnserf-seed.github.io/f2/) is still being improved, and there may be delays, so please stay tuned.


## 🛠️ Q&A

[Common Questions and Solutions](https://johnserf-seed.github.io/f2/question-answer/qa.html)


## 🗓️ Todo

- Local forwarding functionality will be added in version `0.0.1.7`.
- More interfaces for `douyin`, `tiktok`, `weibo`, and `x` will be added in version `0.0.1.7`.
- Known issues with `x` will be fixed in version `0.0.1.7`.


## 🐛 Updates

[ChangeLog](https://github.com/Johnserf-Seed/f2/blob/main/CHANGELOG.md)


## 💡 Applications & Features

Feature status: 🟢 Represents implemented, 🟡 Represents being implemented, 🟤 Represents temporarily not implemented, 🔵 Represents future implementation, 🔴 Represents deprecation.
Account status: ⚪ Represents unknown, 🟣 Represents login required (ignores own account privacy settings), ⚫ Represents not login required (visible to guests only).

<details>
  <summary> 🎶 DouYin </summary>

  - 🟣 Indicates that login is required to download works that are only visible to oneself, favorited works, works in collection folders, or liked works. (After login, ignores own privacy settings and obtains personalized content)
  - ⚫ Indicates that login is not required to download public works, works in collection folders, liked works, etc. (Only downloads works visible to others and pages)

  | Feature | Account Status | API | Status |
  | --- | --- | --- | --- |
  | User Information | 🟣⚫ | `fetch_user_profile` | 🟢 |
  | Single Video (Video, Album, Daily) | 🟣⚫ | `fetch_one_video` | 🟢 |
  | Homepage Videos | 🟣⚫ | `fetch_user_post_videos` | 🟢 |
  | Liked Videos | 🟣⚫ | `fetch_user_like_videos` | 🟢 |
  | Collection Folder Videos | 🟣⚫ | `fetch_user_collects_videos` | 🟢 |
  | Collected Videos | 🟣 | `fetch_user_collection_videos` | 🟢 |
  | Collected Music | 🟣 | `fetch_user_music_collection` | 🟢 |
  | Collected Playlist | 🟣 | `fetch_user_mix_collection` | 🔵 |
  | Collected Series | 🟣 | `fetch_user_series_collection` | 🟤 |
  | Playlist Videos | ⚫ | `fetch_user_mix_videos` | 🟢 |
  | Recommended Videos | 🟣⚫ | `fetch_user_feed_videos` | 🟢 |
  | Related Videos | ⚫ | `fetch_related_videos` | 🟢 |
  | Live Room Information (Stream Download) | ⚫ | `fetch_user_live_videos`, `fetch_user_live_videos_by_room_id` | 🟢 |
  | Live Room Load | ⚫ | `fetch_live_im` | 🟢 |
  | Live Room Danmaku | ⚫ | `fetch_user_live_danmu` | 🟢 |
  | Followed Users Live | 🟣⚫ | `fetch_user_following_lives` | 🟢 |
  | Followed Users Information | 🟣⚫ | `fetch_user_following` | 🟢 |
  | Followers Information | 🟣⚫ | `fetch_user_follower` | 🟢 |
  | Followed Users Videos | 🟣⚫ | `fetch_user_following_videos` | 🟤 |
  | Followers Videos | 🟣⚫ | `fetch_user_follower_videos` | 🟤 |
  | Friends' Videos | 🟣 | `fetch_friend_feed_videos` | 🟢 |
  | Search Videos | ⚫ | `fetch_search_videos` | 🔵 |
  | Search Users | ⚫ | `fetch_search_users` | 🔵 |
  | Search Live | ⚫ | `fetch_search_lives` | 🔵 |
  | Search Suggestions | ⚫ | `fetch_search_suggest` | 🟤 |
  | Douyin Hot Search | ⚫ | `fetch_hot_search` | 🟤 |
  | Video Comments | 🟣⚫ | `fetch_video_comments` | 🔵 |
  | Watch History | 🟣 | `fetch_user_history_read` | 🟤 |
  | Watch Later | 🟣 | `fetch_user_watch_later` | 🟤 |
  | ... | ... | ... | ... |

  | Tool | Class | API | Status |
  | --- | --- | --- | --- |
  | Manage Client Configuration | `ClientConfManager` | | 🟢 |
  | Generate Real msToken | `TokenManager` | `gen_real_msToken` | 🟢 |
  | Generate Fake msToken | `TokenManager` | `gen_false_msToken` | 🟢 |
  | Generate ttwid | `TokenManager` | `gen_ttwid` | 🟢 |
  | Generate webid | `TokenManager` | `gen_webid` | 🟢 |
  | Generate verify_fp | `VerifyFpManager` | `gen_verify_fp` | 🟢 |
  | Generate s_v_web_id | `VerifyFpManager` | `gen_s_v_web_id` | 🟢 |
  | Generate Live Signature | `DouyinWebcastSignature` | `get_signature` | 🟢 |
  | Generate wss Signature Parameters from API Model | `WebcastSignatureManager` | `model_2_endpoint` | 🟢 |
  | Generate Xb Parameters from API URL | `XBogusManager` | `str_2_endpoint` | 🟢 |
  | Generate Xb Parameters from API Model | `XBogusManager` | `model_2_endpoint` | 🟢 |
  | Generate Ab Parameters from API URL | `ABogusManager` | `str_2_endpoint` | 🟢 |
  | Generate Ab Parameters from API Model | `ABogusManager` | `model_2_endpoint` | 🟢 |
  | Extract Single User ID | `SecUserIdFetcher` | `get_sec_user_id` | 🟢 |
  | Extract User IDs from List | `SecUserIdFetcher` | `get_all_sec_user_id` | 🟢 |
  | Extract Single Video ID | `AwemeIdFetcher` | `get_aweme_id` | 🟢 |
  | Extract Video IDs from List | `AwemeIdFetcher` | `get_all_aweme_id` | 🟢 |
  | Extract Single Playlist ID | `MixIdFetcher` | `get_mix_id` | 🟢 |
  | Extract Playlist IDs from List | `MixIdFetcher` | `get_all_mix_id` | 🟢 |
  | Extract Single Live Room ID | `WebCastIdFetcher` | `get_webcast_id` | 🟢 |
  | Extract Live Room IDs from List | `WebCastIdFetcher` | `get_all_webcast_id` | 🟢 |
 </details>

<details>
  <summary> 🎶 TikTok </summary>

  - 🟣 Indicates that login is required to download works that are only visible to oneself, favorited works, works in collection folders, or liked works. (After login, ignores own privacy settings and obtains personalized content)
  - ⚫ Indicates that login is not required to download public works, works in collection folders, liked works, etc. (Only downloads works visible to others and pages)

  | Feature | Account Status | Interface | Feature Status |
  | --- | --- | --- | --- |
  | User Information | 🟣⚫ | `fetch_user_profile` | 🟢 |
  | Single Work | 🟣⚫ | `fetch_one_video` | 🟢 |
  | Home Page Works | 🟣⚫ | `fetch_user_post_videos` | 🟢 |
  | Liked Works | 🟣⚫ | `fetch_user_like_videos` | 🟢 |
  | Favorite Works | 🟣⚫ | `fetch_user_collect_videos` | 🟢 |
  | Playlist  | 🟣⚫ | `fetch_play_list` | 🟢 |
  | Playlist Works | 🟣⚫ | `fetch_user_mix_videos` | 🟢 |
  | Post Search|🟣⚫|`fetch_search_videos`|🟢|
  | Live Room Information (Stream Download) |⚫|`fetch_user_live_videos`|🟢|
  | Check If The webcast Is Alive|🟣⚫|`fetch_check_live_alive`|🟢|
  | ... | ... | ... | ... |
 </details>


## 📸 Screenshots

<details>
  <summary> 🎬 DouYin </summary>

  ### DouYin Single Work

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/3e7c685e-0a0e-4d3a-a605-56eccb71c467'>

  ### DouYin Home Page Works

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/0743627d-4f03-43c9-94f0-653903382685'>

  ### DouYin Liked Works

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/95c588f7-45ab-4713-8102-7cd84452c0b8'>

  ### DouYin Favorite Works

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/66951156-43df-4152-9b0c-4ee4f58a1e38'>

  ### DouYin Collection Works

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/37e2354b-3548-4ade-afa4-f8bb8108c565'>

  ### DouYin Collected Original Sound

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/e0837eff-a7c2-4e6e-99fb-71e85ace83dc'>

  ### DouYin Collection Works

  Support for parsing any work link in the collection
  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/fa79c123-2552-49ed-b37f-0931489dcdad'>

  Collection link parsing
  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/1dd41daa-f375-448f-a3aa-55c14a4bf36c'>

  ### DouYin Hotspot

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/4378b171-ccfd-457d-8850-4a509d888d85'>

  ### DouYin Live Room Information

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/6d62dc77-82cc-48b8-a1b1-ff98b04b5952'>

  ### DouYin Live Room Danmaku

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/96a586a4-94c4-4866-b2ac-446b58d8f8a0'>

  ### DouYin Related Videos

  <img src="https://github.com/Johnserf-Seed/f2/assets/40727745/e36fb510-39ef-486e-b944-7dbf8cf25c36">

  ### DouYin Friend Videos

  <img src="https://github.com/Johnserf-Seed/f2/assets/40727745/437fa0ad-9524-4674-9d73-56db815113ef">

  ### DouYin Webcast Danmaku

  https://github.com/Johnserf-Seed/f2/assets/40727745/500d1eaf-59ba-44ba-849b-666c0ddf8469

</details>

<details>
  <summary> 🎬 TikTok </summary>

  ### TikTok Single Work

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/e08628c9-c6e7-4982-90a9-d9788db9ef6a'>

  ### TikTok Home Page Works

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/0d334e32-3d47-4c17-a4d8-44898f8a71a6'>

  ### TikTok Liked Works

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/a1fd1123-d60a-4e08-9e65-16e6dcab30da'>

  ### TikTok Favorite Works

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/e87d34f4-04e5-47f5-9e46-233e68ab39db'>

  ### TikTok Collection Works

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/0919b53c-4605-464e-90cd-5b4c8d3e8e88'>

  ### TikTok Collected Original Sound

  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/17c9eb02-53b5-4484-8a6d-777a074b99d9'>

  ### TikTok Post Search
  <img src='https://github.com/Johnserf-Seed/f2/assets/40727745/091e66d5-f123-4883-9360-db3dad359d7d'>

</details>


## 📦 Structures

<details>
  <summary>📁 Project Catalogs</summary>

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


## 👨‍💻 Contributions

If you are interested in extending new applications for `F2`, please refer to the [contribution guidelines](https://github.com/Johnserf-Seed/f2/blob/main/.github/CONTRIBUTING.md).


## 🙏 Acknowledgements

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

Without these libraries and programs, `F2` would not be able to achieve these functionalities. Sincere thanks for their contributions and efforts.


## ⚖️ License & Disclaimer

- **Please strictly comply with the web scraping standards and do not engage in any illegal activities using this project.**
- **Do not sell, share, encrypt, upload, research, or disseminate any personal information.**
- **The project and its related code are for learning and research purposes only and do not constitute any express or implied warranties.**
- **Users should bear all risks arising from the use of this project and its code.**
- **Please comply with the Apache-2.0 open-source license and do not delete or modify any copyright information in the code.**
- **Users are not allowed to use this project and its code for any form of commercial purposes and commercial activities.**
- **By using this project and its code, users agree to abide by the above rules.**


## 📜 License

[Apache-2.0 license](https://www.apache.org/licenses/LICENSE-2.0.html)

Copyright (c) 2023 JohnserfSeed


## 📧 Contact

I only answer questions about `F2`. You can contact me through the following methods. Please be patient, and I will reply to you as soon as possible.

- Mail: [johnserf-seed@foxmail.com](mailto:johnserf-seed@foxmail.com)
- Discord: [F2](https://discord.gg/3PhtPmgHf8)

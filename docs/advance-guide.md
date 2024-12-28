---
outline: deep
---

# 进阶用法

::: tip :bulb: 什么是进阶用法？
进阶用法是指在 CLI 命令的基础上，通过进阶开发者接口的方法，提高工具的使用效率，或者解决一些特殊问题。
:::

::: info :mag: 欢迎提问
如果您在开发过程中遇到任何疑问，请详细描述并在 [F2 Discussions](https://github.com/Johnserf-Seed/f2/discussions/categories/q-a) 提问，或通过邮件联系 `support@f2.wiki`，描述您的来意，我将尽快为您解答。
:::

## Douyin

### 批量采集直播流 <Badge text="Beta" type="warning"/>

![batch-lives](/douyin/batch-lives.png)

::: details :link: 示例代码
::: code-group
<<< @/snippets/douyin/batch-lives.py
:::

> [!IMPORTANT] 重要 ❗❗❗
> 1. 抖音限制同一账号不能进入同一个直播间，因此使用登录的方式采集直播流时，无法观看直播。
> 2. 可以使用游客账号绕过第一点的限制，游客账号的生成方法请参考 `mstoken` 与 `ttwid` 或 [直播弹幕转发](#直播弹幕转发) 的代码片段。
> 3. 请确保网络环境稳定，否则可能会导致采集任务中断。
> 4. 请确保设备性能足够，否则大量采集可能会导致设备卡顿，同时请适当增加 `max_connections` 和 `max_tasks` 的值。

### 直播弹幕转发

![wss-connect](/douyin/wss-connect.png)

::: details :link: 示例代码
::: code-group
<<< @/snippets/douyin/user-live-im-fetch.py#user-live-im-fetch-snippet{32-35,38-71,108-115}
:::
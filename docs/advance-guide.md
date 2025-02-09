---
outline: deep
---

# 进阶用法

::: tip :bulb: 什么是进阶用法？
进阶用法是指在 `CLI` 模式的基础上，通过进阶开发者接口的方法，提高工具的使用效率，或者解决一些特殊问题。
:::

::: info :mag: 欢迎提问
如果您在开发过程中遇到任何疑问，请详细描述并在 [F2 Discussions](https://github.com/Johnserf-Seed/f2/discussions/categories/q-a) 提问，或通过邮件联系 `support@f2.wiki`，描述您的来意，我将尽快为您解答。
:::

## Douyin

### 批量采集发布视频 <Badge text="Beta" type="warning"/>

![batch-posts](/douyin/batch-posts.png)

> [!IMPORTANT] 重要 ❗❗❗
> 1. **速率限制**：抖音平台对于频繁请求有一定的速率限制，高并发的请求可能会导致请求失败出现 `429`，`444` 等错误码。请自行控制请求速率，避免被封禁 IP。
> 2. **网络稳定性**：请确保网络环境稳定，否则可能导致采集任务中断，特别是在作品数量较多的情况下。
> 3. **设备性能**：请确保设备性能足够，避免因大量采集任务导致设备卡顿。
> 4. **并发设置**：如需采集多个作品，请适当增加 `max_connections` 和 `max_tasks` 参数值，以满足异步并发需求，否则可能出现任务阻塞的情况。
> 5. **轮询更新作品**：若需轮询检测作品状态并进行采集，请参考代码片段中的变化部分。

::: details :link: 示例代码
::: code-group
<<< @/snippets/douyin/batch-posts.py
:::

### 批量采集直播流 <Badge text="Beta" type="warning"/>

![batch-lives](/douyin/batch-lives.png)

> [!IMPORTANT] 重要 ❗❗❗
> 1. **账号限制**：抖音平台限制同一账号无法同时进入同一直播间。因此，使用登录账号采集直播流时，仅可在采集任务启动后继续观看该直播。
> 2. **游客账号绕过**：可通过游客账号绕过上述限制。有关生成游客账号的方法，请参考 `mstoken` 与 `ttwid` 或 [直播弹幕转发](#直播弹幕转发) 的相关代码片段。
> 3. **网络稳定性**：请确保网络环境稳定，否则可能导致采集任务中断。
> 4. **设备性能**：请确保设备性能足够，避免因大量采集任务导致设备卡顿。
> 5. **并发设置**：如需采集多个直播，请适当增加 `max_connections` 和 `max_tasks` 参数值，以满足异步并发需求，否则可能出现任务阻塞的情况。
> 6. **轮询开播采集**：若需轮询检测开播状态并进行采集，请参考代码片段中的变化部分。

::: details :link: 示例代码
::: code-group
<<< @/snippets/douyin/batch-lives.py
:::

### 直播弹幕转发

![wss-connect](/douyin/wss-connect.png)

> [!IMPORTANT] 重要 ❗❗❗
> 1. **账号限制**：抖音平台限制同一账号无法同时进入同一直播间。因此，需要使用生成 `ttwid` 的方法生成游客账号，绕过上述限制。
> 2. **网络稳定性**：请确保网络环境稳定，否则可能导致采集任务中断。
> 3. **设备性能**：请确保设备性能足够，避免因大量采集任务导致设备卡顿。
> 4. **并发设置**：多个直播间弹幕转发时，请使用不同的 `WSS` 配置连接，以避免弹幕混乱和阻塞。

::: details :link: 示例代码
::: code-group
<<< @/snippets/douyin/user-live-im-fetch.py#user-live-im-fetch-snippet{32-35,38-71,108-115}
:::

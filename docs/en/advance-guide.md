---
outline: deep
---

# Advanced Usage

::: tip :bulb: What is Advanced Usage?
Advanced usage refers to improving tool efficiency or solving specific issues using developer interfaces beyond the basic `CLI` mode.
:::

::: info :mag: Have Questions?
If you encounter any issues during development, please describe them in detail and ask in [F2 Discussions](https://github.com/Johnserf-Seed/f2/discussions/categories/q-a), or contact `support@f2.wiki` via email with your inquiry. I will respond as soon as possible.
:::

## Douyin

### Batch Collection of Published Videos <Badge text="Beta" type="warning"/>

![batch-posts](/douyin/batch-posts.png)

> [!IMPORTANT] Important ❗❗❗
> 1. **Rate Limits**: The Douyin platform enforces rate limits on frequent requests. High-concurrency requests may result in errors such as `429` or `444`. Control the request rate to avoid IP bans.
> 2. **Network Stability**: Ensure a stable network environment to prevent collection task interruptions, especially when processing a large number of videos.
> 3. **Device Performance**: Ensure sufficient device performance to prevent lag caused by large-scale collection tasks.
> 4. **Concurrency Settings**: When collecting multiple videos, increase the values of `max_connections` and `max_tasks` appropriately to support asynchronous concurrency. Otherwise, tasks may become blocked.
> 5. **Polling for New Videos**: If you need to poll for video updates and collect them, refer to the changes in the provided code snippet.

::: details :link: Example Code
::: code-group
<<< @/snippets/douyin/batch-posts.py
:::

### Batch Collection of Live Streams <Badge text="Beta" type="warning"/>

![batch-lives](/douyin/batch-lives.png)

> [!IMPORTANT] Important ❗❗❗
> 1. **Account Restrictions**: Douyin restricts the same account from entering the same livestream room simultaneously. When collecting livestreams with a logged-in account, you can only watch the stream after starting the collection task.
> 2. **Bypassing Restrictions with Guest Accounts**: You can bypass the above restriction using a guest account. Refer to methods for generating `mstoken` and `ttwid`, or see the relevant code snippet in [Livestream Danmaku Forwarding](#直播弹幕转发).
> 3. **Network Stability**: Ensure a stable network environment to prevent task interruptions.
> 4. **Device Performance**: Ensure sufficient device performance to prevent lag from large-scale collection tasks.
> 5. **Concurrency Settings**: When collecting multiple livestreams, increase `max_connections` and `max_tasks` appropriately to support asynchronous concurrency. Otherwise, tasks may become blocked.
> 6. **Polling for Live Streams**: If you need to poll for live stream status updates and collect them, refer to the changes in the provided code snippet.

::: details :link: Example Code
::: code-group
<<< @/snippets/douyin/batch-lives.py
:::

### Livestream Danmaku Forwarding

![wss-connect](/douyin/wss-connect.png)

> [!IMPORTANT] Important ❗❗❗
> 1. **Account Restrictions**: Douyin restricts the same account from entering the same livestream room simultaneously. To bypass this, generate a guest account using `ttwid`.
> 2. **Network Stability**: Ensure a stable network environment to prevent task interruptions.
> 3. **Device Performance**: Ensure sufficient device performance to prevent lag from large-scale collection tasks.
> 4. **Concurrency Settings**: When forwarding danmaku (chat messages) from multiple livestreams, use separate `WSS` connections to prevent message mix-ups and blockages.

::: details :link: Example Code
::: code-group
<<< @/snippets/douyin/user-live-im-fetch.py#user-live-im-fetch-snippet{32-35,38-71,108-115}
:::

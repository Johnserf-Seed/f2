---
outline: deep
---

# 接口列表

::: tip 注意
🟢代表已经实现，🟡代表正在实现或修改，🟤代表暂时不实现，🔵代表未来可能实现，🔴代表将会弃用。
:::

::: details handler接口列表

|     CLI接口          |         方法          |
| :------------------ | :-------------------  |
| get模式发送通知       | `fetch_bark_notification` |
| post模式发送通知      | `post_bark_notification`  |
| cipher模式发送通知    | `cipher_bark_notification`|

|     数据方法接口      |         方法           | 开发者接口  |
| :------------------ | :-------------------   | :--------: |
|  快捷通知            | `send_quick_notification` |   🟢  |
:::

::: details utils接口列表

| 工具类接口        | 类名                | 方法               | 状态 |
| :-------------- | :------------------ | :---------------- | :--: |
| 管理客户端配置     | `ClientConfManager` |                  |  🟢  |
:::

::: details cralwer接口列表


| 爬虫url接口    | 类名       | 方法          | 状态 |
| :----------- | :--------- | :----------  | :--: |
| Bark 通知接口(GET) | `BarkCrawler` | `fetch_bark_notification` | 🟢 |
| Bark 通知接口(POST) | `BarkCrawler` | `post_bark_notification` | 🟢 |
| Bark 通知接口(CIPHER) | `BarkCrawler` | `cipher_bark_notification` | 🟢 |
:::

::: tip :information_source: 提示
- `Bark` 是 `F2` 内置的一个 `iOS` 端通知推送工具，用于将任务执行结果推送到 `iOS` 设备。同时也可以通过 `CLI` 模式来发送通知。[CLI指引](/guide/apps/bark/cli.md)
- `Bark` 的 `GCM` 推送加密模式仍在实验阶段，建议先使用 `AES-256-CBC` 加密模式。
:::

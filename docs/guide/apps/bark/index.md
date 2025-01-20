---
outline: [2,3]
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
| 生成随机数字字节       | -       | `generate_numeric_bytes` |  🟢  |
:::

::: details crawler接口列表


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

## handler接口列表

### 快捷通知 🟢

异步方法，用于发送快捷通知。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| title | str | 通知标题 |
| body | str | 通知内容 |
| send_method | str | 发送方式，可选值为 `GET`、`POST` |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| BarkNotificationFilter | model | 通知过滤器，包含通知数据的 `_to_raw`、`_to_dict` 方法 |

<<< @/snippets/bark/notification.py{15}

## utils接口列表

### 管理客户端配置 🟢

用于管理客户端配置。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| 无 | 无 | 无 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| 配置文件值 | Any | 配置文件值 |

<<< @/snippets/bark/client-config.py{4,5,7,8,10,11}

### 生成随机数字字节 🟢

用于生成随机数字字节。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| length | int | 字节长度 |

| 返回 | 类型 | 说明 |
| :--- | :--- | :--- |
| numeric_str | bytes | 随机字节 |

<<< @/snippets/bark/generate-bytes.py{7}
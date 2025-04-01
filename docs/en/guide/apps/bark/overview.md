---
outline: [2,3]
---

# API List

::: tip Note
🟢 Indicates implemented, 🟡 Indicates in progress or being modified, 🟤 Indicates temporarily not implemented, 🔵 Indicates possible future implementation, 🔴 Indicates deprecation.
:::

::: details Handler API List

|     CLI API          |    Method          |
| :------------------ | :-------------------  |
| (GET) Send notification        | `fetch_bark_notification` |
| (POST) Send notification       | `post_bark_notification`  |
| (Cipher) Send notification     | `cipher_bark_notification`|

| Data Method API     |    Method           | Developer API  |
| :------------------ | :-------------------   | :--------: |
|  Quick Notification  | `send_quick_notification` |   🟢  |
:::

::: details Utils API List

| Utility API  |    Class Name   | Method            | Status |
| :----------- | :-------------- | :---------------- | :--: |
| Manage Client Configuration | `ClientConfManager` |  -  |  🟢  |
| Generate Random Numeric Bytes | - | `generate_numeric_bytes` |  🟢  |
:::

::: details Crawler API List

| Crawler URL API    | Class Name    | Method                  | Status |
| :----------- | :--------- | :----------  | :--: |
| (GET) Bark Notification API | `BarkCrawler` | `fetch_bark_notification` | 🟢 |
| (POST) Bark Notification API | `BarkCrawler` | `post_bark_notification` | 🟢 |
| (CIPHER) Bark Notification API | `BarkCrawler` | `cipher_bark_notification` | 🟢 |
:::

::: tip :bulb: Note
- `Bark` is an integrated `iOS` notification push tool in `F2`, used to push task execution results to `iOS` devices. It can also send notifications via `CLI` mode. [CLI Guide](/guide/apps/bark/cli)
- `Bark`'s `GCM` push encryption mode is still in the experimental stage. It is recommended to use `AES-256-CBC` encryption mode for now.
:::

## handler API List

### Quick Notification 🟢

Asynchronous method for sending quick notifications.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| title | str | Notification title |
| body | str | Notification content |
| send_method | str | Sending method, options: `GET`, `POST` |

| Return | Type | Description |
| :--- | :--- | :--- |
| BarkNotificationFilter | model | Notification filter containing `_to_raw`, `_to_dict` methods |

<<< @/snippets/bark/notification.py{15}

## utils API List

### Manage Client Configuration 🟢

Used for managing client configuration.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | None | None |

| Return | Type | Description |
| :--- | :--- | :--- |
| Config file value | Any | Configuration file value |

<<< @/snippets/bark/client-config.py{4,5,7,8,10,11}

### Generate Random Numeric Bytes 🟢

Used to generate random numeric bytes.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| length | int | Byte length |

| Return | Type | Description |
| :--- | :--- | :--- |
| numeric_str | bytes | Random bytes |

<<< @/snippets/bark/generate-bytes.py{7}

## crawler API List

### Bark Notification API (GET) 🟢

Asynchronous method for sending `Bark` notifications.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| params | BarkModel | API parameter model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_get_json | dict | Return value after sending |

### Bark Notification API (POST) 🟢

Asynchronous method for sending `Bark` notifications using `POST`.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| params | BarkModel | API parameter model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_post_json | dict | Return value after sending |

### Bark Notification API (CIPHER) 🟢

Asynchronous method for sending encrypted `Bark` notifications.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| params | BarkCipherModel | API parameter model |

| Return | Type | Description |
| :--- | :--- | :--- |
| _fetch_post_json | dict | Return value after sending |

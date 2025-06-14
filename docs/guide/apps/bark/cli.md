---
outline: deep
---

## 参数列表

| 短参数 | 长参数 | 类型 | 说明 |
| ------ | ------ | ---- | ---- |
| `-c`   | `--config` | `FILE` | 配置文件路径，最低优先 |
| `-k`   | `--key` | `TEXT` | Bark 的 `API Key` |
| `-d`   | `--token` | `TEXT` | Bark 的 `Device Token` |
| `-M`   | `--mode` | `ENUM` | 推送模式 |
| `-t`   | `--title` | `TEXT` | 推送的标题 |
| `-b`   | `--body` | `TEXT` | 推送的内容 |
| `-cl`  | `--call` | `BOOLEAN` | 是否持续响铃，默认关闭 |
| `-l`   | `--level` | `ENUM` | 推送级别 |
| `-v`   | `--volume` | `INTEGER` | 推送音量，范围 `0-10` |
| `-bd`  | `--badge` | `INTEGER` | 推送的角标数量 |
| `-ac`  | `--autoCopy` | `BOOLEAN` | 是否自动复制推送内容 |
| `-cp`  | `--copy` | `TEXT` | 指定要复制的内容，若未指定则复制整个推送内容 |
| `-s`   | `--sound` | `ENUM` | 推送铃声 |
| `-i`   | `--icon` | `TEXT` | 推送图标 URL，相同的图标 URL 仅下载一次 |
| `-g`   | `--group` | `TEXT` | 推送分组，通知中心将按分组显示推送 |
| `-a`   | `--isArchive` | `BOOLEAN` | 是否保存推送，默认保存 |
| `-u`   | `--url` | `TEXT` | 点击推送时跳转的 URL |
| `-P`   | `--proxies` | `TEXT...` | 代理服务器 |
|        | `--update-config` | `FLAG` | 更新配置文件 |
|        | `--init-config` | `TEXT` | 初始化配置文件 |
| `-h`   |               | `FLAG` | 显示富文本帮助 |
|        | `--help`      | `FLAG` | 显示帮助信息并退出 |


## 详细说明

### `--config`

指定配置文件的路径，优先级最低。默认**主配置文件**路径为 `f2/conf/app.yaml`，支持**绝对路径**与**相对路径**。

### `--key`

`Bark` 的 `key` 是一个 `22` 位的字符串。可在 `Bark` 应用的首页查看。

![Bark Key](/bark/bark-key.jpg)

::: details :link: 示例：使用 `/push` 接口时需将 `key` 放入请求体
::: code-group
```shell [bash]
curl -X "POST" "https://api.day.app/push" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
  "body": "Test Bark Server",
  "title": "Test Title",
  "device_key": "your_key"
}'
```
:::

### `--token`

`Bark` 的 `Token` 是一个 `64` 位的字符串。可在 `Bark` 应用的首页查看。

![Bark Token](/bark/bark-token.jpg)

::: warning :lock: 密钥来源
- `Bark` 的 `Key` 由 `Bark` 服务器生成，**请勿泄露**，包括开发者和社区。
- `Bark` 的 `Device Token` 由 `Apple` 服务器生成，**请勿泄露**。
:::

::: danger :bangbang: 隐私保护 :bangbang:
- 绝对不要在 `Discussions`、`Issues`、`Discord`等公共场所分享你的 `Key` 和 `Token`，注意删除敏感信息。
- 任何人获取到你的 `Cookie` 都可以向你的设备发送推送通知。
- 当发生泄露时，请立即在 `Bark` 应用中重新生成 `Key` 和 `Token`。
- 更多隐私保护信息，请参阅 `Bark` 的[隐私安全](https://bark.day.app/#/privacy)。
:::

### `--mode`

指定推送方式：

- `get`：使用 GET 请求发送通知（**默认**）。
- `post`：使用 POST 请求发送通知。

::: info :information_source: 注意事项
- 若手动拼接参数，需注意 `URL 编码` 问题；`F2` 会自动处理编码。
- 使用 `post` 模式时，参数会以 `JSON` 格式发送，无需手动编码。
- [常见问题：URL编码](https://bark.day.app/#/faq?id=%e6%8e%a8%e9%80%81%e7%89%b9%e6%ae%8a%e5%ad%97%e7%ac%a6%e5%af%bc%e8%87%b4%e6%8e%a8%e9%80%81%e5%a4%b1%e8%b4%a5%ef%bc%8c%e6%af%94%e5%a6%82-%e6%8e%a8%e9%80%81%e5%86%85%e5%ae%b9%e5%8c%85%e5%90%ab%e9%93%be%e6%8e%a5%ef%bc%8c%e6%88%96%e6%8e%a8%e9%80%81%e5%bc%82%e5%b8%b8-%e6%af%94%e5%a6%82-%e5%8f%98%e6%88%90%e7%a9%ba%e6%a0%bc)
:::

- `cipher`：推送加密模式 <Badge type="warning" text="实验性" />

推送加密是一种保护推送内容的方法，通过自定义密钥对推送内容进行加密和解密，防止推送内容被 `Bark` 和 `Apple` 服务器访问或泄露。

细节均由 `F2` 自动完成，只需正常提供明文内容即可。

![Bark Ciphertext](/bark/bark-ciphertext.jpg)

![Bark Ciphertext Setting](/bark/bark-ciphertext-setting.jpg)

::: details :link: 示例：`F2` 官方的加密推送命令
```shell [bash]
f2 bark -t "Test Title" -b "Test Body" -M cipher
```
:::

::: details :link: 示例：`Bark` 官方的发送脚本
<<< @/snippets/bark/ciphertext.sh
:::

> [!IMPORTANT] 重要 ❗❗❗
> - 启用推送加密后，默认的 `get` 请求模式将不再适用，需切换到 `cipher` 模式。
> - 在 `Bark` 首页的 `推送加密` 设置中，必须按照要求配置自定义密钥，密钥的长度由所选加密算法决定。
> - 为了增强安全性并降低碰撞概率，`F2` 会自动使用随机 `iv`。在 `Bark` 中 `iv` 可以任意填写。
> - 尽管推送加密功能仍在实验阶段，建议先使用 `AES-256-CBC` 加密模式。因为目前 `Bark v1.4.3(5)` 版本的 `GCM` 模式尚未完全支持，需在往后版本中才能启用。[允许使用GCM Mode#262](https://github.com/Finb/Bark/commit/8a2a7fc2b44073498e4abea54f62497a0e06926e)。
> - 了解更多信息，请参阅 `Bark` 的[推送加密](https://bark.day.app/#/encryption)。

### `--title`

推送的标题。建议不要超过 **8个字符**。

### `--body`

推送的内容。建议不要超过 **30个字符**。

### `--call`

是否持续响铃，默认**关闭**。

### `--level`

推送通知的优先级：
- `active`：**默认**
- `timeSensitive`：时效性通知
- `passive`：被动通知
- `critical`：紧急通知

::: warning :warning: 重要提示 :warning:
- 设置为 `critical` 级别的通知，在 `iOS 15` 及以上版本中会强制震动，即使设备处于静音模式。
:::

### `--volume`

推送音量，范围 `0-10`。

### `--badge`

推送的角标数量。会在 `Bark` 应用的图标上显示。

### `--autoCopy`

是否自动复制推送内容。

在 `iOS 14.5` 之后的版本因权限收紧，不能在收到推送时自动复制推送内容到剪切板。

可下拉推送或在锁屏界面左滑推送点查看即可自动复制，或点击弹出的推送复制按钮。

### `--copy`

指定要复制的内容，若未指定则复制整个推送内容。一般用于需要复制推送内容的场景。

### `--sound`

推送铃声，可选值：
- `birdsong`
- `alarm`
- `chord`
- `dog`
- `guitar`
- `piano`
- `ring`
- `robot`
- `siren`
- `trumpet`
- `vibrate`
- `none`
- ……

更多铃声请查看 `Bark` 应用的设置。同时支持自定义铃声。

### `--icon`

推送图标 `URL`，相同的图标 `URL` 仅下载一次。默认为 `F2` 的图标。

![F2 Icon](/f2-logo.ico)

### `--group`

推送分组，通知中心将按分组显示推送。适用不同的推送场景，如不同的应用与服务器状况。建议不超过 **8个字符**。

### `--isArchive`

是否保存推送，默认**保存**。若关闭，则推送不会保存在 `Bark` 应用中。

### `--url`

点击推送时跳转的 URL，支持 `URL Scheme` 和 `Universal Link`。适用一些需要回调或跳转的场景。

<video src="https://github.com/user-attachments/assets/ab289f3c-dcb4-4c08-af75-91a3109493f8" width="70%" height="auto" autoplay loop style="border-radius: 8px; overflow: hidden;"></video>

::: details :link: 示例：使用 `URL Scheme` 跳转到 `F2` 文档官网。
```shell [bash]
f2 bark -t "Jump Test" -b "Open F2 Docs" --url "https://f2.wiki/"
```
:::

::: tip :earth_asia: 更新路线-正式版
- `F2` 向用户推送开播通知，点击推送即可远程下载直播。
- `F2` 向用户推送作品更新通知，点击推送即可下载更新。
- 通过 `F2 URL Scheme` 命令实现远程控制。
:::

### `--proxies`

配置代理服务器，支持多种代理类型，支持最多两个参数，分别指定代理类型和地址。

**语法格式：**
```bash
--proxies <type> <address>
```

**支持的代理类型：**
- `http`: HTTP代理
- `https`: HTTPS代理
- `socks4`: SOCKS4代理
- `socks5`: SOCKS5代理

**使用示例：**

::: code-group
```bash[SOCKS5代理]
f2 bk --proxies socks5 127.0.0.1:1080
```

```bash[HTTP代理]
f2 bk --proxies http proxy.example.com:8080
```

```bash[带认证的代理]
# 可在配置文件中设置用户名密码
f2 bk --proxies socks5 user:pass@127.0.0.1:1080
```
:::

> [!IMPORTANT] 重要提示
> - **SOCKS代理推荐**：对于Bark等平台，推荐使用 SOCKS5 代理以获得更好的兼容性
> - **认证支持**：支持用户名密码认证，格式：`username:password@host:port`
> - **兼容性**：如果代理不支持出口 HTTPS，请使用 HTTP 类型的代理

> [!TIP] 配置文件方式
> 你也可以在配置文件中设置代理：
> ```yaml
> douyin:
>   proxies:
>     type: socks5
>     host: 127.0.0.1
>     port: 1080
>     username: user  # 可选
>     password: pass  # 可选
> ```

### `--update-config`

通过 `CLI` 参数更新配置文件。详见：[配置Cookie](/site-config#配置Cookie)。

### `--init-config`

初始化高频配置文件。详见：[初始化配置文件](/site-config#初始化配置文件)。

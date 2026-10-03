---
outline: deep
---

## 参数列表

| 短参数 | 长参数 | 类型 | 说明 |
| ------ | ------ | ---- | ---- |
| `-c`   | `--config` | `FILE` | 配置文件的路径，最低优先 |
| `-u`   | `--url` | `TEXT` | 根据模式提供相应的链接 |
| `-p`   | `--path` | `TEXT` | 作品保存位置 |
| `-f`   | `--folderize` | `BOOLEAN` | 是否将作品保存到单独的文件夹 |
| `-M`   | `--mode` | `ENUM` | 下载模式 |
| `-n`   | `--naming` | `TEXT` | 全局作品文件命名方式 |
| `-k`   | `--cookie` | `TEXT` | 登录后的cookie |
| `-i`   | `--interval` | `TEXT` | 下载日期区间 |
| `-e`   | `--timeout` | `INTEGER` | 网络请求超时时间 |
| `-r`   | `--max_retries` | `INTEGER` | 网络请求超时重试数 |
| `-x`   | `--max-connections` | `INTEGER` | 网络请求并发连接数 |
| `-t`   | `--max-tasks` | `INTEGER` | 异步的任务数 |
| `-o`   | `--max-counts` | `INTEGER` | 最大作品下载数 |
| `-s`   | `--page-counts` | `INTEGER` | 每页获取作品数 |
| `-P`   | `--proxies` | `TEXT...` | 代理服务器 |
|        | `--insecure` | `FLAG` | 关闭 TLS 证书校验 |
|        | `--update-config` | `BOOLEAN` | 更新配置文件 |
|        | `--init-config` | `TEXT` | 初始化配置文件 |
|        | `--auto-cookie` | `ENUM` | 自动获取cookie |
| `-h`   |               | `FLAG` | 显示富文本帮助 |
|        | `--help`      | `FLAG` | 显示帮助信息并退出 |

## 详细说明

### `--config`

指定配置文件的路径，优先级最低。默认**主配置文件**路径为 `f2/conf/app.yaml`，支持**绝对路径**与**相对路径**。

配置文件无法解析时，`F2` 会给出出错的行号与列号；文件顶层不是键值映射或没有该应用的配置时同样直接报错，并以退出码 `1` 结束。没有该应用的配置时，可以用 `--init-config` 向该文件补充默认配置。

### `--url`

根据模式提供相应的链接。

### `--path`

推文保存位置。默认为当前目录下的 `Download`。支持**绝对路径**与**相对路径**。

::: tip :bulb: 提示
推文按 `<path>/twitter/<mode>/<用户昵称>` 分目录保存。用户修改昵称后，再次下载该用户（任一模式）时会把各下载模式下旧昵称的目录一起重命名为新昵称，已下载的推文随目录保留，文件名没有变化的推文不会重新下载；之后再改名也会继续跟随。某个模式下新昵称的目录已经存在时，该模式的两个目录都保持不变并在日志中提示，手动合并并删除旧目录后不再提示。
:::

### `--folderize`

是否将推文保存到单独的文件夹。默认为 `true`。

### `--mode`

下载模式：
- `one`：单个推文
- `post`：主页推文，包括置顶推文与串推（自己回复自己的推文）
- `like`：喜欢推文
- `bookmark`：书签(收藏)推文

### `--naming`

全局推文文件命名方式。默认为 `{create}_{desc}`，支持的变量有：`{create}`，`{nickname}`，`{tweet_id}`，`{desc}`，`{uid}`。支持的分割符有：`_`，`-`。

- `{create}`：推文创建时间
- `{nickname}`：用户昵称
- `{tweet_id}`：推文 ID
- `{desc}`：推文文案
- `{uid}`：用户 ID

::: tip :bulb: 提示
- `custom_fields` 为自定义字段，开发者可以自定义字段映射，详见：[全局格式化文件名 🟢](/guide/apps/twitter/overview#全局格式化文件名-🟢)。
- 文件名中的文案与昵称会原样保留标点、空格和各国文字，只把系统不允许的字符 `\ / : * ? " < > |` 换成外观相近的全角字符（例如 `?` 换成 `？`），换行等控制字符会换成空格或去掉；文案超过 200 字节时会截断中间部分，整个文件名连同后缀超过 255 字节时也会截断中间部分，这样也能保存到 NAS 等按字节限制文件名长度的位置；Windows 下路径超过 260 个字符时会自动改用长路径，不需要修改系统设置。
:::

### `--cookie`

登录后的 `Cookie`。大部分接口需要登录后才能获取数据，所以需要提供登录后的 `Cookie`。

::: details :link: `Cookie` 获取方法请参阅下图。
![Console Cookie](https://github.com/user-attachments/assets/4523e8c7-f74e-4d5f-9da6-6bb3658f8b24)
:::

::: tip :bulb: 提示
- `Twitter` 的请求需要 `X-Csrf-Token`。`F2` 会自动使用 `cookie` 中的 `ct0`，复制完整的 `cookie` 即可；只有 `cookie` 里没有 `ct0` 时，才会使用[**F2配置文件**](/site-config#主配置文件)中的 `X-Csrf-Token`。
- 无法采集或风控时请及时更新 `Cookie`。
- 不可以出现除 `ascii` 以外的字符，更新配置前请仔细检查。
:::

::: danger :bangbang: 警告 :bangbang:
- 绝对不要在 `Discussions`、`Issues`、`Discord`等公共场所分享你的 `Cookie`，注意删除敏感信息。
- 任何人获取到你的 `Cookie` 都可以直接登录你的账号。
- 当发生泄露时，请立即登出账号并重新登录。
:::

### `--interval`

下载日期区间内发布的推文，格式：`年-月-日|年-月-日`，首尾两天都包含在内，按北京时间计算。例如：`2024-01-01|2024-06-30`，设置 `all` 为下载所有推文。

::: tip :bulb: 提示
- 按推文的发布时间筛选，对所有模式生效。
- `post` 模式从最新的推文开始翻页，翻到区间开始之前的推文时停止，区间越早，需要翻的页越多。置顶推文不按发布时间排列，在区间内时同样会下载，不影响翻页。
- `like` 与 `bookmark` 按点赞、收藏的时间排列，与推文的发布时间无关，会翻完全部页面再按区间筛选。
- 日期格式错误或结束日期早于开始日期时直接报错退出，不会发起请求。
- 同时设置 `--max-counts` 时，按区间筛选后的数量计算。
:::

### `--timeout`

网络请求超时时间。默认为 `10` 秒。

### `--max_retries`

网络请求超时重试数。默认为 `5` 次。

### `--max-connections`

网络请求并发连接数。默认为 `10`。

### `--max-tasks`

异步的任务数。默认为 `5`。

### `--max-counts`

本次最多下载的推文数，按所有页累计计算，达到后不再翻页。设置为 `None` 或 `0` 表示无限制。默认为 `0`。

### `--page-counts`

每次向接口请求的推文数，只决定分几次请求（翻几页），不限制总共下载多少条。不建议超过 `20`。默认为 `20`。

::: tip :bulb: 提示
`--page-counts` 是每页要多少，`--max-counts` 是总共下载多少，两者互不替代。例如 `-s 5 -o 2` 表示每次向接口请求 5 条推文，总共最多下载 2 条；只想限制下载数量时设置 `--max-counts` 即可。
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
f2 x --proxies socks5 127.0.0.1:1080
```

```bash[HTTP代理]
f2 x --proxies http proxy.example.com:8080
```

```bash[带认证的代理]
# 可在配置文件中设置用户名密码
f2 x --proxies socks5 user:pass@127.0.0.1:1080
```
:::

> [!IMPORTANT] 重要提示
> - **SOCKS代理推荐**：对于Twitter等平台，推荐使用 SOCKS5 代理以获得更好的兼容性
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

### `--insecure`

关闭 `TLS` 证书校验，仅建议在受信任的调试代理环境中使用。该选项只对本次运行生效，不会写入配置文件；需要持久关闭请在 `conf.yaml` 中设置 `verify: false`。详见：[证书校验](/site-config#证书校验)。

```bash
f2 x --insecure --proxies http 127.0.0.1:8888 ...
```

### `--update-config`

通过 `CLI` 参数更新配置文件。详见：[配置Cookie](/site-config#配置Cookie)。

### `--init-config`

初始化高频配置文件。详见：[初始化配置文件](/site-config#初始化配置文件)。

### `--auto-cookie`

自动从浏览器获取cookie，使用该命令前请确保关闭所选的浏览器。支持的浏览器有：
- `chrome`
- `firefox`
- `edge`
- `opera`
- `opera_gx`
- `safari`
- `chromium`
- `brave`
- `vivaldi`
- `librewolf`

获取成功后会把 cookie 写入配置文件（用 `-c` 指定了自定义配置文件时写入该文件）并退出，不会开始下载；获取失败时输出原因并以退出码 `1` 结束。

Windows 上的新版 Chrome、Edge 暂时无法自动获取 cookie，解决办法见 [FAQ](/faq#自动获取-cookie-失败-unable-to-get-key-for-cookie-decryption)。

不支持切换浏览器用户配置。

> [!IMPORTANT] 重要 ❗❗❗
> - 近期受新版 `Chromium` 内核升级影响，更新了 `Cookie` 加密方式，导致 `F2` 无法自动获取晚于 `2024/08/15` 之后版本的浏览器 `Cookie`。
> - 在修复版本的依赖更新前请手动更新 `Cookie`。
> - 了解更多请参阅 [borisbabic/browser_cookie3#215](https://github.com/borisbabic/browser_cookie3/pull/215)。
> - 截至 `2024/12/23`，该修复不支持最新的 `Chromium` 版本。请使用不同的浏览器或降级到 `v128` 之前的版本。

::: details :link: 示例：手动更新 `Cookie`。
```shell [bash]
f2 x -k "your_cookie" -c your_config.yaml --update-config
```
:::

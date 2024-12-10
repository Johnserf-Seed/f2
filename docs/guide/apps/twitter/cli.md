---
outline: deep
---

## 参数列表

| 短参数 | 长参数 | 类型 | 说明 |
| ------ | ------ | ---- | ---- |
| `-c`   | `--config` | `FILE` | 配置文件的路径，最低优先 |
| `-u`   | `--url` | `TEXT` | 根据模式提供相应的链接 |
| `-d`   | `--desc` | `BOOLEAN` | 是否保存视频文案 |
| `-p`   | `--path` | `TEXT` | 作品保存位置 |
| `-f`   | `--folderize` | `BOOLEAN` | 是否将作品保存到单独的文件夹 |
| `-M`   | `--mode` | `ENUM` | 下载模式 |
| `-n`   | `--naming` | `TEXT` | 全局作品文件命名方式 |
| `-k`   | `--cookie` | `TEXT` | 登录后的cookie |
| `-e`   | `--timeout` | `INTEGER` | 网络请求超时时间 |
| `-r`   | `--max_retries` | `INTEGER` | 网络请求超时重试数 |
| `-x`   | `--max-connections` | `INTEGER` | 网络请求并发连接数 |
| `-t`   | `--max-tasks` | `INTEGER` | 异步的任务数 |
| `-o`   | `--max-counts` | `INTEGER` | 最大作品下载数 |
| `-s`   | `--page-counts` | `INTEGER` | 每页获取作品数 |
| `-l`   | `--languages` | `ENUM` | 显示语言 |
| `-P`   | `--proxies` | `TEXT...` | 代理服务器 |
|        | `--update-config` | `BOOLEAN` | 更新配置文件 |
|        | `--init-config` | `TEXT` | 初始化配置文件 |
|        | `--auto-cookie` | `ENUM` | 自动获取cookie |
| `-h`   |               | `FLAG` | 显示富文本帮助 |
|        | `--help`      | `FLAG` | 显示帮助信息并退出 |

## 详细说明

### `--config`

配置文件的路径，最低优先。默认配置文件路径为 `f2/conf/app.yaml`。支持**绝对路径**与**相对路径**。

### `--url`

根据模式提供相应的链接。

### `--desc`

是否保存推文文案。默认为 `true`。保留原始文案信息。

### `--path`

推文保存位置。默认为当前目录。支持**绝对路径**与**相对路径**。

### `--folderize`

是否将推文保存到单独的文件夹。默认为 `true`。

### `--mode`

下载模式：
- `one`：单个推文
- `post`：主页推文
- `like`：喜欢推文
- `bookmark`：书签(收藏)推文

### `--naming`

全局推文文件命名方式。默认为 `{create}_{desc}`，支持的变量有：`{create}`，`{nickname}`，`{tweet_id}`，`{desc}`，`{uid}`。

- `{create}`：推文创建时间
- `{nickname}`：用户昵称
- `{tweet_id}`：推文 ID
- `{desc}`：推文文案
- `{uid}`：用户 ID


### `--cookie`

登录后的 `Cookie`。大部分接口需要登录后才能获取数据，所以需要提供登录后的 `Cookie`。

::: details :link: `Cookie` 获取方法请参阅下图。
![Console Cookie](https://github.com/user-attachments/assets/4523e8c7-f74e-4d5f-9da6-6bb3658f8b24)
:::

::: tip :bulb: 提示
- `Twitter` 还需要额外获取 `X-Csrf-Token`，请确保在**低频配置文件**中配置。
- 无法采集或风控时请及时更新 `Cookie` 与 `X-Csrf-Token`。
- 不可以出现除 `ascii` 以外的字符，更新配置前请仔细检查。
:::

::: danger :bangbang: 警告 :bangbang:
- 绝对不要在 `Discussions`、`Issues`、`Discord`等公共场所分享你的 `Cookie`，注意删除敏感信息。
- 任何人获取到你的 `Cookie` 都可以直接登录你的账号。
- 当发生泄露时，请立即登出账号并重新登录。
:::

### `--languages`

指定显示语言。默认值为 zh_CN，支持选项：zh_CN 和 en_US，不支持通过配置文件修改。

### `--proxies`

配置代理服务器，支持最多两个参数，分别对应 `http://` 和 `https://` 协议。
例如：`http://x.x.x.x https://x.x.x.x`。
如果代理不支持出口 HTTPS，请使用：`http://x.x.x.x http://x.x.x.x`。

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

不支持切换浏览器用户配置。

> [!IMPORTANT] 重要 ❗❗❗
> - 近期受新版 `Chromium` 内核升级影响，更新了 `Cookie` 加密方式，导致 `F2` 无法自动获取晚于 `2024/08/15` 之后版本的浏览器 `Cookie`。
> - 在修复版本的依赖更新前请手动更新 `Cookie`。
> - 了解更多请参阅 [borisbabic/browser_cookie3#215](https://github.com/borisbabic/browser_cookie3/pull/215)。

::: details :link: 示例：手动更新 `Cookie`。
```shell [bash]
f2 x -k "your_cookie" -c your_config.yaml --update-config
```
:::

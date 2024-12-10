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
| `-n`   | `--naming` | `TEXT` | 全局微博文件命名方式 |
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

### `--mode`

下载模式：
- `one`：单个微博
- `post`：主页微博
- `like`：点赞微博

### `--interval`

下载日期区间发布的微博，格式：`2022-01-01|2023-01-01`，`all` 为下载所有作品。

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
f2 wb -k "your_cookie" -c your_config.yaml --update-config
```
:::

## CLI 帮助 - 推特

### 参数列表

| 短参数 | 长参数 | 类型 | 说明 |
| ------ | ------ | ---- | ---- |
| `-c`   | `--config` | `FILE` | 配置文件的路径，最低优先 |
| `-u`   | `--url` | `TEXT` | 根据模式提供相应的链接 |
| `-p`   | `--path` | `TEXT` | 作品保存位置，支持绝对与相对路径 |
| `-f`   | `--folderize` | `BOOLEAN` | 是否将作品保存到单独的文件夹 |
| `-M`   | `--mode` | `[one\|post\|like\|bookmark]` | 下载模式：单个推文(one)，主页推文(post)，喜欢(like)，书签(bookmark) |
| `-n`   | `--naming` | `TEXT` | 全局推文文件命名方式，前往文档查看更多帮助 |
| `-k`   | `--cookie` | `TEXT` | 登录后的cookie |
| `-e`   | `--timeout` | `INTEGER` | 网络请求超时时间 |
| `-r`   | `--max_retries` | `INTEGER` | 网络请求超时重试数 |
| `-x`   | `--max-connections` | `INTEGER` | 网络请求并发连接数 |
| `-t`   | `--max-tasks` | `INTEGER` | 异步的任务数 |
| `-o`   | `--max-counts` | `INTEGER` | 最大推文下载数。`0` 表示无限制 |
| `-s`   | `--page-counts` | `INTEGER` | 从接口每页可获取推文数，不建议超过 `20` |
| `-l`   | `--languages` | `[zh_CN\|en_US]` | 显示语言。默认为 `zh_CN`，可选：`zh_CN`、`en_US`，不支持配置文件修改 |
| `-P`   | `--proxies` | `TEXT...` | 代理服务器，最多 2 个参数，`http://`与`https://`。空格区分 2 个参数，例如：`http://x.x.x.x https://x.x.x.x` |
|        | `--update-config` | `BOOLEAN` | 使用命令行选项更新配置文件。需要先使用`-c`选项提供一个配置文件路径 |
|        | `--init-config` | `TEXT` | 初始化配置文件。不能同时初始化和更新配置文件 |
|        | `--auto-cookie` | `[chrome\|firefox\|edge\|opera\|opera_gx\|safari\|chromium\|brave\|vivaldi\|librewolf]` | 自动从浏览器获取cookie，使用该命令前请确保关闭所选的浏览器 |
| `-h`   | `--help` | `FLAG` | 显示富文本帮助 |
|        | `--help` | `FLAG` | 显示帮助信息并退出 |

### 详细说明

#### `--config`

配置文件的路径，最低优先。默认配置文件路径为 `f2/conf/app.yaml`。支持绝对路径与相对路径。

#### `--url`

根据模式提供相应的链接。

#### `--mode`

下载模式：
- `one`：单个推文
- `post`：主页推文
- `like`：喜欢推文
- `bookmark`：书签(收藏)推文

#### `--languages`

显示语言。默认为 `zh_CN`，可选：`zh_CN`、`en_US`，不支持配置文件修改。

#### `--proxies`

代理服务器，最多 2 个参数，`http://`与`https://`。空格区分 2 个参数，例如：`http://x.x.x.x https://x.x.x.x`。如果你的代理不支持`出口HTTPS`，那么请使用`http://x.x.x.x http://x.x.x.x`。

#### `--auto-cookie`

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

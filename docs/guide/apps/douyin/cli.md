## CLI 帮助 - 抖音

### 参数列表

| 短参数 | 长参数 | 类型 | 说明 |
| ------ | ------ | ---- | ---- |
| `-c`   | `--config` | `TEXT` | 配置文件的路径，最低优先 |
| `-u`   | `--url` | `TEXT` | 根据模式提供相应的链接 |
| `-m`   | `--music` | `BOOLEAN` | 是否保存视频原声 |
| `-v`   | `--cover` | `BOOLEAN` | 是否保存视频封面 |
| `-d`   | `--desc` | `BOOLEAN` | 是否保存视频文案 |
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
| `-l`   | `--languages` | `ENUM` | 显示语言 |
| `-P`   | `--proxies` | `TEXT...` | 代理服务器 |
| `-L`   | `--lyric` | `BOOLEAN` | 是否保存原声歌词 |
|        | `--update-config` | `BOOLEAN` | 更新配置文件 |
|        | `--init-config` | `TEXT` | 初始化配置文件 |
|        | `--auto-cookie` | `ENUM` | 自动获取cookie |
| `-h`   |               | `FLAG` | 显示富文本帮助 |
|        | `--help`      | `FLAG` | 显示帮助信息并退出 |

### 详细说明

#### `--config`

配置文件的路径，最低优先。默认配置文件路径为 `f2/conf/app.yaml`。支持绝对路径与相对路径。

#### `--url`

根据模式提供相应的链接。例如：主页、点赞、收藏作品填入主页链接，单作品填入作品链接，合集与直播同上。

#### `--mode`

下载模式：
- `one`：单个作品
- `post`：主页作品
- `like`：点赞作品
- `collection`：收藏作品
- `collects`：收藏夹作品
- `music`：收藏音乐
- `mix`：合集
- `live`：直播

#### `--naming`

全局作品文件命名方式。默认为 `{create}_{desc}`，支持的变量有：`{nickname}`，`{create}`，`{aweme_id}`，`{desc}`，`{uid}`。支持的分割符有：`_`，`-`。

- `{nickname}`：作者昵称
- `{create}`：作品创建时间
- `{aweme_id}`：作品ID
- `{desc}`：作品文案
- `{uid}`：作者ID

#### `--interval`

下载日期区间发布的作品，格式：`年-月-日` 如：`2022-01-01|2023-01-01`，设置`all` 为下载所有作品。

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

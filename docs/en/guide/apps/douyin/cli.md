---
outline: [2,3]
---

## Parameter list

| Short parameter | Long parameter | Type | Description |
| ------ | ------ | ---- | ---- |
| `-c`   | `--config` | `FILE` | Profile path, lowest priority |
| `-u`   | `--url` | `TEXT` | Links are provided according to the pattern |
| `-m`   | `--music` | `BOOLEAN` | Whether to save the original audio of the video |
| `-v`   | `--cover` | `BOOLEAN` | Whether to save video cover |
| `-d`   | `--desc` | `BOOLEAN` | Whether to save the video desc |
| `-p`   | `--path` | `TEXT` | The location where the video is saved |
| `-f`   | `--folderize` | `BOOLEAN` | Whether to save the work in a separate folder |
| `-M`   | `--mode` | `ENUM` | Download mode |
| `-n`   | `--naming` | `TEXT` | Global video file naming method |
| `-k`   | `--cookie` | `TEXT` | Logged in cookie |
| `-i`   | `--interval` | `TEXT` | Download date range |
| `-e`   | `--timeout` | `INTEGER` | Network request timeout |
| `-r`   | `--max_retries` | `INTEGER` | Network request timeout retry count |
| `-x`   | `--max-connections` | `INTEGER` | Network request concurrent connection count |
| `-t`   | `--max-tasks` | `INTEGER` | Asynchronous task count |
| `-o`   | `--max-counts` | `INTEGER` | Maximum number of downloads |
| `-s`   | `--page-counts` | `INTEGER` | Number of works per page |
| `-P`   | `--proxies` | `TEXT...` | Proxy server |
| `-L`   | `--lyric` | `BOOLEAN` | Whether to save the original lyrics |
|        | `--update-config` | `BOOLEAN` | Update configuration file |
|        | `--init-config` | `TEXT` | Initialize configuration file |
|        | `--auto-cookie` | `ENUM` | Automatically obtain cookies |
| `-h`   |               | `FLAG` | Display rich text help |
|        | `--help`      | `FLAG` | Display the help message and exit |

## Detailed description

### `--config`

Specify the path to the configuration file, with the lowest priority. The default path for the **main configuration file** is `f2/conf/app.yaml`, which supports **absolute paths** and **relative paths**.

### `--url`

Links are provided according to the pattern. For example, fill in the homepage link for homepage, likes, and favorite works, fill in the link of the work for a single work, and the collection is the same as for the live broadcast.

### `--music`

Whether to save the original audio of the video. The default is `true`.

### `--cover`

Whether to save the video cover. The default is `true`. Only save the cover in the original size.

### `--desc`

Whether to save the video copy. Defaults to `true`. Keep the original desc information.

### `--path`

The location where the video is saved. Defaults to `Download` in the current directory. Supports **absolute paths** and **relative paths**.

### `--folderize`

Whether to save the video to a separate folder. Defaults to `true`.

### `--mode`

Download mode:
- `one`: a single video
- `post`: Homepage videos
- `like`: Liked videos
- `collection`: collection of works
- `collects`: favorite works
- `music`: collection of music
- `mix`: collection
- `live`: live broadcast

::: info :information_source: Tips
- `collection` mode requires login.
- `music` mode requires the `--lyric` parameter to specify whether to save original lyrics.
- `mix` mode requires the `--url` parameter, which can be a collection link or a link to a work in the collection.
- `live` mode does not currently support special live broadcast rooms, such as `360°` live broadcast.
:::

### `--naming`

Global work file naming method. The default is `{create}_{desc}`, supported variables include: `{nickname}`, `{create}`, `{aweme_id}`, `{desc}`, `{uid}`. Supported separators include: `_`, `-`.

- `{nickname}`: author’s nickname
- `{create}`: creation time of the work
- `{aweme_id}`: work ID
- `{desc}`: work copywriting
- `{uid}`: Author ID

### `--cookie`

`Cookie` after login. Most interfaces require logging in to obtain data, so a `Cookie` after logging in is required.

::: details :link: Please see the figure below for how to obtain `Cookie`.
![Console Cookie](https://github.com/user-attachments/assets/4523e8c7-f74e-4d5f-9da6-6bb3658f8b24)
:::

::: tip :bulb: Tips
- Please update `Cookie` in time when collection or risk control cannot be performed.
- Characters other than `ascii` are not allowed. Please check carefully before updating the configuration.
:::

:::danger :bangbang: warning :bangbang:
- Never share your `Cookie` in `Discussions`, `Issues`, `Discord` and other public places, and be careful to delete sensitive information.
- Anyone who gets your `Cookie` can log in to your account directly.
- When a leak occurs, please log out of your account immediately and log in again.
:::

### `--interval`

Download works published within a date range, in the format: `Year-Month-Day|Year-Month-Day`. For example: `2022-01-01|2023-01-01`, set `all` to download all works.

### `--timeout`

Network request timeout. Default is `10` seconds.

### `--max_retries`

Network request timeout retry count. The default is `5` times.

### `--max-connections`

Network request concurrent connection number. Default is `10`.

### `--max-tasks`

The number of asynchronous tasks. Default is `5`.

### `--max-counts`

Maximum number of work downloads. Set to `None` or `0` for no limit. Default is `0`.

### `--page-counts`

The number of works that can be obtained from each page of the interface is not recommended to exceed `20`. Default is `20`.

### `--proxies`

Configure the proxy server, supporting up to two parameters, corresponding to the `http://` and `https://` protocols.

Example: `--proxies http://x.x.x.x https://x.x.x.x`。

> [!IMPORTANT] IMPORTANT ❗❗❗
> **If the proxy does not support egress HTTPS, use: `--proxies http://x.x.x.x http://x.x.x.x`.**

### `--lyric`

Whether to save the original lyrics. The default is `false`. Save in `.lrc` format.

### `--update-config`

Update configuration files via `CLI` parameters. For details, see: [Configuring Cookies](/en/site-config#configure-cookies)。

### `--init-config`

Initialize the high-frequency configuration file. See: [Initialize Config File](/en/site-config#initialize-configuration-file)。

### `--auto-cookie`

Automatically obtain `cookie` from the browser. Please make sure to close the selected browser before using this command. Supported browsers include:
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

Not supported to switch browser user settings.

> [!IMPORTANT] IMPORTANT ❗❗❗
> - Due to an update to the `Chromium` security policy, the `Cookie` encryption version has been upgraded to `V20`. Causes the `--auto-cookie` command to temporarily fail to fetch browser `cookies` issued after `August 15, 2024`.
> - Please update `F2` to the latest version to get the latest fix.
> - If you do not wish to upgrade, you can refer to the `PR` below to manually install the dependencies of the fixed version.
> - [borisbabic/browser_cookie3#215](https://github.com/borisbabic/browser_cookie3/pull/215)
> - As of `2024/dec/23`, the fix still does not support the latest `Chromium` kernel version, please use a different browser or downgrade the browser version to before `v128`.

::: details :link: Example: Manually update `Cookie`.
```shell [bash]
f2 dy -k "your_cookie" -c your_config.yaml --update-config
```
:::

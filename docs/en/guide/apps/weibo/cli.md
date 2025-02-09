---
outline: deep
---

## Parameter List

| Short | Long | Type | Description |
| ------ | ------ | ---- | ---- |
| `-c`   | `--config` | `FILE` | Path to the configuration file, lowest priority |
| `-u`   | `--url` | `TEXT` | Provide the corresponding link based on the mode |
| `-p`   | `--path` | `TEXT` | Save location for posts |
| `-f`   | `--folderize` | `BOOLEAN` | Whether to save posts in separate folders |
| `-M`   | `--mode` | `ENUM` | Download mode |
| `-n`   | `--naming` | `TEXT` | Global file naming format for posts |
| `-k`   | `--cookie` | `TEXT` | Logged-in session cookie |
| `-e`   | `--timeout` | `INTEGER` | Network request timeout duration |
| `-r`   | `--max_retries` | `INTEGER` | Number of retries for timed-out network requests |
| `-x`   | `--max-connections` | `INTEGER` | Number of concurrent network connections |
| `-t`   | `--max-tasks` | `INTEGER` | Number of asynchronous tasks |
| `-o`   | `--max-counts` | `INTEGER` | Maximum number of posts to download |
| `-s`   | `--page-counts` | `INTEGER` | Number of posts fetched per page |
| `-l`   | `--languages` | `ENUM` | Display language |
| `-P`   | `--proxies` | `TEXT...` | Proxy servers |
|        | `--update-config` | `BOOLEAN` | Update configuration file |
|        | `--init-config` | `TEXT` | Initialize configuration file |
|        | `--auto-cookie` | `ENUM` | Automatically retrieve the cookie |
| `-h`   |               | `FLAG` | Display rich-text help |
|        | `--help`      | `FLAG` | Show help message and exit |

## Detailed Explanation

### `--config`

Path to the configuration file, lowest priority. The default configuration file path is `f2/conf/app.yaml`. Supports both **absolute** and **relative** paths.

### `--url`

Provide the corresponding link based on the selected mode.

### `--path`

Save location for posts. The default is `Download` in the current directory. Supports **absolute** and **relative** paths.

### `--folderize`

Whether to save posts in separate folders. Default is `true`.

### `--mode`

Download modes:
- `one`: Single post
- `post`: Homepage posts

### `--naming`

Global file naming format for posts. The default format is `{create}_{desc}`. Supported variables:
- `{nickname}`: User nickname
- `{create}`: Post creation time
- `{weibo_id}`: Weibo post ID
- `{desc}`: Post description
- `{uid}`: User ID

Supported separators: `_`, `-`.

::: tip :bulb: Tip
- `custom_fields` allows developers to define custom field mappings. See: [Global File Name Formatting 🟢](/guide/apps/weibo/overview#global-file-name-formatting-🟢).
:::

### `--cookie`

Logged-in session `Cookie`. Most APIs require login, so a valid `Cookie` must be provided.

::: details :link: See the image below for how to retrieve your `Cookie`.
![Console Cookie](https://github.com/user-attachments/assets/4523e8c7-f74e-4d5f-9da6-6bb3658f8b24)
:::

::: tip :bulb: Tip
- If data collection fails or you get restricted, update your `Cookie` promptly.
- The `Cookie` should only contain `ASCII` characters; check carefully before updating.
- Some APIs do not require login and allow guest `Cookies`. See: [Generate Guest Cookie 🟢](/guide/apps/weibo/overview#generate-guest-cookie-🟢).
:::

::: danger :bangbang: Warning :bangbang:
- Never share your `Cookie` in `Discussions`, `Issues`, `Discord`, or any public forum.
- Anyone with your `Cookie` can log into your account.
- If leaked, log out immediately and sign back in to invalidate it.
:::

### `--timeout`

Network request timeout duration. Default is `10` seconds.

### `--max_retries`

Number of retries for timed-out network requests. Default is `5` times.

### `--max-connections`

Number of concurrent network connections. Default is `10`.

### `--max-tasks`

Number of asynchronous tasks. Default is `5`.

### `--max-counts`

Maximum number of posts to download. Set to `None` or `0` for unlimited. Default is `0`.

### `--page-counts`

Number of posts fetched per API request. It is not recommended to exceed `20`. Default is `20`.

### `--languages`

Specifies the display language. Default is `zh_CN`. Supported options: `zh_CN`, `en_US`. This cannot be modified in the configuration file.

### `--proxies`

Configure the proxy server, supporting up to two parameters, corresponding to the `http://` and `https://` protocols.

Example: `--proxies http://x.x.x.x https://x.x.x.x`。

> [!IMPORTANT] IMPORTANT ❗❗❗
> **If the proxy does not support egress HTTPS, use: `--proxies http://x.x.x.x http://x.x.x.x`.**

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
f2 wb -k "your_cookie" -c your_config.yaml --update-config
```
:::

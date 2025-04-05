---
outline: deep
---

## Parameter List

| Short | Long | Type | Description |
| ------ | ------ | ---- | ---- |
| `-c`   | `--config` | `FILE` | Path to the configuration file, lowest priority |
| `-u`   | `--url` | `TEXT` | Provide the corresponding link based on the mode |
| `-p`   | `--path` | `TEXT` | Save location for works |
| `-f`   | `--folderize` | `BOOLEAN` | Whether to save works in separate folders |
| `-M`   | `--mode` | `ENUM` | Download mode |
| `-n`   | `--naming` | `TEXT` | Global file naming format for works |
| `-k`   | `--cookie` | `TEXT` | Login cookie |
| `-e`   | `--timeout` | `INTEGER` | Network request timeout |
| `-r`   | `--max_retries` | `INTEGER` | Maximum retry attempts for network timeout |
| `-x`   | `--max-connections` | `INTEGER` | Number of concurrent network connections |
| `-t`   | `--max-tasks` | `INTEGER` | Number of asynchronous tasks |
| `-o`   | `--max-counts` | `INTEGER` | Maximum number of works to download |
| `-s`   | `--page-counts` | `INTEGER` | Number of works retrieved per page |
| `-P`   | `--proxies` | `TEXT...` | Proxy servers |
|        | `--update-config` | `BOOLEAN` | Update configuration file |
|        | `--init-config` | `TEXT` | Initialize configuration file |
|        | `--auto-cookie` | `ENUM` | Automatically obtain cookies |
| `-h`   |               | `FLAG` | Display rich-text help |
|        | `--help`      | `FLAG` | Show help information and exit |

## Detailed Explanation

### `--config`

Specifies the path to the configuration file, with the lowest priority. The default **main configuration file** path is `f2/conf/app.yaml`. Supports **absolute** and **relative paths**.

### `--url`

Provides the corresponding link based on the mode.

### `--path`

The save location for works. Defaults to `Download` in the current directory. Supports **absolute** and **relative paths**.

### `--folderize`

Determines whether works should be saved in separate folders. Default is `true`.

### `--mode`

Download modes:
- `one`: Single work
- `post`: Homepage works
- `like`: Liked works
- `bookmark`: Bookmarked (saved) works

### `--naming`

Global file naming format for works. Defaults to `{create}_{desc}`. Supported variables include: `{create}`, `{nickname}`, `{tweet_id}`, `{desc}`, `{uid}`. Supported separators: `_`, `-`.

- `{create}`: Work creation time
- `{nickname}`: User nickname
- `{tweet_id}`: Work ID
- `{desc}`: Work caption
- `{uid}`: User ID

::: tip :bulb: Tip
- `custom_fields` allows developers to define custom field mappings. See: [Global Formatting for Filenames 🟢](/guide/apps/twitter/overview#global-formatting-filenames-🟢).
:::

### `--cookie`

Login `Cookie`. Most APIs require login to access data, so a logged-in `Cookie` is required.

::: details :link: How to obtain `Cookie`
![Console Cookie](https://github.com/user-attachments/assets/4523e8c7-f74e-4d5f-9da6-6bb3658f8b24)
:::

::: tip :bulb: Tip
- `Twitter` also requires `X-Csrf-Token`. Ensure it is configured in [**F2 Configuration File**](/site-config#main-configuration-file).
- If unable to fetch data or facing restrictions, update `Cookie` and `X-Csrf-Token` promptly.
- Only ASCII characters are allowed. Double-check before updating configurations.
:::

::: danger :bangbang: Warning :bangbang:
- **Never share your `Cookie` in public spaces like Discussions, Issues, or Discord. Remove sensitive information.**
- **Anyone with access to your `Cookie` can log into your account.**
- **If leaked, log out and re-login immediately.**
:::

### `--timeout`

Network request timeout. Default is `10` seconds.

### `--max_retries`

Maximum retry attempts for network timeout. Default is `5` retries.

### `--max-connections`

Number of concurrent network connections. Default is `10`.

### `--max-tasks`

Number of asynchronous tasks. Default is `5`.

### `--max-counts`

Maximum number of works to download. `None` or `0` means unlimited. Default is `0`.

### `--page-counts`

Number of works retrieved per page from the API. Not recommended to exceed `20`. Default is `20`.

### `--proxies`

Configures the proxy server, supporting up to two parameters for `http://` and `https://` protocols.

Example: `--proxies http://x.x.x.x https://x.x.x.x`.

> [!IMPORTANT] IMPORTANT ❗❗❗
> **If the proxy does not support HTTPS egress, use: `--proxies http://x.x.x.x http://x.x.x.x`.**

### `--update-config`

Updates the configuration file via `CLI` parameters. See: [Configuring Cookies](/en/site-config#configure-cookies).

### `--init-config`

Initializes the high-frequency configuration file. See: [Initialize Config File](/en/site-config#initialize-configuration-file).

### `--auto-cookie`

Automatically retrieves `cookie` from the browser. Ensure the selected browser is closed before using this command. Supported browsers:
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

User settings switching is not supported.

> [!IMPORTANT] IMPORTANT ❗❗❗
> - Due to a `Chromium` security update, `Cookie` encryption has been upgraded to `V20`. This has temporarily broken the `--auto-cookie` command for cookies issued after `August 15, 2024`.
> - Update `F2` to the latest version for a fix.
> - If you do not wish to upgrade, manually install the dependency fix from the PR below:[borisbabic/browser_cookie3#215](https://github.com/borisbabic/browser_cookie3/pull/215)
> - As of `2024/Dec/23`, the fix does not support the latest `Chromium` version. Use a different browser or downgrade to a version before `v128`.

::: details :link: Example: Manually update `Cookie`.
```shell [bash]
f2 x -k "your_cookie" -c your_config.yaml --update-config
```
:::

# Command Line

The `F2` configuration file is independent of `CLI` command parameters and has the `lowest priority`.

## Temporary CLI Configuration

`CLI` command parameters have the highest priority, allowing you to change the settings without modifying the configuration file. For example, you can use `CLI` parameters to download all `liked` posts from a Douyin user.

This means you can temporarily download **User A**'s livestream, **User B**'s posts, and **User C**'s liked videos via the `CLI`.

::: code-group

```bash [User A]
$ f2 dy -c A.yaml -M live -u https://live.douyin.com/xxxxxxxxx
```

```bash [User B]
$ f2 dy -c B.yaml -M post
```

```bash [User C]
$ f2 dy -c C.yaml -M like
```
:::

Give it a try!

::: tip :triangular_flag_on_post: TODO
In future versions, operations will be simplified. You won’t need to specify the user’s livestream room ID to switch to the livestream download mode.
For more CLI commands, please check the [CLI Reference](/cli).
:::

::: warning Important
- There are no restrictions on naming conventions. You can use `dy-A.yaml`, `dy-B.yaml`, `tk-A.yaml`, `tk-B.yaml` to differentiate user configurations across different apps.
- Configuration operations are universal. The example uses a `Douyin` configuration file, but the same process applies to `TikTok` and other `F2` applications.
:::

## Advanced Usage

If you don’t want to create multiple configuration files, use the main configuration file. When using the main configuration file, there’s no need to specify `-c`. Just set it in the `application default/main config (app.yaml)`.

To download all `posted` videos from a Douyin user, set `mode: post`.

::: code-group

```sh [Windows]
$ f2 dy
```

```sh [Linux]
$ f2 dy
```

```sh [MacOS]
$ f2 dy
```
:::

To download all `liked` videos from a Douyin user, set `mode: like` in the `CLI`.

::: code-group

```sh [Windows]
$ f2 dy -M like
```

```sh [Linux]
$ f2 dy -M like
```

```sh [MacOS]
$ f2 dy -M like
```
:::

To download a `single` video from Douyin:

::: code-group

```sh [Windows]
$ f2 dy -M one -u https://v.douyin.com/iRNBho6u/
```

```sh [Linux]
$ f2 dy -M one -u https://v.douyin.com/iRNBho6u/
```

```sh [MacOS]
$ f2 dy -M one -u https://v.douyin.com/iRNBho6u/
```
:::

F2 will intelligently recognize links in messy text and supports both short and long URLs.

::: details :link: Supported Link Formats
<<< @/snippets/douyin/support-link.md
:::

::: tip :bulb: Important Notes
- The `interval` parameter is global and applies to all modes. You can set `-i` all in `CLI` to download all posts.
- In `CLI` mode, if the input text contains additional information, wrap it in double quotes `""` 👇
```sh [Windows]
$ f2 dy -M one -u "7.64 gOX:/ w@f.oD 05/14 世界这本书 又多读了一页。冰岛????旅行记# 冰岛  https://v.douyin.com/iR2syBRn/ 复制此链接，打开Dou音搜索，直接观看视！"
```
:::

## Application Command Line

### Bark

- [CLI Reference](/guide/apps/bark/cli)

### DouYin

- [CLI Reference](/guide/apps/douyin/cli)

### TikTok

- [CLI Reference](/guide/apps/tiktok/cli)

### Twitter

- [CLI Reference](/guide/apps/twitter/cli)

### WeiBo

- [CLI Reference](/guide/apps/weibo/cli)

# Quick Start

## Configuration

### First-time Setup

`F2` is an asynchronous library that runs based on configuration files. You can set the default configuration file and specify personalized configuration files.

After installation, run the command for initializing the configuration file for different applications:

::: code-group

```sh [Windows]
$ f2 apps --init-config apps.yaml
```

```sh [Linux]
$ f2 apps --init-config apps.yaml
```

```sh [MacOS]
$ f2 apps --init-config apps.yaml
```
:::

You will be prompted with a few simple questions:

::: tip Generate configuration files for different applications

A list of supported applications is currently available. Simply generate the configuration file based on the desired application.

Initialize the configuration file for "Douyin" application:
```sh
$ f2 dy --init-config dy.yaml
```
:::

::: tip Path parameter for configuration files
The configuration file path supports both absolute and relative paths. Initializing the configuration file forcefully overwrites it and does not automatically backup.
:::


### Configuration File

The default configuration file (./conf/app.yaml) is a yaml file with a basic structure:

```yaml
douyin:
  headers:
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0
    Referer: https://www.douyin.com/

  cookie:
  cover: yes
  desc: yes
  folderize: yes
  interval: 0
  languages: zh_CN
  timeout: 10
  max_retries: 5
  max_connections: 5
  max_tasks: 5
  page_counts: 5
  max_counts: 0
  ......
```
::: tip Meaning of these configurations
You can get help information about them from the CLI:

```sh
$ f2 apps -h
```

Where `f2/conf/app.yaml` is the default configuration file for F2, if you need to use a customized configuration file please follow the [Configuration Reference](/site-config).


:::


## Startup and Execution

For example, I want to download all works published by a user on "Douyin" using the default configuration:

::: code-group

```sh [Windows]
$ f2 dy -c f2/conf/app.yaml
```

```sh [Linux]
$ f2 dy -c f2/conf/app.yaml
```

```sh [MacOS]
$ f2 dy -c f2/conf/app.yaml
```
:::

The download mode, user, cookie, and other information are all saved in the default configuration file. You can also use CLI parameters to change it to download all works `like` by a user on `Douyin` without modifying the configuration file:

::: code-group

```sh [Windows]
$ f2 dy -M like -c f2/conf/app.yaml
```

```sh [Linux]
$ f2 dy -M like -c f2/conf/app.yaml
```

```sh [MacOS]
$ f2 dy -M like -c f2/conf/app.yaml
```
:::


It is also possible to enter different links depending on the mode, for example, to download `single` works by `like' users:

::: code-group

```sh [Windows]
$ f2 dy -M one -u https://v.douyin.com/iRNBho6u/ -c conf/app.yaml
```

```sh [Linux]
$ f2 dy -M one -u https://v.douyin.com/iRNBho6u/ -c conf/app.yaml
```

```sh [MacOS]
$ f2 dy -M one -u https://v.douyin.com/iRNBho6u/ -c conf/app.yaml
```
:::

F2 intelligently recognizes links in confusing text, and also supports the input of short and long links.

::: details Supported Link Formats

```sh
# 带有其他信息的链接
4.38 12/09 q@e.BG zTL:/ 你别太帅了郑润泽# 现场版live # 音乐节 # 郑润泽  https://v.douyin.com/iR2nEj44/ 复制此链接，打开Dou音搜索，直接观看视频！
7.64 gOX:/ w@f.oD 05/14 世界这本书 又多读了一页。冰岛????旅行记# 冰岛  https://v.douyin.com/iR2syBRn/ 复制此链接，打开Dou音搜索，直接观看视频！

# 短链
https://v.douyin.com/iRNBho6u/  # 视频
https://v.douyin.com/iR2syBRn/  # 图集
https://v.douyin.com/iRxM1Xut/  # 直播

# 完整链接
https://www.douyin.com/video/7298145681699622182  # 视频
https://www.douyin.com/note/7285559250619813155   # 图集
https://live.douyin.com/895627289314              # 直播
```
:::

::: tip Note that
In CLI mode, text with additional information needs to be wrapped in quotes:

```sh [Windows]
$ f2 dy -M one -u '7.64 gOX:/ w@f.oD 05/14 世界这本书 又多读了一页。冰岛????旅行记# 冰岛  https://v.douyin.com/iR2syBRn/ 复制此链接，打开Dou音搜索，直接观看视！
' -c conf/app.yaml
```
:::

The CLI parameter has the highest priority and allows you to set different download modes and links without modifying the configuration file.
For more detailed information on the "Jitterbug" CLI commands, see [CLI reference](/cli).


## What's next?

- For more advanced uses of F2, see this document's "[advanced-use](./advance-guide)" in this document.

- To learn more about what F2 can do, such as asynchronous data generators, see this document's "[guide](./guide/what-is-f2)" section of this document. Learn more about the developer's approach.

- If you want to further customize the parsed data explore how to [extend the default data model]() or [build custom model]() (to be updated in the next release).

- If you're a developer be sure to read this [guide](./guide/what-is-f2).
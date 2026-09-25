# Quick Start

::: info Tip
This page is still under development and may contain inaccuracies. Contributions are welcome at the bottom of the page.
The English version is being translated.
:::

## Start and Run

`F2` is a flexible *asynchronous* download library. It helps users and developers fetch data from multiple platforms with a single command, either via the CLI or directly in code.

![cli-start](/f2-help.png)

To see the help for an app, put the app name or its short name after `f2` and add `-h`, for example for Douyin:

::: code-group

```sh [Windows]
$ f2 dy -h
```

```sh [Linux]
$ f2 dy -h
```

```sh [MacOS]
$ f2 dy -h
```
:::

Supported apps and short names: `douyin` (`dy`), `tiktok` (`tk`), `weibo` (`wb`), `twitter` (`x`) and `bark` (`bk`). Run `f2 -h` to list all apps.

## Start with Configuration File

- Please refer to the 「[Configuration File](/site-config)」 section in this documentation. It contains detailed information about configuration files.

## CLI Mode

![cli-start](/douyin/cli-start.png)

![cli-start-2](/douyin/cli-start-2.png)

## API Call

![code-start](/douyin/code-start.png)

![code-start-2](/douyin/code-start-2.png)

## What's Next?

- Unsure how to configure? See the [Configuration File](/site-config) section.
- Looking for advanced usage? Check the [Advanced Guide](/advance-guide).
- To learn more features, such as asynchronous generators, read the [Guide](/guide/what-is-f2).
- Need custom data models? Explore [Extend Default Data Models](/en/guide/custom-model).
- Developers should read the full [guide](/guide/what-is-f2).

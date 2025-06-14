# Configuration file

::: warning important
Read this chapter carefully to understand how `F2` configuration files work and how to operate them efficiently.
:::

## Main configuration file

`F2` uses several types of configuration files:

- **App low-frequency/main configuration file** (`app.yaml`): stores settings that rarely change, such as `cookie`, filename templates, download paths, and network timeouts.
- **F2 configuration file** (`conf.yaml`): global settings like computation parameters and proxies for each app.
- **App default configuration file** (`defaults.yaml`): initialization templates for each app. <font color=red><u>**Do not modify this file**</u></font>.
- **Test configuration file** (`test.yaml`): configuration for the project's tests.
- **Custom configuration files**: high-frequency settings tailored for personal use that override defaults.

::: info :bulb: What is yaml?
Presents the data serialization format file in an outline-like indentation manner, [what is yaml?](https://zh.wikipedia.org/wiki/YAML).
:::

**App low-frequency/main configuration file (app.yaml)**: used to save all app configurations that do not change frequently, such as `cookie`, `file name template`, `download path`, `connection timeout`, `Number of timeout retries`, etc.

**F2 configuration file (conf.yaml)**: used to save the configuration of `F2`, such as `computation parameters` and `agent` of different apps.

**App default configuration file (defaults.yaml)**: used to save the initialization default configuration template of each app, <font color=red><u>**_Please do not modify and use it_**</u> </font>.

**Test Configuration File (test.yaml)**: Used to save the configuration of test cases for `F2`, it is necessary to configure it before running `pytest`.

::: code-group
<<< @../../f2/conf/app.yaml
<<< @../../f2/conf/conf.yaml
<<< @../../f2/conf/defaults.yaml
<<< @../../f2/conf/test.yaml
:::

With high- and low-frequency parameters separated, you only maintain long-lived settings like `cookie` in `app.yaml`. Frequently changed options—such as home page links or download modes—are placed in custom configuration files. This approach simplifies maintenance when managing multiple profiles.

Useful links:

- [Initialize configuration file](#initialize-configuration-file)
- [Custom configuration file](#custom-configuration-file)
- [Configure cookies](#configure-cookies)
- [Advanced usage](./advance-guide)

- If you already know how to use configuration files, you can skip this chapter and view [Advanced Usage](./advance-guide).

## Initialize configuration file

Check out the list of currently supported apps

```bash
$ f2 -h
```

After `F2` is installed, the first step is to run the app’s initialization configuration file command:

::: code-group

```sh [Windows]
$ f2 apps --init-config my_apps.yaml
```

```sh [Linux]
$ f2 apps --init-config my_apps.yaml
```

```sh [MacOS]
$ f2 apps --init-config my_apps.yaml
```
:::

`my_apps.yaml` is the custom configuration file of the app.

Then check the [Command Line Guide](guide/what-is-f2) of the **app** and configure your custom configuration file according to the documentation, otherwise it will not work properly.

::: tip :bulb: You will be greeted with a few simple questions

1. **Are both complete app names and abbreviated names supported?**

Yes, both full app name and short name are supported. For example: `douyin` and `dy`, `tiktok` and `tk`.

::: code-group

  ```sh [dy]
  $ f2 dy/douyin --init-config dy.yaml
  ```
  ```sh [tk]
  $ f2 tk/tiktok --init-config tk.yaml
  ```

2. **Does the configuration file support relative paths?**

Configuration file paths support `absolute` and `relative` paths. The initialization configuration file is forced to be overwritten and will not be automatically backed up.

3. **Can't find the main configuration file?**

Please refer to: [location of configuration file](#location of configuration file).
:::

## Custom configuration file

Since the configuration file of `F2` adopts separate design for high and low frequency parameters, this means that you can set `different configuration files` for the `same app`.

You can set only one parameter in a custom configuration file, or you can set parameters that you need to modify frequently.

### Flexible configuration for multiple users

For example, I follow 3 users. Among them are A's `Home Page Works', B's `Like Page Works', and C's `Live Broadcast'. Then I can configure a dedicated profile for each user.

In `F2`, first configure `cookie` and other parameters you need to set in the **app low-frequency configuration file (app.yaml)**. Then create exclusive configuration files for users A, B, and C in other directories, and only need to configure the parameters that are not set in the low frequency.

As shown in the two `high frequency parameters` below, they are the download modes required by different users.

::: code-group

```yaml [User A’s homepage post]
douyin:
  # 浩子
  url: https://www.douyin.com/user/MS4wLjABAAAAu8qwDm1-muGuMhZZ-tVzyPVWlUxIbQRNJN_9k83OhWU?vid=7263127189829307659
  # Homepage post
  mode: post
```

```yaml [User B’s favorite page post]
douyin:
  #小布丁
  url: https://www.douyin.com/user/MS4wLjABAAAA35iXl5qqCbLKY99pUvxkXzvpSXi8jgUbJ0zR4EuTpcHcS8PHaEb6G9yB6iKR0dNl?vid=7240082457372937511
  # Like the post
  mode: like
```

```yaml [User C live broadcast]
  douyin:
  # 醒子8ke
  url: https://live.douyin.com/775841227732
  # Live mode
  mode: live
```
:::

::: tip :bulb: Description
This is just an example. In fact, user B's like page is not open, and user C may not live broadcast. Everything is set according to the actual situation, Do whatever you want.
:::

Then you can open the terminal and directly enter the path to the custom configuration file to download it with one click. The remaining low-frequency parameters will be automatically merged, so there is no need to worry.

::: code-group

```bash [User A]
$ f2 dy -c X:\A.yaml
```

```bash [user B]
$ f2 dy -c X:\B.yaml
```

```bash [user C]
$ f2 dy -c X:\C.yaml
```
:::

Isn't it very convenient and easy to manage🤭, you can add your favorite user profiles and set your desired download mode at any time.

::: warning configuration priority
- The `CLI` parameter has the highest priority, the `custom configuration file` has the second priority, and the `app low-frequency configuration file (app.yaml)` has the lowest priority.
- `CLI` > `Custom configuration file` > `Apply low-frequency configuration file (app.yaml)`.
- High-frequency parameters will overwrite low-frequency parameters, and unset parameters will not be overwritten.
- To learn more about `CLI` parameters, see [CLI Reference](/cli).
:::

## Configure Cookies

Through simple configuration, users and developers can get started with `F2` immediately. Just pass the `--update-config` command to save `cookie` to the main configuration file.

Or use the `--auto-cookie` command to automatically obtain it from the browser. :warning: **See red warning below** :warning:.

::: code-group

```sh [--update-config]
$ f2 dy -k "cookie copied from browser" -c app.yaml --update-config
```

```sh [--auto-cookie]
$ f2 dy -c app.yaml --auto-cookie edge
```
:::

Of course, if you don’t want to make mistakes, manually copy the `cookie` in the browser, and then use the `--update-config` command to save it to the main configuration file. The manual copying operation can be done in Google.

::: warning :warning: Important reminder
- When updating the configuration file, the original configuration file will be backed up in the same directory. The backup file name is `*.yaml.bak` to facilitate rollback.
- If `--auto-cookie` does not specify the `-c` parameter, it will be saved directly to the **low-frequency configuration file (app.yaml)**.
- `cookies` can also be saved to custom configuration files. It depends on your usage habits. For beginners, please strictly follow the instructions in the document.
- The `--update-config` command and the `--auto-cookie` command will overwrite the `cookie` in the main configuration file, please use it with caution.
- The `--update-config` command needs to specify the `-c` parameter, otherwise an error will be reported.
:::

:::danger :fire: Unable to use `--auto-cookie` command? :fire:
Due to the update of `Chromium` security policy, the `Cookie` encryption version has been upgraded to `V20`. As a result, the `--auto-cookie` command is temporarily unable to obtain browser `cookies` released after `August 15, 2024`.

- Please update `F2` to the latest version to get the latest fixes.
- If you do not want to upgrade, you can refer to the following `PR` to manually install the repaired version of dependencies.
- [borisbabic/browser_cookie3#215](https://github.com/borisbabic/browser_cookie3/pull/215)
- As of `2024/dec/23` the fixed version still cannot support browsers with the latest `Chromium` kernel version, please use other browsers or downgrade the browser version to `v128`.
:::

## Location of configuration file

You can find them in the `x:\xxxxxxx\Python\Lib\site-packages\f2\conf\` folder.

::: tip :bulb: Tips
If you cannot find the configuration folder path, you can enter it in the terminal

::: code-group
```sh [Windows]
$ pip show f2
```

```sh [Linux]
$ pip3 show f2
```

```sh [MacOS]
$ pip3 show f2
```
Then check `Location` and find the configuration file in that directory.
:::

## What's next?

- For more details on CLI commands, see [CLI Reference](/cli).

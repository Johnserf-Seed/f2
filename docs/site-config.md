# 配置文件

::: warning 重要
请详细的阅读本章节，它将会帮助你快速上手 `F2` 配置文件与操作。
:::

## 主配置文件

`F2` 配置文件核心由三部分组成，`应用低频/主配置文件(app.yaml)`，`F2配置文件(conf.yaml)`，`应用默认配置文件(defaults.yaml)`。

额外的部分是你的 `应用高频/自定义配置文件`，它可以涵盖 `应用默认配置文件` 中的所有参数。

以及 `测试配置文件(test.yaml)`，负责 `F2` 的测试用例的配置。

::: info :bulb: 什么是 yaml？
用类似大纲的缩进方式呈现数据序列化的格式文件，[what is yaml?](https://zh.wikipedia.org/wiki/YAML)。
:::

**应用低频/主配置文件(app.yaml)**：用来保存所有应用不常变动的配置，例如的 `cookie`、`文件名模板`、`下载路径`、`连接超时时间`、`超时重试次数`等。

**F2配置文件(conf.yaml)**：用来保存 `F2` 的配置，例如不同应用的 `计算参数` 和 `代理`。

**应用默认配置文件(defaults.yaml)**：用来保存各个app的初始化默认配置模板，<font color=red><u>**_请不要修改与使用它_**</u></font>。

**测试配置文件(test.yaml)**：用来保存 `F2` 的测试用例的配置，运行 `pytest` 前务必先配置好。

::: code-group
<<< @../../f2/conf/app.yaml
<<< @../../f2/conf/conf.yaml
<<< @../../f2/conf/defaults.yaml
<<< @../../f2/conf/test.yaml
:::

高低频参数分离意味着当创建的自定义配置文件比较多的情况下无需修改每一个自定义配置文件中的 `cookie`，只需要修改**应用低频配置文件(app.yaml)** 中的 `cookie` 即可。

将高频修改的参数 `主页链接`、`下载模式` 等，设置在你的自定义配置中，即可灵活调用下载不同用户的不同类型作品。

- 如何初始化配置文件？请查阅[初始化配置文件](#初始化配置文件)。

- `F2` 支持多用户个性化配置文件，请按照[自定义配置文件](#自定义配置文件)来进行配置。

- 如何配置Cookie？请查阅[配置Cookie](#配置Cookie)。

- 如果你已经知悉如何使用配置文件，那么可以跳过该章查看[进阶用法](./advance-guide)。

## 初始化配置文件

查看目前支持的应用列表

```bash
$ f2 -h
```

`F2` 安装完成后，第一步就是运行应用的初始化配置文件命令:

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

`my_apps.yaml` 就是该应用的自定义配置文件。

然后查阅该**应用**的[命令行指引](guide/what-is-f2)，并根据文档的说明来配置你的自定义配置文件，否则无法正常使用。

::: tip :bulb: 迎接你的将是几个简单的问题

1. **完整的应用名和简写名都支持吗？**

是的，完整的应用名和简名都支持。例如：`douyin` 与 `dy`、`tiktok` 与 `tk`。

::: code-group

  ```sh [douyin]
  $ f2 dy/douyin --init-config dy.yaml
  ```
  ```sh [tiktok]
  $ f2 tk/tiktok --init-config tk.yaml
  ```

2. **配置文件支持相对路径吗？**

配置文件路径支持 `绝对` 与 `相对` 路径。初始化配置文件是强制覆盖，不会 `自动备份`。

3. **找不到主配置文件？**

请查阅：[配置文件的位置](#配置文件的位置)。
:::

## 自定义配置文件

由于 `F2` 的配置文件采用高低频参数分离式设计，这意味着你可以为`相同的应用`设置`不同的配置文件`。

你可以只设置一个参数在自定义配置文件中，也可以设置你需要高频修改的参数。

### 多用户灵活配置

举个例子，我关注了3个用户。其中有A的 `主页作品`、B的 `喜欢页作品`、C的 `直播`。那么我可以为每个用户配置一个专属的配置文件。

在 `F2` 中，先把**应用低频配置文件(app.yaml)** 中 `cookie` 与其他你需要设置的参数配置好。再在其他目录下建立A、B、C用户的专属配置文件，只需配置上低频中没有设置的参数。如下面2个 `高频参数` 所示，为不同用户所需的下载模式。

::: code-group

```yaml [用户A主页作品]
douyin:
  # 浩子
  url: https://www.douyin.com/user/MS4wLjABAAAAu8qwDm1-muGuMhZZ-tVzyPVWlUxIbQRNJN_9k83OhWU?vid=7263127189829307659
  # 主页作品
  mode: post
```

```yaml [用户B喜欢页作品]
douyin:
  # 小布丁
  url: https://www.douyin.com/user/MS4wLjABAAAA35iXl5qqCbLKY99pUvxkXzvpSXi8jgUbJ0zR4EuTpcHcS8PHaEb6G9yB6iKR0dNl?vid=7240082457372937511
  # 喜欢作品
  mode: like
```

```yaml [用户C直播]
douyin:
  # 醒子8ke
  url: https://live.douyin.com/775841227732
  # 直播模式
  mode: live
```
:::

::: tip :bulb: 说明
这只是举例，实际上用户B的喜欢页没有开放，用户C也不一定直播，一切根据实际情况来设置，Do whatever you want。
:::

随后你便可以开启终端，并直接输入自定义配置文件路径即可一键下载，剩下的低频参数会自动合并，无需担心。

::: code-group

```bash [用户A]
$ f2 dy -c X:\A.yaml
```

```bash [用户B]
$ f2 dy -c X:\B.yaml
```

```bash [用户C]
$ f2 dy -c X:\C.yaml
```
:::

是不是非常方便且容易管理🤭，你可以随时添加喜欢的用户配置文件并设置你所需的下载模式。

::: warning 配置优先级
- `CLI`参数优先级最高，`自定义配置文件`优先级次之，`应用低频配置文件(app.yaml)`优先级最低。
- `CLI` > `自定义配置文件` > `应用低频配置文件(app.yaml)`。
- 高频参数会覆盖低频参数，未设置的参数不会被覆盖。
- 要想了解更多的`CLI`参数，请查阅[CLI 参考](/cli)。
:::

## 配置Cookie

通过简单的配置，用户与开发者就可以立马上手 `F2`。只需通过 `--update-config` 命令就可以保存 `cookie` 到主配置文件中。

或者使用 `--auto-cookie` 命令自动从浏览器获取。 :warning: **请查看下文的红色警告** :warning:。

::: code-group

```sh [--update-config]
$ f2 dy -k "从浏览器中复制的cookie" -c app.yaml --update-config
```

```sh [--auto-cookie]
$ f2 dy -c app.yaml --auto-cookie edge
```
:::

当然不想出错就手动复制浏览器中的 `cookie`，然后使用 `--update-config` 命令保存到主配置文件中。手动复制的操作百度一下就可以了。

::: warning :warning: 重要提示
- 更新配置文件的同时将会在同目录里备份原配置文件，备份文件名为 `*.yaml.bak`，方便回滚。
- 如果 `--auto-cookie` 不指定 `-c` 参数，将直接保存至**低频配置文件(app.yaml)** 中。
- `cookie` 也可以保存到自定义的配置文件中。随你的使用习惯，小白请严格按照文档的说明来操作。
- `--update-config` 命令与 `--auto-cookie` 命令会覆盖主配置文件中的 `cookie`，请谨慎使用。
- `--update-config` 命令需要指定 `-c` 参数，否则会报错。
:::

::: danger :fire: 无法使用 `--auto-cookie` 命令？ :fire:
由于 `Chromium` 安全策略的更新，将 `Cookie` 加密版本升级到了 `V20`。导致 `--auto-cookie` 命令暂时无法获取 `2024 年 8 月 15 日` 之后发布的浏览器 `Cookie`。

- 请更新 `F2` 到最新版本，以获取最新的修复补丁。
- 如果您不希望升级，可以参考以下 `PR`，手动安装修复版本的依赖。
- [borisbabic/browser_cookie3#215](https://github.com/borisbabic/browser_cookie3/pull/215)
- 截至 `2024/dec/23` 修复版本仍无法支持最新 `Chromium` 内核版本的浏览器，请使用其他浏览器或降级浏览器版本到 `v128` 之前。
:::

## 配置文件的位置

你可以在 `x:\xxxxxxx\Python\Lib\site-packages\f2\conf\` 文件夹中找到它们。

::: tip :bulb: 提示
如果找不到配置文件夹路径可以在终端输入

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
然后查看 `Location`，并在该目录下找到配置文件。
:::

## 下一步是什么？

- 更多 CLI 命令的详细信息，请查阅 [CLI 参考](/cli)。
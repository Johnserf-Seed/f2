# 配置文件

::: warning 重要
请详细的阅读本章节，它将会帮助你快速上手 `F2` 配置文件与操作。
:::

## 主配置文件

`F2` 是一个灵活的异步下载库。你可以使用默认的配置文件，同时也能指定个性化的配置文件。

`F2` 默认的配置文件(`f2/conf/app.yaml`)是一个yaml文件。它非常重要，用来保存各个app基础的配置。

::: info 什么是yaml？
用类似大纲的缩进方式呈现数据序列化的格式文件，[yaml](https://zh.wikipedia.org/wiki/YAML)。
:::

::: code-group
<<< @../../f2/conf/app.yaml
:::

F2 配置文件独立于 CLI 命令参数且具有`最低优先`。这意味只需要一个主配置存`cookie`再用 CLI 命令或者用户的自定义配置即可下载不同的用户作品。

- 如何初始化配置文件？请查阅[初始化配置文件](#初始化配置文件)。

- 如何配置cookie？请查阅[配置cookie](#配置cookie)。

- F2 支持多用户个性化配置文件，请按照[自定义配置文件](#自定义配置文件)来进行配置。

- 如果你已经知悉如何使用配置文件，那么可以跳过该章查看[进阶用法](./advance-guide)。


## 初始化配置文件

查看目前支持的应用列表
```bash
$ f2 -h
```

F2 安装完成后，运行不同应用的启动初始化配置文件命令:

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


迎接你的将是几个简单的问题:

::: tip 完整的应用名和简写名都支持吗？

是的，完整的应用名和简名都支持。例如：`douyin`与`dy`、`tiktok`与`tk`。
```sh
$ f2 dy --init-config dy.yaml
```
与
```sh
$ f2 douyin --init-config dy.yaml
```
:::

::: tip 配置文件支持相对路径吗？
配置文件路径支持`绝对`与`相对`路径。初始化配置文件是强制覆盖，不会`自动备份`。
:::

::: tip 找不到主配置文件？
请查阅[配置文件的位置](#配置文件的位置)。
:::


## 配置cookie

通过简单的配置，用户与开发者就可以立马上手 `F2`。只需通过 `--update-config` 命令就可以保存`cookie`到主配置文件或者使用`--auto-cookie`命令自动从浏览器获取并填写。

::: code-group

```sh [--update-config]
$ f2 dy -k "从浏览器中复制的cookie" -c conf/app.yaml --update-config
```

```sh [--auto-cookie]
$ f2 dy -c conf/app.yaml --auto-cookie edge
```
:::

当然不想出错就手动复制浏览器中的`cookie`，然后使用`--update-config` 命令保存到主配置文件中。手动复制的操作百度一下就可以了。

::: warning 重要
- 更新配置文件的同时将会在同目录里备份原配置文件，备份文件名为`*.yaml.bak`，方便出错回滚。
- 不一定非要保存到主配置文件中，你也可以保存到自定义的配置文件中。随你的使用习惯，小白请按照文档的说明来操作。
- `--update-config` 命令与`--auto-cookie`命令会覆盖主配置文件中的`cookie`，请谨慎使用。
- `--update-config` 命令需要指定`-c`参数，否则会报错。
:::


## 配置文件的位置

你可以可以在`x:\xxxxxxx\Python\Lib\site-packages\f2\conf\app.yaml`中找到它。

::: tip 提示
如果找不到配置文件可以在终端输入

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
然后查看Location，并在该目录下找到配置文件。
:::


## 自定义配置文件

由于 F2 采用 app 插件分离式设计，这意味着你可以为相同的 app 配置不同模式的配置文件。

一头雾水🎃？ 接着看。


### 多用户配置

举个例子，我关注了3个用户其中有A的主页跳舞作品、B的喜欢页作品、C的直播。以往的`TikTokDownload`项目设计冗余，一次性实现起来较复杂。

在 F2 中，先把主配置文件中`cookie`与其他你需要设置的命令配置好。再在其他目录下建立A、B、C用户的专属配置文件，只需配置不同你所需的的下载模式。

::: code-group

```yaml [用户A]
douyin:
  # 浩子
  url: https://www.douyin.com/user/MS4wLjABAAAAu8qwDm1-muGuMhZZ-tVzyPVWlUxIbQRNJN_9k83OhWU?vid=7263127189829307659
  # 主页作品
  mode: post
```

```yaml [用户B]
douyin:
  # 小布丁
  url: https://www.douyin.com/user/MS4wLjABAAAA35iXl5qqCbLKY99pUvxkXzvpSXi8jgUbJ0zR4EuTpcHcS8PHaEb6G9yB6iKR0dNl?vid=7240082457372937511
  # 喜欢作品
  mode: like
```

```yaml [用户C]
douyin:
  # 醒子8ke
  url: https://live.douyin.com/775841227732
  # 直播模式
  mode: live
```
:::

::: tip 说明
只是举例，实际上用户B的喜欢页没有开放，用户C也不一定直播，一切根据你的喜好来设置。
:::

随后你便可以开启终端，并输入不同的配置文件路径即可一键下载。

::: code-group

```bash [用户A]
$ f2 dy -c C:\Users\JohnserfSeed\Desktop\A.yaml
```

```bash [用户B]
$ f2 dy -c C:\Users\JohnserfSeed\Desktop\B.yaml
```

```bash [用户C]
$ f2 dy -c C:\Users\JohnserfSeed\Desktop\C.yaml
```
:::

是不是非常方便且容易管理🤭，你可以随时添加喜欢的用户配置文件并设置你所需的下载模式。

### CLI临时配置

CLI 参数命令优先级最高，所以在不修改配置文件的情况下就可以使用 CLI 参数更改为下载「抖音」用户`喜欢`的所有作品。因此也可以在 CLI 中临时下载A的直播，B的作品与C的喜欢。

::: code-group

```bash [用户A]
$ f2 dy -c C:\Users\JohnserfSeed\Desktop\A.yaml -M live -u https://live.douyin.com/xxxxxxxxx
```

```bash [用户B]
$ f2 dy -c C:\Users\JohnserfSeed\Desktop\B.yaml -M post
```

```bash [用户C]
$ f2 dy -c C:\Users\JohnserfSeed\Desktop\C.yaml -M like
```
:::

赶快试试吧！

::: tip 说明
之后的版本会简化操作。不需要再指定该用户的直播间就可以切换下载该用户直播的模式。
更多的 CLI 命令请查阅 [CLI 参考](/cli)。
:::

::: warning 重要
- 命名方式也不受限制，你可以设置`dy-A.yaml`、`dy-B.yaml`、`tk-A.yaml`、`tk-B.ymal`用以区分不同app的用户配置。
- 配置的操作是通用的，举例用的是douyin的配置文件，tiktok与其他 F2 应用的配置文件的操作是一模一样的。
:::


## 拓展

如果不想设置很多配置文件，那就使用主配置。

下载「抖音」用户`发布`的所有作品，只需要在主配置文件中设置`mode: post`即可。

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

下载「抖音」用户`喜欢`的所有作品，CLI 中设置`mode: like`即可。

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

下载「抖音」用户`单个`的作品:

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

F2 会智能的识别出混乱文本中的链接，同时也支持长短链的输入。

::: details 支持的链接格式

<<< @/snippets/douyin/support-link.md
:::

::: tip 需要注意的是
在CLI模式下，带有其他信息的文本需要用英文引号将其完整包裹:

```sh [Windows]
$ f2 dy -M one -u '7.64 gOX:/ w@f.oD 05/14 世界这本书 又多读了一页。冰岛????旅行记# 冰岛  https://v.douyin.com/iR2syBRn/ 复制此链接，打开Dou音搜索，直接观看视！
' -c conf/app.yaml
```
:::

## 下一步是什么？

- 更多 CLI 命令的详细信息，请查阅 [CLI 参考](/cli)。

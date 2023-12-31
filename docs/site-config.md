# 配置文件

默认的配置文件(`./conf/app.yaml`)是一个[yaml](https://en.wikipedia.org/wiki/yaml)文件。

如果你已经知悉如何使用配置文件，那么可以跳过该章查看[进阶用法](./advance-guide)。

::: tip 找不到主配置文件？
请查看开发指南中的[#配置文件](./guide/what-is-f2)。
:::

::: warning 配置的操作是通用的
举例用的是douyin的配置文件，tiktok配置文件的操作是一模一样的。
:::

## 自定义配置文件

由于 f2 采用 app 插件分离式设计，这意味着你可以为每一个不同的 app 设置不同的配置文件。也可以为相同的 app 配置不同下载模式的配置文件。

::: code-group

```yaml [douyin]
douyin:
  headers:
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36
    Referer: https://www.douyin.com/

  cookie: ""
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

```yaml [tiktok]
tiktok:
  headers:
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36
    Referer: https://www.douyin.com/

  cookie: ""
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

```yaml [twitter]
......
```

```yaml [...]
......
```
:::


重点是配置文件独立于 cli 参数且具有最高优先，这意味只需要一个主配置存账号cookie，用 cli 命令或者单独用户的配置即可下载不同用户的作品。

一头雾水🎃？ 接着看。

## 多用户配置

举个例子，我关注了3个用户其中有A的主页跳舞作品、B的喜欢页作品、C的直播。传统的`TikTokDownload`项目一次性实现起来较复杂。

在 f2 中，先修改`./conf/app.yaml`，把cookie与其他你需要设置的命令填好。再在其他目录下建立A、B、C用户的专属配置文件，并只配置不同的下载需求。

::: code-group

```yaml [用户A]
douyin:
  # 浩子
  url: https://www.douyin.com/user/MS4wLjABAAAAu8qwDm1-muGuMhZZ-tVzyPVWlUxIbQRNJN_9k83OhWU?vid=7263127189829307659
  mode: post
```

```yaml [用户B]
douyin:
  # 小布丁
  url: https://www.douyin.com/user/MS4wLjABAAAA35iXl5qqCbLKY99pUvxkXzvpSXi8jgUbJ0zR4EuTpcHcS8PHaEb6G9yB6iKR0dNl?vid=7240082457372937511
  mode: like
```

```yaml [用户C]
douyin:
  # 醒子8ke
  url: https://live.douyin.com/775841227732
  mode: live
```
:::

::: tip 说明
只是举例，实际上用户B的喜欢页没有开放，用户C也不一定直播，一切根据你的喜好来设置。
:::

随后你便可以开启终端，并输入不同的命令即可一键下载。

::: code-group

```bash [用户A]
$ f2 -d dy -c C:\Users\JohnserfSeed\Desktop\A.yaml
```

```bash [用户B]
$ f2 -d dy -c C:\Users\JohnserfSeed\Desktop\B.yaml
```

```bash [用户C]
$ f2 -d dy -c C:\Users\JohnserfSeed\Desktop\C.yaml
```
:::

是不是非常方便且容易管理，你可以随时添加喜欢的用户并设置不同的下载模式。也可以在 cli 中临时下载A的直播，B的作品与C的喜欢。

::: code-group

```bash [用户A]
$ f2 -d dy -c C:\Users\JohnserfSeed\Desktop\A.yaml -M live -u https://live.douyin.com/xxxxxxxxx
```

```bash [用户B]
$ f2 -d dy -c C:\Users\JohnserfSeed\Desktop\B.yaml -M post
```

```bash [用户C]
$ f2 -d dy -c C:\Users\JohnserfSeed\Desktop\C.yaml -M like
```
:::

::: tip 说明
之后的版本会简化操作。不需要再指定该用户的直播间就可以切换下载该用户直播的模式。
更多的 cli 命令请查阅 [CLI 参考](/reference/cli)。
:::

::: warning 命名方式也不受限制
你可以设置`dy-A.yaml`、`dy-B.yaml`、`tk-A.yaml`、`tk-B.ymal`用以区分不同app的用户配置。
:::

赶快试试吧！

## 拓展

如果不想设置很多配置文件，例如我使用默认配置下载「抖音」用户`发布`的所有作品:

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

下载模式，下载用户，cookie等信息都保存在了默认的配置文件中。你也可以在不修改配置文件的情况下使用CLI参数更改为下载「抖音」用户`喜欢`的所有作品:

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

也可以依据模式输入不同的链接，例如下载「抖音」用户`单个`的作品:

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

::: tip 需要注意的是
在CLI模式下，带有其他信息的文本需要用英文引号将其完整包裹:

```sh [Windows]
$ f2 dy -M one -u '7.64 gOX:/ w@f.oD 05/14 世界这本书 又多读了一页。冰岛????旅行记# 冰岛  https://v.douyin.com/iR2syBRn/ 复制此链接，打开Dou音搜索，直接观看视！
' -c conf/app.yaml
```
:::

CLI参数拥有最高优先，可以在不修改配置文件的情况下设置不同的下载模式和链接。
更多「抖音」CLI命令的详细信息，请查阅 [CLI 参考](./reference/cli)。
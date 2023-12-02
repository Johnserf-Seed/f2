# 快速使用

## 配置

### 第一次设置

`F2` 是一个依赖配置文件运行的异步库。你可以设置默认的配置文件，同时也可以指定个性化的配置文件。

安装完成后，运行不同应用的启动初始化配置文件命令:

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

::: tip 生成不同应用的配置文件

目前支持的[应用列表]()，只需要根据所需的应用名生成即可。
初始化「抖音」相关配置文件:
```sh
$ f2 dy --init-config dy.yaml
```
:::

::: tip 配置文件的路径参数
配置文件路径支持`绝对`与`相对`路径。初始化配置文件是强制覆盖，不会`自动备份`。
:::


### 配置文件

默认的配置文件(`./conf/app.yaml`)是一个[yaml](https://en.wikipedia.org/wiki/yaml)文件，基本的结构:

```yaml
douyin:
  headers:
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36
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
::: tip 这些配置的含义
可以从CLI获取有关的帮助信息:

```sh
$ f2 apps -h
```

其中`f2/conf/app.yaml`是F2的默认配置文件，如果需要使用自定义配置文件请按照[配置参考](./reference/site-config)来进行配置。


:::


## 启动和运行

例如我使用默认配置下载「抖音」用户`发布`的所有作品:

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


## 下一步是什么？

- 想知道 F2 还有哪些进阶用法，请参阅本文档的「[进阶用法](./advance-guide)」

- 要进一步了解 F2 可以做什么，例如异步数据生成器，请参阅本文档的 「[指南](./guide/what-is-f2)」 部分。了解更多开发者的方法。

- 如果你想进一步定制解析的数据请探索如何 [扩展默认数据模型]() 或 [构建自定义模型]() （下个版本更新）。

- 如果你是开发者请务必仔细阅读该[指南](./guide/what-is-f2)。
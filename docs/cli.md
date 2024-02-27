# 命令行

`F2` 配置文件独立于 CLI 命令参数且`最低优先`。

## CLI临时配置

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
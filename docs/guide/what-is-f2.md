# 开发者必看

如果你是开发者或贡献着，开发前请阅读此文档再查看接口。

## 指定配置文件

开发者可以直接定义自己的配置文件，然后在测试时通过 `-c` 参数指定配置文件的路径，例如：

```bash
f2 dy -c conf/app.yaml
```
也可以在代码中指定配置文件的路径，例如：

<<< @/snippets/set-debug.py#set-config-snippet{3}

## 设置调试日志级别

<<< @/snippets/set-debug.py#set-debug-snippet{6}

支持代码 `接口` 模式的同时也支持在 `CLI` 模式中加上 `-d` 来指定记录日志级别。可选的参数 `DEBUG`，`INFO`，`WARNING`，`ERROR`。

```bash
$ f2 -d WARNING dy -M post
```

![set-debug](/douyin/set-debug.png)

::: tip :bulb: 提示
`F2` 的日志会自动脱敏：配置里的 `cookie`、`key`、`token`、密码以及代理地址中的账号密码在写入控制台、文件或向上传播到你自己的日志处理器之前就会被打码（只保留开头几个字符和长度）。作为库使用时，如需在自己的日志里打印配置，可以用 `from f2.log.redact import redact_config` 先脱敏。
:::

## 日志输出到控制台

作为库导入 `F2` 时，日志默认只输出到控制台，不会在当前目录创建 `logs` 目录，也不会清理旧日志。如需同时写入日志文件，调用 `log_setup` 并指定 `log_path`（默认 `./logs`，传 `None` 表示不写文件）；`CLI` 启动时会自动完成这一配置。

<<< @/snippets/set-debug.py#log-2-console-snippet{6}

![log-2-console](/douyin/log-2-console.png)

::: tip :bulb: 提示
如果你想要输出到控制台的日志更加详细，可以使用 `DEBUG` 级别。`log_setup` 在同一进程内只会生效一次，之后再调用会直接返回已配置好的 `logger`。异常堆栈单独记录在 `f2-trace` 记录器中，作为库使用时可通过 `log_setup(log_to_console=False, log_name="f2-trace", lazy_file_creation=True)` 开启它的文件输出。
:::

## WSS配置 <Badge type="warning" text="实验性" />

如果你想使用 `douyin` 或 `tiktok` 的直播弹幕转发功能，那么你需要配置 `WSS` 服务的地址和端口。

`WSS` 配置须在 `conf.yaml` 文件中进行配置，配置如下：

::: code-group
```yaml [douyin]
douyin:
......
    wss:
      domain: localhost
      port: 8765
      verify: false
......
```
```yaml [tiktok]
tiktok:
......
    wss:
      domain: localhost
      port: 8766
      verify: false
......
```
:::

::: details :link: 示例：启动 `WSS` 服务并连接。
![wss](/douyin/wss-connect.png)
:::

> [!IMPORTANT] 重要 ❗❗❗
> - `wss` 段中的 `verify` 是本地弹幕转发服务的证书设置，当前版本暂不支持开启，请保持 `false`。它与 `conf.yaml` 顶层控制 `HTTP` 请求证书校验的 `verify`（默认开启）无关。
> - 本地连接与远程连接的默认超时时间均为 `10` 秒。
> - 如果本地在超时时间内未连接至 `WSS`，`F2` 将自动断开连接以节省资源。

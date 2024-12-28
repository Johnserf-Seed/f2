# 常见的问题与解决办法

## 第 n 次请求响应内容为空

只要是出现第 n 次请求响应内容为空均是 `cookie` 设置的问题。

::: details :link: 解决办法
1. 检查对应 `app` 配置文件中的 `cookie` 值是否正确配置，未出现换行，空格，缺失，错误字符（`非Ascii码`）等。
2. 如抖音，完整的网页端 `douyin`的`cookie` 有超过 `60` 个键，而 网页版`tiktok` 为不到 `30` 个。如果你获取的 `cookie` 长度过短，那明显是无法正常使用的。
3. 使用 `--auto-cookie` 命令时，确保选择的浏览器中已登录正常账号，游客账号的 `cookie` 非常不稳定。
4. 如果你使用的是该app扫码登录的功能，可能会因为未知的设备环境风控造成网页端与app端账号下线。如果出现扫码登录的 `cookie` 失效，请使用 `--auto-cookie` 命令。
5. `0.0.1.2` 之前的版本如果将 `cookie` 保存在自定义配置文件中，会有无法被正确识别的情况。

`Cookie` 获取方法请参阅下图。
![Console Cookie](https://github.com/user-attachments/assets/4523e8c7-f74e-4d5f-9da6-6bb3658f8b24)
:::

## API Rate Limit Error

如果出现 `API Rate Limit Error` 时只需等待一会后重试即可，这是因为你的请求频率过高，被服务器限制了。

继续频繁出现该错误需在网页端中重新登录并重新获取 `cookie`。仍无效后请切换网络环境和账号。

**参考链接：**
- https://zh.wikipedia.org/wiki/HTTP%E7%8A%B6%E6%80%81%E7%A0%81
- https://datatracker.ietf.org/doc/html/rfc6585#section-7.2

## <urlopen error [Errno 11001] getaddrinfo failed>

该问题为本地网络连接问题，请检查你的网络连接是否正常，DNS是否被污染。需要排查代理是否可以正常访问。

## f2: command not found

在非 `Windows` 系统中，如果出现 `f2: command not found` 错误，说明你的系统环境变量中没有添加 `f2` 命令的路径。

::: details :link: 解决办法
运行 `which f2` 命令查看 `f2` 命令的路径，然后将该路径添加到环境变量中。
1. 编辑`~/.bashrc`文件，添加`export PATH="$PATH:/home/YOUR_NAME/.local/bin"`。
2. 运行`source ~/.bashrc`命令使环境变量生效。
3. 重新打开终端，输入`f2`命令即可使用。
:::

## WARNING  没有找到符合条件的作品

如果出现 `WARNING  没有找到符合条件的作品`，请检查你是否配置了 `interval` 参数，该参数是用来设置作品发布时间的筛选条件。

::: details :link: 解决办法
1. 检查你的配置文件中是否有 `interval` 参数。如果没有，请添加为 `interval: all`。
2. 如果你的配置文件中有 `interval` 参数，请检查你的 `interval` 参数是否设置正确。
3. `cli` 命令中的 `-i` 参数也是用来设置作品发布时间的筛选条件 你可以设置为 `-i all`。
4. 如果你使用了 `-i` 参数，请检查你的 `-i` 参数是否设置正确。
:::
**参考链接：**
- https://github.com/Johnserf-Seed/f2/issues/42
- https://github.com/Johnserf-Seed/TikTokDownload/issues/660

## EOF occurred in violation of protocol (_ssl.c:992)

出现 `EOF occurred in violation of protocol (_ssl.c:992)` 说明SSL握手失败。

非项目代码问题，可能涉及到多个方面，需要自己逐步排查和解决。

::: details :link: 解决办法
1. 请检查你的代理设置是否正确，是否有防火墙或代理服务器阻止了 `SSL/TLS` 握手过程。
2. 确保代理网络连接稳定。
3. 使用更加专业的代理工具。
4. 更换网络环境。
5. 尝试更换 `DNS` 服务器。
6. 新版 `httpx` 库修改了代理与证书方面，如果在你的本地出现此问题，可以尝试降级 `httpx` 库版本。
7. 可能会出现使用工具（如 `Postman` 或 `curl`）测试相同的 `API` 请求，均可以访问但是使用本项目会超时，见第 `6`。

## _ssl.c:975 The handshake operation timed out

出现 `_ssl.c:975: The handshake operation timed out` 说明 `SSL` 握手超时。可能是网络连接不稳定或延迟过高导致。

解决办法：
1. 检查网络连接: 确保网络连接稳定，尽量减少网络延迟。
2. 检查服务器状态: 确保服务器运行正常，并且响应速度良好。
3. 检查防火墙和代理设置: 确保防火墙和代理服务器的设置正确，并且不会影响 `SSL/TLS` 握手过程。
4. 调整超时设置。

非项目代码问题，可能涉及到多个方面，需要自己逐步排查和解决。

## tiktok 403 Forbidden

当下载 `tiktok` 视频时出现 `403 Forbidden` 错误时，是由于 `设备id` 被封禁导致的。

`设备id` 与生成的 `cookie` 是一一对应的，如果 `设备id` 被封禁，那么生成的 `cookie` 也会被封禁。

::: details :link: 解决办法
1. 运行生成 `device_Id` 的代码片段，获取新的 `device_Id`。
2. 将新的 `device_Id` 替换到配置文件中。
3. 将新的 `cookie` 里的值替换到配置文件的 `cookie` 中（增量非覆盖）。
4. 重新运行下载命令。
:::
**参考链接：**
- https://f2.wiki/guide/apps/tiktok/#%E7%94%9F%E6%88%90deviceid-%F0%9F%9F%A2
- https://github.com/Johnserf-Seed/f2/issues/154

## TypeError: object of type 'NoneType' has no len()

在终端，你会看到类似以下的错误日志：

```shell
由于接口更新，部分字段处理失败:
字段 weibo_read_count 出错: object of type 'NoneType' has no len()
字段 weibo_topic_title 出错: object of type 'NoneType' has no len()
```

这通常是因为接口字段已更新，导致代码中的 `jsonpath` 对应的字段已经不存在或发生了更改。

::: details :link: 解决办法
请及时在 Issue 中反馈问题，并附上以下信息：

1. 脱敏的 debug 日志(`f2 -d DEBUG [app_name]`)：
    - 包含完整的错误信息及上下文。
2. 字段描述：
    - 明确指出哪些字段出现了问题，哪些字段可能需要更新。
3. 接口返回数据的简化结构（可选）：
    - 提供相关字段在接口返回数据中的大致位置，方便定位问题。

收到反馈后，我会尽快排查问题，并在后续版本中更新代码适配最新接口，同时也欢迎你提交 PR。
:::

## twitter 403 forbidden

当下载 `twitter` 推文时出现 `403 Forbidden` 错误时，是由于 `cookie` 或 `X-Csrf-Token` 失效导致的。

::: details :link: 解决办法
1. 重新获取 `cookie` 和 `X-Csrf-Token`。
2. 将新的 `cookie` 和 `X-Csrf-Token` 替换到配置文件中。
3. 重新运行下载命令。

需要注意的是，`X-Csrf-Token` 配置在 `F2配置文件(conf.yaml)` 中，`cookie` 配置在 `应用低频/主配置文件(app.yaml)` 或 `应用高频/自定义配置文件` 中。
:::

## Installing build dependencies error

当安装构建依赖项时出现以下错误：
```shell
  × pip subprocess to install build dependencies did not run successfully.
  │ exit code: 1
      Looking in indexes: https://xxxx
      ERROR: Could not find a version that satisfies the requirement hatchling (from versions: none)
      ERROR: No matching distribution found for hatchling
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
```

这通常是因为 `pip` 无法找到构建依赖项的版本，导致安装失败。请切换回官方源再次尝试安装。

::: details :link: 解决办法
1. 运行以下命令切换回官方源：

```shell
pip config unset global.index-url
```
2. 重新安装项目：

```shell
pip install f2
```
或

```shell
pip install -e .
```
:::

# 开发者必看

如果你是开发者或贡献着，开发前请阅读此文档再查看接口。

## 配置文件

f2 的配置文件可以在`x:\xxxxxxx\Python\Lib\site-packages\f2\conf\app.yaml`中找到它。

f2 提供了一些默认的配置，用户与开发者只需手动填写cookie或者使用--auto-cookie命令。

同时 f2 支持自由的配置文件定制，你可以在`f2/conf/app.yaml`中找到F2的默认配置文件，如果需要使用自定义配置文件请按照[配置参考](../site-config)来进行配置。

::: tip 提示
如果找不到配置文件可以在终端输入
```bash
pip show f2
```
查看Location，然后在该目录下找到配置文件。
:::

开发者可以直接定义自己的配置文件，然后在测试时通过`-c`参数指定配置文件的路径，例如：

```bash
f2 -d dy -c conf/app.yaml
```
也可以在代码中指定配置文件的路径，例如：

```python
import f2

f2.APP_CONFIG_FILE_PATH = "conf/app.yaml"
```

## 调试日志级别

<<< @/snippets/set-debug.py#set-debug-snippet{5}

![set-debug](/douyin/set-debug.png)


## 日志输出到控制台

<<< @/snippets/set-debug.py#log-2-console-snippet{5}

![log-2-console](/douyin/log-2-console.png)

::: tip 提示
如果你想要输出到控制台的日志更加详细，可以使用 `DEBUG` 级别。并且后续必须使用该logger对象来输出日志，否则日志将不会输出到控制台。
:::
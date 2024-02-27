# 开发者必看

如果你是开发者或贡献着，开发前请阅读此文档再查看接口。

## 指定配置文件

开发者可以直接定义自己的配置文件，然后在测试时通过`-c`参数指定配置文件的路径，例如：

```bash
f2 dy -c conf/app.yaml
```
也可以在代码中指定配置文件的路径，例如：

```python
import f2

f2.APP_CONFIG_FILE_PATH = "conf/app.yaml"
```

## 设置调试日志级别

<<< @/snippets/set-debug.py#set-debug-snippet{5}

支持代码`接口`模式的同时也支持在`CLI`模式中加上`-d`来指定记录日志级别。可选的参数`DEBUG`，`INFO`，`WARNING`，`ERROR`。

<<< @/snippets/set-debug.py#cli-debug-snippet

![set-debug](/douyin/set-debug.png)


## 日志输出到控制台

<<< @/snippets/set-debug.py#log-2-console-snippet{5}

![log-2-console](/douyin/log-2-console.png)

::: tip 提示
如果你想要输出到控制台的日志更加详细，可以使用 `DEBUG` 级别。并且后续必须使用该logger对象来输出日志，否则日志将不会输出到控制台。
:::
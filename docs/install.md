# 安装

## 必备条件

- [Python](https://www.python.org/) ≥ 3.9, 推荐版本3.11.1。
- [Windows Terminal](https://aka.ms/terminal) 终端，通过命令行界面（CLI）访问。
- 支持[Python](https://en.wikipedia.org/wiki/python) 语法的文本编辑器。
  - 推荐使用[VSCode](https://code.visualstudio.com/) 或[VSCode在线](https://vscode.dev)。

`F2` 可单独使用，也可安装到现有项目中。在这两种情况下，你都可以使用以下命令选择不同版本安装:

::: code-group

```sh [Windows]
$ pip install f2              # 最新版本
$ pip install f2==x.x.x       # 指定版本
$ pip install 'f2>=x.x.x'     # 最小版本
```

```sh [Linux]
$ pip3 install f2              # 最新版本
$ pip3 install f2==x.x.x       # 指定版本
$ pip3 install 'f2>=x.x.x'     # 最小版本
```

```sh [MacOS]
$ pip3 install f2              # 最新版本
$ pip3 install f2==x.x.x       # 指定版本
$ pip3 install 'f2>=x.x.x'     # 最小版本
```
:::

::: details 收到依赖或其他警告?
如果提示python或pip版本错误，请尝试更新到必备条件的版本。

如果你的网络环境缓慢，无法正常访问官方镜像。请使用可以正常访问的第三方镜像源。
::: code-group

```sh [Windows]
$ pip install -i https://pypi.tuna.tsinghua.edu.cn/simple f2
```

```sh [Linux]
$ pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple f2
```

```sh [MacOS]
$ pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple f2
```
:::

::: tip 提示

`F2` 是一个异步库，开发者在调用方法前请仔细`阅读相关文档`。

更多详情，请参阅 [高级指南](/advance-guide)。

:::
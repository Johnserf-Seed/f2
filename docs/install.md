# 安装

## 必备条件

- [Python](https://www.python.org/) ≥ 3.10, 推荐版本3.11.1。
- [Windows Terminal](https://aka.ms/terminal) 终端，通过命令行界面（CLI）访问。
- [Git](https://git-scm.com/) ，用于开发者从GitHub上克隆项目。
- [GitHub Desktop](https://desktop.github.com/) ，用于可视化管理Git项目。
- 支持[Python](https://en.wikipedia.org/wiki/python) 语法的文本编辑器。
  - 如果你是新手，推荐使用[VSCode](https://code.visualstudio.com/) 或 [VSCode在线](https://vscode.dev)，因为它们非常轻量级且插件丰富。

> [!TIP] 还需要什么？ 🤔
> - 一个[GitHub](https://github.com) 账号，用于克隆项目和参与讨论。
> - 一个良好的网络环境，还有耐心和耐心。

## 包管理器安装

`F2` 可单独使用，也可安装到现有项目中。在这两种情况下，你都可以使用以下命令选择不同版本安装：

::: code-group

```sh [Windows]
$ pip install f2                # 最新版本
$ pip install f2==x.x.x.x       # 指定版本
$ pip install -U f2             # 更新版本
$ pip uninstall f2              # 卸载版本
```

```sh [Linux]
$ pip3 install f2                # 最新版本
$ pip3 install f2==x.x.x.x       # 指定版本
$ pip3 install -U f2             # 更新版本
$ pip3 uninstall f2              # 卸载版本
```

```sh [MacOS]
$ pip3 install f2                # 最新版本
$ pip3 install f2==x.x.x.x       # 指定版本
$ pip3 install -U f2             # 更新版本
$ pip3 uninstall f2              # 卸载版本
```
:::

::: details :warning: 收到依赖或其他警告?
如果提示 `python` 或 `pip` 版本错误，请务必更新到必备条件的版本。

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

## 编译安装

### 如果你是Python开发者

可以通过以下命令克隆代码库并编译安装项目：

::: code-group

```sh [Windows]
$ git clone https://github.com/Johnserf-Seed/f2.git
$ cd f2
$ pip install -e .  #注意点前面有一个空格
```

```sh [Linux]
$ git clone https://github.com/Johnserf-Seed/f2.git
$ cd f2
$ pip3 install -e . #注意点前面有一个空格
```

```sh [MacOS]
$ git clone https://github.com/Johnserf-Seed/f2.git
$ cd f2
$ pip3 install -e . #注意点前面有一个空格
```
:::

### 如果你是PR贡献者

请先 `fork` 本项目，然后克隆你的项目。

1. 在 `Discussions` 中提出你的想法，或者在 `Issues` 中报告错误。
2. 更新完代码后，按照 `CONTRIBUTING.md` 的指导提交 `PR`。

### 如果你想测试最新功能

当代码库有新功能或者错误修复但未发布到 `PyPi` 时，你可以切换到最新的开发分支：

::: code-group

```sh [Windows]
$ git branch -a         # 查看所有分支
$ git checkout vx.x.x.x # 切换到最新的vx.x.x.x分支
$ pip install -e .      #注意点前面有一个空格
```

```sh [Linux]
$ git branch -a         # 查看所有分支
$ git checkout vx.x.x.x # 切换到最新的vx.x.x.x分支
$ pip3 install -e .     #注意点前面有一个空格
```

```sh [MacOS]
$ git branch -a         # 查看所有分支
$ git checkout vx.x.x.x # 切换到最新的vx.x.x.x分支
$ pip3 install -e .     #注意点前面有一个空格
```
:::

::: tip :bulb: 提示
`F2` 是一个**异步库**，开发者在调用方法前请仔细`阅读相关文档` 和 `异步编程` 的相关知识。

- 请注意切换至开发分支时，需要检查当日提交的代码是否通过测试。
- 执行一次**编译安装**后，对代码库的修改会实时生效。
- 更多详情，请参阅 [高级指南](./advance-guide)。
- 更多接口，请参阅 [开发者接口](./guide/apps/douyin/)。
:::

---
outline: [2,3]
---

# 安装

## 必备条件

### **开发语言**
   - [Python](https://www.python.org/) ≥ `3.10`，推荐版本 `3.11.1`，用来运行 `F2`。
   - [Nvm](https://github.com/nvm-sh/nvm) ≥ `1.1.12`，用来管理 `Node.js` 版本，`F2` 部分应用依赖。
### **终端**
   - [Windows Terminal](https://aka.ms/terminal) ≥ `1.21.3231.0`，使用命令行界面（`CLI`）所需。
### **版本控制工具**
   - [Git](https://git-scm.com/) ≥ `2.47.0.2` 或 []
   - [GitHub Desktop](https://desktop.github.com/) ≥ `3.4.12`，用于可视化管理 `Git` 项目。
### **文本编辑器**
   - 支持 [Python](https://en.wikipedia.org/wiki/python) 语法的文本编辑器。如果你是新手，推荐使用 [VSCode](https://code.visualstudio.com/) ≥ `1.96.2` 或 [VSCode 在线](https://vscode.dev)，因为它们非常轻量且插件丰富。
### **浏览器**
   - 主流的浏览器如 [Chrome](https://www.google.com/chrome/)、[Firefox](https://www.mozilla.org/firefox/)、[Edge](https://www.microsoft.com/edge) 等，用于查看文档和调试。
### **网络环境**
   - 稳定的网络环境，用于安装依赖和采集数据。
### **其他**
   - 了解 [Markdown](https://www.markdownguide.org/) 语法，用于编辑文档。
   - 了解 [YAML](https://yaml.org/) 语法，用于编辑配置文件。
   - 了解 [异步编程](https://docs.python.org/3/library/asyncio.html) 文档，用于理解 `F2` 的异步特性。
   - 阅读 [开发指南](/guide/what-is-f2)，了解 `F2` 的开发者文档。

> [!TIP] 还需要什么？ 🤔
> - 一个[GitHub](https://github.com) 账号，用于克隆项目和参与讨论。
> - 善用搜索引擎，查找你遇到的基础问题。
> - 提问的智慧，学会如何提问，以及如何解决问题。
> - 最后还有友善与耐心。

## 包管理器安装

`F2` 可单独使用，也可安装到现有项目中。这两种情况下，你都可以使用以下命令选择不同版本安装：

::: code-group

```sh [Windows]
$ pip install f2                # 安装最新版本
$ pip install f2==x.x.x.x       # 安装指定版本
$ pip install -U f2             # 更新到最新版本
$ pip uninstall f2              # 卸载
```

```sh [Linux]
$ pip3 install f2                # 安装最新版本
$ pip3 install f2==x.x.x.x       # 安装指定版本
$ pip3 install -U f2             # 更新到最新版本
$ pip3 uninstall f2              # 卸载
```

```sh [MacOS]
$ pip3 install f2                # 安装最新版本
$ pip3 install f2==x.x.x.x       # 安装指定版本
$ pip3 install -U f2             # 更新到最新版本
$ pip3 uninstall f2              # 卸载
```
:::

::: details :warning: 收到依赖或其他警告?
1. 如果提示 `python` 或 `pip` 版本错误，请务必更新到[必备条件](#必备条件)的版本。

2. 如果你的网络环境缓慢，无法正常访问官方镜像。请使用可以正常访问的第三方镜像源。
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

3. 如遇到其他问题，请参阅 [常见问题](/faq)。
:::

## 编译安装

### Python开发者

通过以下命令克隆代码库并编译安装项目：

::: code-group

```sh [Windows]
$ git clone https://github.com/Johnserf-Seed/f2.git
$ cd f2
$ pip install -e .  # 在当前目录下进行开发安装
```

```sh [Linux]
$ git clone https://github.com/Johnserf-Seed/f2.git
$ cd f2
$ pip3 install -e . # 在当前目录下进行开发安装
```

```sh [MacOS]
$ git clone https://github.com/Johnserf-Seed/f2.git
$ cd f2
$ pip3 install -e . # 在当前目录下进行开发安装
```
:::

### PR贡献者

1. 请先 `fork` 本项目，然后克隆你的项目。
2. 在 `Discussions` 中提出你的想法，或者在 `Issues` 中报告错误。
3. 更新完代码后，按照 [CONTRIBUTING](https://github.com/Johnserf-Seed/f2/blob/main/CONTRIBUTING.md) 的指导提交 `PR`。

### 测试最新功能

当代码库有新功能或者错误修复但未发布到 `PyPi` 时，可以切换到最新的开发分支：

::: code-group

```sh [Windows]
$ git branch -a         # 查看所有分支
$ git checkout vx.x.x.x # 切换到最新的vx.x.x.x分支
$ pip install -e .      # 开发安装
```

```sh [Linux]
$ git branch -a         # 查看所有分支
$ git checkout vx.x.x.x # 切换到最新的vx.x.x.x分支
$ pip3 install -e .     # 开发安装
```

```sh [MacOS]
$ git branch -a         # 查看所有分支
$ git checkout vx.x.x.x # 切换到最新的vx.x.x.x分支
$ pip3 install -e .     # 开发安装
```
:::

::: tip :bulb: 提示
- **异步特性**：`F2` 是一个异步库，请仔细阅读 [异步编程](https://docs.python.org/3/library/asyncio.html) 和本文档。
- **分支注意**：切换至开发分支后，请检查最新提交的代码是否通过测试。
- **实时生效**：执行一次 [编译安装](#编译安装) 后，对代码库的修改会实时生效。
:::

## 更多内容
  - [开发指南](/guide/what-is-f2)
  - [开发者接口](/guide/api-examples)
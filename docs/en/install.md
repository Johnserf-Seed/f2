# Installation

## Prerequisites

- [Python](https://www.python.org/) ≥ 3.9, recommended version 3.11.1.
- [Windows Terminal](https://aka.ms/terminal) Terminal, accessed through the command line interface (CLI).
- Text editor with [Python](https://en.wikipedia.org/wiki/python) syntax support.
  - [VSCode](https://code.visualstudio.com/) or [VSCode Online](https://vscode.dev) is recommended.

`F2` can be used alone or installed into an existing project. In both cases, you can select a different version to install using the following command:

::: code-group

```sh [Windows]
$ pip install f2              # Latest version
$ pip install f2==x.x.x       # Specified version
$ pip install 'f2>=x.x.x'     # Minimum version
```

```sh [Linux]
$ pip3 install f2              # Latest version
$ pip3 install f2==x.x.x       # Specified version
$ pip3 install 'f2>=x.x.x'     # Minimum version
```

```sh [MacOS]
$ pip3 install f2              # Latest version
$ pip3 install f2==x.x.x       # Specified version
$ pip3 install 'f2>=x.x.x'     # Minimum version
```
:::

::: details Got a dependency or other warning?
If you are prompted with a python or pip version error, try updating to the required version.

If you have a slow network environment and cannot access the official mirrors properly. Please use a third-party mirror source that can be accessed properly.
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

::: tip Tip

``F2`` is an asynchronous library, and developers should carefully ``read the documentation`` before calling methods.

For more details, see [advance-guide](./advance-guide).

:::

---
outline: [2,3]
---

# Installation

## Prerequisites

### **Programming Languages**
   - [Python](https://www.python.org/) ≥ `3.10`, recommended version `3.11.1`, required to run `F2`.
   - [Nvm](https://github.com/nvm-sh/nvm) ≥ `1.1.12`, used to manage `Node.js` versions, which some `F2` applications depend on.
### **Terminal**
   - [Windows Terminal](https://aka.ms/terminal) ≥ `1.21.3231.0`, required for command line interface (`CLI`).
### **Version Control Tools**
   - [Git](https://git-scm.com/) ≥ `2.47.0.2` or []
   - [GitHub Desktop](https://desktop.github.com/) ≥ `3.4.12`, used for visual management of `Git` projects.
### **Text Editors**
   - A text editor that supports [Python](https://en.wikipedia.org/wiki/python) syntax. If you are a beginner, it is recommended to use [VSCode](https://code.visualstudio.com/) ≥ `1.96.2` or [VSCode Online](https://vscode.dev), as they are lightweight and have rich plugins.
### **Browsers**
   - Popular browsers such as [Chrome](https://www.google.com/chrome/), [Firefox](https://www.mozilla.org/firefox/), [Edge](https://www.microsoft.com/edge), etc., for viewing documentation and debugging.
### **Network Environment**
   - A stable network environment for installing dependencies and collecting data.
### **Other**
   - Knowledge of [Markdown](https://www.markdownguide.org/) syntax for editing documentation.
   - Knowledge of [YAML](https://yaml.org/) syntax for editing configuration files.
   - Understanding of [asynchronous programming](https://docs.python.org/3/library/asyncio.html) documentation to grasp `F2`'s asynchronous features.
   - Read [Developer Guide](/guide/what-is-f2) for detailed developer documentation on `F2`.

> [!TIP] What else is needed? 🤔
> - A [GitHub](https://github.com) account to clone projects and participate in discussions.
> - Make good use of search engines to look up basic issues you encounter.
> - The wisdom of asking questions, learning how to ask and how to solve problems.
> - And lastly, be friendly and patient.

## Package Manager Installation

`F2` can be used alone or installed in an existing project. In both cases, you can install it in different versions using the following commands:

::: code-group

```sh [Windows]
$ pip install f2                # Install the latest version
$ pip install f2==x.x.x.x       # Install a specific version
$ pip install -U f2             # Upgrade to the latest version
$ pip uninstall f2              # Uninstall
```

```sh [Linux]
$ pip3 install f2                # Install the latest version
$ pip3 install f2==x.x.x.x       # Install a specific version
$ pip3 install -U f2             # Upgrade to the latest version
$ pip3 uninstall f2              # Uninstall
```

```sh [MacOS]
$ pip3 install f2                # Install the latest version
$ pip3 install f2==x.x.x.x       # Install a specific version
$ pip3 install -U f2             # Upgrade to the latest version
$ pip3 uninstall f2              # Uninstall
```
:::

::: details :warning: Encountering dependencies or other warnings?
1. If prompted with an error regarding `python` or `pip` versions, please update to the versions specified in the [Prerequisites](#prerequisites)

2. If you have slow network connectivity and cannot access the official mirrors, use a third-party mirror that is accessible.
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

3. If you encounter other issues, refer to the [FAQ](/en/faq).
:::

## Build from Source

### Python Developers

Clone the repository and build the project with the following commands:

::: code-group

```sh [Windows]
$ git clone https://github.com/Johnserf-Seed/f2.git
$ cd f2
$ pip install -e .  # Install in development mode
```

```sh [Linux]
$ git clone https://github.com/Johnserf-Seed/f2.git
$ cd f2
$ pip3 install -e . # Install in development mode
```

```sh [MacOS]
$ git clone https://github.com/Johnserf-Seed/f2.git
$ cd f2
$ pip3 install -e . # Install in development mode
```
:::

### For PR Contributors

1. First, `fork` this project and clone your fork.
2. Submit your ideas in `Discussions`, or report issues in `Issues`.
3. After updating your code, submit a `PR` following the instructions in [CONTRIBUTING](https://github.com/Johnserf-Seed/f2/blob/main/CONTRIBUTING.en.md).

### Test the Latest Features

When new features or bug fixes have not been released to PyPi, you can switch to the latest development branch:

::: code-group

```sh [Windows]
$ git branch -a         # List all branches
$ git checkout vx.x.x.x # Switch to the latest vx.x.x.x branch
$ pip install -e .      # Install in development mode
```

```sh [Linux]
$ git branch -a         # List all branches
$ git checkout vx.x.x.x # Switch to the latest vx.x.x.x branch
$ pip3 install -e .     # Install in development mode
```

```sh [MacOS]
$ git branch -a         # List all branches
$ git checkout vx.x.x.x # Switch to the latest vx.x.x.x branch
$ pip3 install -e .     # Install in development mode
```
:::

::: tip :bulb: Tips
- **Asynchronous Features**: `F2` is an asynchronous library, so make sure to read [Asynchronous Programming](https://docs.python.org/3/library/asyncio.html) and the rest of this documentation.
- **Branch Notes**: After switching to a development branch, make sure the latest commits pass the tests.
- **Instant Effect**: After performing a [build installation](#build-from-source), modifications to the codebase will take effect immediately.
:::

## More Resources
  - [Developer Guide](/en/guide/what-is-f2)
  - [Developer API](/en/guide/api-examples)

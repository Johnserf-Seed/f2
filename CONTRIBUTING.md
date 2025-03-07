# 如何贡献到 F2 🚀

感谢您对 `F2` 的兴趣！🎉 无论是修复 bug、添加新功能，还是改进文档，我们都欢迎您的贡献。您可能希望在开始工作之前打开一个问题，或先向 `support@f2.wiki` 发送电子邮件讨论它。请花点时间阅读此指南，了解我们的开发流程。

## 必备条件 🛠️
> [!IMPORTANT]
> 您将需要安装 `Python`，我们强烈建议使用虚拟环境来管理依赖。
> 本指南的其余部分假定您位于虚拟环境中。

要开始使用该项目，请按照官方文档中的 [安装](https://f2.wiki/install#必备条件) 指南设置开发环境。

接下来按照 [PR贡献者](https://f2.wiki/install#pr贡献者) 的步骤进行操作。

## 开发规范 📝
在开发 `F2` 代码时，请注意以下几点：

1. **避免使用变量名缩写**：描述性的变量名能让代码更易读，也更容易维护。
2. **保持一致性**：遵循已设定的编码风格。
3. **文档很重要**：确保您的代码有良好的文档，尤其是新的功能或复杂的逻辑。
4. **避免硬编码**：避免硬编码敏感信息，将配置信息集成在 `conf.yaml` 文件中。

## 提交规范 📌
在提交代码之前，您应该：

1. **运行测试**：确保所有测试通过。
2. **检查类型错误**：使用类型检查工具，来捕获类型问题。
3. **格式化代码**：使用 `black` 自动格式化代码，遵循 `PEP 8` 风格。

## 代码格式化 🛠️

`F2` 使用 [`black`](https://github.com/psf/black) 进行代码格式化。建议在编辑器中设置 `black` 以在保存时格式化代码。

如果使用 `VSCode` 开发，那么已经配置好了 `black` 调试器。您也可以在项目根目录运行以下命令来格式化代码：

```bash
$ black **/*.py --exclude venv/*
```

## 测试规范 🧪
`F2` 使用 `pytest` 进行单元测试。以下是如何进行测试的步骤：

1. **配置测试环境**：确保测试的配置已经准备好。对于异步代码，使用 `pytest-asyncio` 插件。
2. **编写测试**：对于新功能或 bug 修复，始终添加相应的测试。
3. **模拟外部依赖**：使用 `unittest.mock` 进行依赖模拟。
4. **检查测试覆盖率**：查看测试覆盖率，确保没有遗漏。

在项目根目录运行以下命令来运行

普通测试：
```bash
$ pytest -vv
```

覆盖率测试：
```bash
$ pytest --cov-report term-missing --cov=f2 ./ -vv
```

理想情况下，新代码应该有测试，并且不会破坏现有的测试。如果修改或新添加的代码未出现在覆盖率报告中，则强烈建议添加相应的测试。

## 本地化 🌍
> [!IMPORTANT]
> 如果安装了 `F2` 本地化工具 `Babel`，则不需要额外安装 `gettext`。

添加翻译的步骤：

1. 在项目根目录运行以下脚本以生成 `.pot` 与 `.po` 文件：

（适用于 Windows）
```bash
$ make_pot.bat
```
（适用于 Linux/macOS）
```bash
$ make_pot.sh
```
2. 将 `.po` 文件翻译为所需语言，这里推荐使用 [Poedit](https://poedit.net/) 工具。
3. 将不同语言的 `.po` 文件编译为 `.mo` 文件并放置在相应语言的 `languages` 文件夹下。

## 文档编写 📚
考虑一下您所做的更改是否会从文档中受益。如果该更改需要文档支持，答案是肯定的。

构建文档需要一些额外的依赖项。这些依赖项可以通过运行（在 `docs` 目录下）以下命令来安装：

1. **本地运行文档**：
使用 `pnpm` 运行 `VitePress`：
```bash
$ cd docs
$ pnpm i
$ pnpm docs:dev
```
2. **编写文档**：在 `docs` 目录下添加新的代码相关文档。请遵循现有的文档风格和格式。
3. **本地构建**：提交代码前，确保文档能够正确构建。
生成静态文档：
```bash
$ pnpm docs:build
```

## 更新 ChangeLog 和 Contributors 📋
如果这是您第一次为 `F2` 贡献代码，欢迎您！🎉

您需要更新以下文件：
1. **ChangeLog**：在 `CHANGELOG.md` 文件中更新您的更改摘要。
2. **贡献者**：将您的名字添加到 `CONTRIBUTORS.md` 文件中。
3. **团队**：请将您的信息添加到文档的 `team.md` 中。

## 创建 PR 🚀
一旦对您的代码感到满意，并确保已遵守上述所有步骤，且通过了所有测试，您就可以创建一个您所 `fork` 分支的 `Pull Request`。

`GitHub` 提供了一个很好的 [指南](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) 来帮助您创建 `PR`。请确保 `PR` 中包含您对更改的描述，并将其链接到相关的 `Issue` 或讨论。

## 代码审查 🕵️
所有的代码更改都需要经过代码审查。等待仓库的代码审查机器人自动检查您的代码。如果有问题，可能会有一些讨论和迭代。大多数情况下，需要几次迭代才能完全解决问题。

## 最后一步 🏁
一旦您的 `PR` 被批准，它将被合并到 `main` 分支中，并在下次发布时供所有用户使用。🚀
# How to Contribute to F2 🚀

Thank you for your interest in contributing to `F2`! 🎉 Whether it's fixing bugs, adding new features, or improving documentation, we welcome your contributions. Before you start, we recommend opening an issue or emailing `support@f2.wiki` to discuss it. Please take a moment to read through this guide to understand our development process.

## Prerequisites 🛠️
> [!IMPORTANT]
> You will need to install `Python`, and we strongly recommend using a virtual environment to manage dependencies.
> The remainder of this guide assumes you are working within a virtual environment.

To get started with the project, follow the [Installation](https://f2.wiki/install#必备条件) guide in the official documentation.

Next, follow the steps for [PR Contributors](https://f2.wiki/install#pr贡献者).

## Development Guidelines 📝
When developing for `F2`, keep the following points in mind:

1. **Avoid Variable Name Abbreviations**: Descriptive variable names make the code more readable and easier to maintain.
2. **Consistency is Key**: Follow the established coding style throughout the project.
3. **Documentation is Important**: Ensure your code is well-documented, especially new features or complex logic.
4. **Avoid Hardcoding**: Do not hardcode sensitive information; store configuration details in the `conf.yaml` file.

## Commit Guidelines 📌
Before committing your code, ensure you:

1. **Run Tests**: Make sure all tests pass.
2. **Check for Type Errors**: Use type checking tools to catch any type issues.
3. **Format Code**: Use `black` to auto-format your code according to `PEP 8` style guidelines.

## Code Formatting 🛠️

`F2` uses [`black`](https://github.com/psf/black) for code formatting. It is recommended to set up `black` in your editor to format your code on save.

If you are using `VSCode`, the `black` formatter is already configured. Alternatively, you can format the code manually by running the following command from the project root:

```bash
$ black **/*.py --exclude venv/*
```

## Pre-commit Hooks 🔄

`F2` uses `pre-commit` hooks to automatically check code quality and formatting. First, install pre-commit:

```bash
$ pip install pre-commit
$ pre-commit install
```

Once installed, hooks will run automatically every time you execute `git commit`. You can also manually run all configured hooks on all files with the following command:

```bash
$ pre-commit run --all-files
```

This will execute code formatting, type checking, and other configured quality checks to ensure your code meets project standards. It's recommended to run this command before committing, or have it automatically triggered through `git commit -m "message"`.

If a hook fails, fix the issues and run the command again to verify. For special cases, you can skip hook checks using `--no-verify`, but this is not recommended for regular use:

```bash
$ git commit -m "message" --no-verify
```

## Testing Guidelines 🧪
`F2` uses `pytest` for unit testing. Here are the steps to run tests:

1. **Set up the Test Environment**: Ensure the test configuration is prepared. For asynchronous code, use the `pytest-asyncio` plugin.
2. **Write Tests**: Always add tests for new features or bug fixes.
3. **Mock External Dependencies**: Use `unittest.mock` to mock external dependencies.
4. **Check Test Coverage**: Review test coverage to ensure nothing is missed.

To run tests from the project root, use the following commands:

Normal tests:

```bash
$ pytest -vv
```
Coverage tests:
```bash
$ pytest --cov-report term-missing --cov=f2 ./ -vv
```

Ideally, new code should be covered by tests and should not break existing tests. If modified or newly added code does not appear in the coverage report, it is strongly advised to add relevant tests.

## Localization 🌍
> [!IMPORTANT]
> If you have the `F2` localization tool `Babel` installed, you do not need to install `gettext` separately.

To add translations:

1. Run the following script from the project root to generate `.pot` and `.po` files:

(Windows)
```bash
$ make_pot.bat
```
(Linux/macOS)
```bash
$ make_pot.sh
```
2. Translate the `.po` files to the desired language. We recommend using the [Poedit](https://poedit.net/) tool.
3. Compile the `.po` files into `.mo` files and place them in the respective language folder under `languages`.

## Documentation 📚
Consider whether the changes you make require documentation updates. If so, you should add documentation.

Building the documentation requires additional dependencies. You can install them by running the following commands from the `docs` directory:

1. **Run Documentation Locally**:
Use `pnpm` to run `VitePress`:
```bash
$ cd docs
$ pnpm i
$ pnpm docs:dev
```
2. **Write Documentation**: Add new code-related documentation in the `docs` directory. Follow the existing style and format.
3. **Build Documentation Locally**: Before submitting your code, ensure the documentation builds correctly.
Generate static documentation:
```bash
$ pnpm docs:build
```

## Update ChangeLog and Contributors 📋
If this is your first contribution to `F2`, welcome! 🎉

You need to update the following files:
1. **ChangeLog**: Update the summary of your changes in the `CHANGELOG.md` file.
2. **Contributors**: Add your name to the `CONTRIBUTORS.md` file.
3. **Team**: Add your information to the `team.md` file in the documentation.

## Creating a PR 🚀
Once you are satisfied with your code and have followed all the above steps, and your code passes all tests, you can create a `Pull Request` for your `forked` branch.

`GitHub` provides a useful [guide](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) to help you create a `PR`. Be sure to include a description of your changes and link to the related `Issue` or discussion.

## Code Review 🕵️
All code changes are subject to a code review. Wait for the repository's code review bot to automatically check your code. There may be some discussions and iterations. In most cases, a few iterations are needed to fully address any issues.

## Final Step 🏁
Once your `PR` is approved, it will be merged into the `main` branch and made available to all users in the next release. 🚀

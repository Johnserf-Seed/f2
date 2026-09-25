# How to Contribute to F2 🚀

Thank you for your interest in contributing to `F2`! 🎉 Whether it's fixing bugs, adding new features, or improving documentation, we welcome your contributions. Before you start, we recommend opening an issue or emailing `support@f2.wiki` to discuss it. Please take a moment to read through this guide to understand our development process.

## Prerequisites 🛠️
> [!IMPORTANT]
> You will need to install `Python`, and we strongly recommend using a virtual environment to manage dependencies.
> The remainder of this guide assumes you are working within a virtual environment.

To get started with the project, follow the [Installation](https://f2.wiki/install#必备条件) guide in the official documentation.

Next, follow the steps for [PR Contributors](https://f2.wiki/install#pr贡献者).

## Branches and PR Targets 🌿
> [!IMPORTANT]
> Please do not open `PR`s against `main`. `main` only holds released code; development happens on the current development branch, which is currently [`v0.0.1.8-pw3`](https://github.com/Johnserf-Seed/f2/tree/v0.0.1.8-pw3).

- **Branch naming**: development branches are named `v<next version>-pw<sequence>`, e.g. `v0.0.1.8-pw3`. The `Dev Branch` badge at the top of the README always shows the current one.
- **Start from the development branch**: after forking, create your feature branch from the development branch:

  ```bash
  git remote add upstream https://github.com/Johnserf-Seed/f2.git
  git fetch upstream
  git checkout -b fix/your-change upstream/v0.0.1.8-pw3
  ```

- **PR target**: choose the current development branch as the `base` when opening a `PR`. If you already opened it against `main`, click `Edit` next to the title on the `PR` page and change the base branch; there is no need to close and reopen it. Rebase onto the development branch if there are conflicts.
- **External `PR`s targeting `main`**: they are blocked by the `PR target branch` check. Maintainers will ask you to retarget, or port your change to the development branch and credit you with `Co-authored-by`.
- **Release flow**: once the development branch is tested it is merged into `main`, released to `PyPI` from `main`, and the next development branch is created.

## Issues and Labels 🏷️
When opening an issue, pick the matching template: bug report, platform API change, feature request, documentation or question. Please ask general usage questions in the [Q&A](https://github.com/Johnserf-Seed/f2/discussions/categories/q-a) discussion category, and report security issues through [private reporting](https://github.com/Johnserf-Seed/f2/security/advisories/new).

Maintainers organize issues with these kinds of labels:

| Kind | Labels |
| :--- | :--- |
| Type | `故障(bug)`, `需求建议(enhancement)`, `提问(question)`, `文档改进(docs)` |
| Platform | `抖音(douyin)`, `TikTok(tiktok)`, `微博(weibo)`, `推特(twitter)`, `Bark(bark)`, added automatically from the platform chosen in the template |
| Area | `直播(live)`, `下载(download)`, `配置(config)` |
| Status | `已确认(confirmed)`, `等待反馈(feedback)`, `接口变化(api-change)`, `开发分支已修复(fixed-in-dev)`, `重复(duplicate)`, `无效(invalid)`, `不修复(wontfix)` |
| Priority | `紧急(P0)`, `重要(P1)`, `一般(P2)` |

Issues labeled `开发分支已修复(fixed-in-dev)` can be verified by installing the development branch as described in [Test the Latest Features](https://f2.wiki/en/install#test-the-latest-features); they are closed once the fix ships in a release.

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

Before committing, also run `ruff check .` (unused imports/variables, undefined names and similar correctness checks) and `isort .`; `CI` runs the same commands.

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
5. **Provide Test Credentials**: `f2/conf/test.yaml` only holds guest data used by the tests. Supply personal cookies through the `F2_TEST_<APP>_<KEY>` environment variables (e.g. `F2_TEST_DOUYIN_COOKIE`) or a `test.local.yaml` next to it (git-ignored); never write them back into `test.yaml`.

To run tests from the project root, use the following commands:

Normal tests (offline, same as CI):

```bash
$ pytest -m "not network" -vv
```

Platform API tests (`f2/apps/*/test` and the version-check test carry the `network` marker and need real network access plus test credentials):

```bash
$ pytest -m network -vv
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

## Continuous Integration and Releases 🚦
Every `PR` and push triggers `.github/workflows/ci.yml`:

1. **Lint**: `ruff check .`, `black --check .`, `isort --check-only .` and `mypy f2/`, matching the local `pre-commit` hooks.
2. **Test**: `pytest -m "not network"` on Python 3.10–3.13, with coverage uploaded to Codecov.
3. **Build**: builds the `sdist`/`wheel`, validates metadata with `twine check`, and installs the `wheel` in a clean environment as a smoke test.

`security.yml` additionally runs the `gitleaks` secret scan, the `wheel` content check and a `pip-audit` dependency vulnerability scan (also scheduled weekly on Mondays).

Releases are handled by `.github/workflows/release.yml`: after updating `__version__` in `f2/__init__.py` and `CHANGELOG.md` and merging, maintainers create a GitHub Release tagged `vX.Y.Z`; clicking Publish release triggers the build and publishes through PyPI Trusted Publishing, so no API token is stored in the repository (the workflow verifies that the tag matches the version). Drafts do not trigger anything; releases marked as pre-release are only built, not published, and the artifacts can be downloaded from the workflow run; pushing a tag on its own never publishes. One-time setup: add a GitHub publisher in the PyPI project's Publishing settings (repository `Johnserf-Seed/f2`, workflow `release.yml`, environment `pypi`) and create the `pypi` environment under the repository's Settings → Environments, optionally with required reviewers as a final approval gate.

When switching to a new development branch, maintainers update the following:

1. Create the new development branch from `main`, e.g. `v0.0.1.9-pw1`.
2. Update the `Dev Branch` badge and the development branch note at the top of `README.md` and `README.en.md`, the current development branch in `CONTRIBUTING.md` and this file, and `target-branch` in `.github/dependabot.yml`.
3. During development, set the repository's default branch (Settings → General → Default branch) to the development branch: new `PR`s then target it by default, and `dependabot`, the `PR` template and scheduled scans all read their configuration from the default branch.

## Creating a PR 🚀
Once you are satisfied with your code and have followed all the above steps, and your code passes all tests, you can create a `Pull Request` for your `forked` branch. **Choose the current development branch as the `base`, not `main`**, and go through the checklist in the `PR` template.

`GitHub` provides a useful [guide](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) to help you create a `PR`. Be sure to include a description of your changes and link to the related `Issue` or discussion.

## Code Review 🕵️
All code changes are subject to a code review. Wait for the repository's code review bot to automatically check your code. There may be some discussions and iterations. In most cases, a few iterations are needed to fully address any issues.

## Final Step 🏁
Once your `PR` is approved, it will be merged into the current development branch, then merged into `main` and released to `PyPI` with the next version. 🚀

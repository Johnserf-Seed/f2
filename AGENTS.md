# AGENT Instructions

This repository contains **F2**, an asynchronous multi-platform download library implemented in Python.

## Contribution rules

- **Formatting**: Run `black` with line length 88 on all modified Python files.
- **Imports**: Run `isort --profile black` to sort imports.
- **Type checking**: Run `mypy --ignore-missing-imports --check-untyped-defs`. Skip generated proto files.
- **Quality checks**: Use `pre-commit run --files <file1> <file2>` to execute the configured hooks.
- **Testing**: Execute `pytest -vv` before submitting changes.
- **Documentation**: When code changes require documentation, update the markdown files under `docs/` and ensure they build using `pnpm docs:build`.
- **Changelog**: Summarize user-facing changes in `CHANGELOG.md` and add your name to `CONTRIBUTORS.md`.

These instructions apply to the entire repository.

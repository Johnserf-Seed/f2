# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Testing
- `pytest` - Run all tests (asyncio mode enabled by default)
- `pytest f2/apps/douyin/test/` - Run tests for specific app
- `pytest -m apps` - Run tests marked as apps-related
- `pytest -m asyncio` - Run async-related tests

### Linting and Formatting
- `black .` - Format Python code using Black formatter (line length 88)
- `isort .` - Sort imports using isort with Black profile
- `mypy f2/` - Type checking with mypy (ignores missing imports, excludes docs/snippets/, f2-secrets/, tests/)
- `pre-commit run --all-files` - Run all pre-commit hooks

### Installation and Dependencies
- `pip install -e .` - Install in development mode
- `pip install -e .[dev]` - Install with development dependencies
- `f2` - Main CLI entry point after installation

### Documentation (VitePress)
- `cd docs && pnpm install` - Install documentation dependencies
- `pnpm run docs:dev` - Start VitePress development server
- `pnpm run docs:build` - Build documentation for production
- `pnpm run docs:preview` - Preview built documentation

### Pre-commit Hooks
The project uses pre-commit with:
- trailing-whitespace and end-of-file-fixer
- isort with Black profile
- Black formatting
- MyPy type checking (excludes protobuf files and test directories)
- Gitleaks security scanning

## Architecture Overview

F2 is an asynchronous Python library for downloading content from multiple social media platforms. The codebase follows a modular architecture:

### Core Structure
- **f2/apps/**: Platform-specific implementations (douyin, tiktok, twitter, weibo, bark)
- **f2/cli/**: Command-line interface components
- **f2/conf/**: Configuration management (YAML-based)
- **f2/crawlers/**: Base crawler classes and WebSocket crawler
- **f2/db/**: Database abstraction layer
- **f2/dl/**: Download managers including M3U8 support
- **f2/exceptions/**: Custom exception hierarchy
- **f2/utils/**: Shared utilities (crypto, HTTP, JSON processing, string handling)

### App Module Pattern
Each app follows a consistent structure:
- `api.py` - API endpoint definitions
- `cli.py` - Command-line interface
- `crawler.py` - Platform-specific crawling logic
- `db.py` - Database models and operations
- `dl.py` - Download handling
- `filter.py` - Data filtering and processing
- `handler.py` - Main business logic
- `model.py` - Data models using Pydantic
- `utils.py` - App-specific utilities
- `test/` - Unit tests

### Key Features
- **Async/await throughout**: All I/O operations are asynchronous
- **Multi-platform support**: DouYin, TikTok, Twitter, WeiBo, Bark notifications
- **WebSocket support**: Live stream and real-time data handling
- **Protobuf integration**: For binary message parsing (webcast)
- **Configuration management**: YAML-based with hierarchical merging
- **Database abstraction**: SQLite with async operations
- **Cryptographic operations**: Platform-specific signature generation
- **Proxy support**: HTTP and SOCKS proxy configurations

### Security Algorithms
The project implements platform-specific security algorithms:
- **XBogus/ABogus**: ByteDance signature generation for DouYin/TikTok
- **WebCast signatures**: Live stream authentication
- **Token management**: Platform-specific token generation and refresh

### Configuration System
- **app.yaml**: Main application configuration
- **conf.yaml**: Platform-specific settings
- **defaults.yaml**: Default values
- **test.yaml**: Test environment settings

Uses hierarchical configuration merging where specific configs override defaults.

### Testing Approach
- Uses pytest with asyncio support
- Test data stored in `tests/data/` with platform-specific samples
- Protobuf test data for WebCast message parsing
- Markers for categorizing tests (`apps`, `asyncio`)

### CLI Structure
- `cli_commands.py`: Main command definitions using Click
- `cli_console.py`: Console output formatting with Rich
- Multi-platform CLI with app-specific subcommands

### Database Design
- Uses aiosqlite for async SQLite operations
- Platform-specific tables (douyin_users.db, douyin_videos.db, etc.)
- Migration support for schema changes
- WebSocket message storage for live streams

## File Processing Patterns

### Media Downloads
- Supports video, audio, and image downloads
- M3U8 playlist processing for live streams
- Watermark-free content extraction
- Batch download capabilities

### Data Filtering
- JSONPath-based data extraction
- Pydantic models for type safety
- Custom filters for each platform's response format

### Internationalization
- Babel-based i18n support
- Language files in `f2/languages/`
- Support for zh_CN and en_US locales

### Documentation Structure
The project uses VitePress for documentation hosted at https://f2.wiki/:
- **docs/**: VitePress documentation source
- **docs/.vitepress/**: VitePress configuration
- **docs/snippets/**: Code examples for each platform
- **docs/guide/**: Developer guides and API documentation
- **docs/en/**: English documentation mirror
- Bilingual support (Chinese and English)
- Interactive examples and code snippets

## Important Notes

- **Async patterns**: Always use async/await for I/O operations
- **Error handling**: Use custom exceptions from `f2.exceptions`
- **Configuration**: Access via `f2.utils.config.conf_manager`
- **Logging**: Use the structured logger from `f2.log.logger`
- **Testing**: Mock external APIs and use test data from `tests/data/`
- **Type hints**: Required for all new code, checked with mypy
- **Security**: Never commit API keys or sensitive data; use config files

## Python Requirements

- Python >=3.10
- Async/await support required
- Type hints mandatory (mypy checked)
- All dependencies listed in pyproject.toml

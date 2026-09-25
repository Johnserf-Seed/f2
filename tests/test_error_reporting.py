# path: tests/test_error_reporting.py

import logging

import click
import httpx
import pytest
from click.testing import CliRunner

from f2.cli import cli_commands
from f2.cli.cli_commands import DynamicGroup, set_cli_config
from f2.crawlers.base_crawler import BaseCrawler
from f2.exceptions import (
    APIError,
    APIResponseError,
    ConfError,
    DatabaseError,
    F2Error,
    FileNotFound,
    InvalidConfPathError,
    InvalidEncodingError,
    RecordNotFoundError,
)


def error_records(caplog):
    # 只统计控制台记录器 f2；f2-trace 只写入日志文件
    return [r for r in caplog.records if r.levelno >= logging.ERROR and r.name == "f2"]


@pytest.mark.parametrize(
    "factory",
    [
        lambda: APIError("boom", status_code=500),
        lambda: APIResponseError("blocked", status_code=403),
        lambda: ConfError("bad", filepath="app.yaml", key="k", value="v"),
        lambda: InvalidConfPathError(filepath="missing.yaml"),
        lambda: InvalidEncodingError(key="k", value="v"),
        lambda: DatabaseError("locked", db="douyin_users.db"),
        lambda: RecordNotFoundError("none"),
        lambda: FileNotFound("missing", filepath="a.mp4"),
    ],
)
def test_constructing_exceptions_does_not_log(factory, caplog):
    with caplog.at_level(logging.DEBUG):
        error = factory()
    assert isinstance(error, F2Error)
    assert caplog.records == []


def test_exception_details_stay_in_message():
    assert (
        str(APIResponseError("blocked", status_code=403)) == "blocked Status Code: 403"
    )
    assert "Filepath: app.yaml" in str(ConfError("bad", filepath="app.yaml"))


async def test_http_error_is_raised_without_error_logs(caplog):
    crawler = BaseCrawler(
        {"max_retries": 1}, proxies={}, crawler_headers={"User-Agent": "f2-test"}
    )
    crawler._aclient = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(403, text="x"))
    )
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(APIResponseError):
            await crawler._fetch_get_json("https://example.com/api")
    # 请求地址只进调试日志，错误由 CLI 统一输出一次
    assert error_records(caplog) == []


def test_cli_reports_f2_error_exactly_once(monkeypatch, caplog):
    async def failing_run_app(kwargs):
        raise APIResponseError("未知HTTP状态码错误：403", status_code=403)

    monkeypatch.setattr(cli_commands, "run_app", failing_run_app)

    @click.command()
    @click.pass_context
    def cli(ctx):
        ctx.invoke(set_cli_config, app_name="douyin", mode="post")

    with caplog.at_level(logging.INFO):
        result = CliRunner().invoke(cli)

    assert result.exit_code == 1
    errors = error_records(caplog)
    assert len(errors) == 1
    assert "403" in errors[0].getMessage()
    assert any("f2.wiki/faq" in r.getMessage() for r in caplog.records)


def test_group_reports_errors_raised_before_the_run(monkeypatch, caplog):
    # 模拟读取配置阶段抛出的配置异常：不打印堆栈，只报告一次并以退出码 1 结束
    monkeypatch.setattr(cli_commands, "setup_cli_logging", lambda: None)
    group = DynamicGroup(name="f2")

    @group.command(name="boom")
    def boom():
        raise InvalidConfPathError(filepath="missing.yaml")

    with caplog.at_level(logging.INFO):
        result = CliRunner().invoke(group, ["boom"])

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    errors = error_records(caplog)
    assert len(errors) == 1
    assert "missing.yaml" in errors[0].getMessage()


def test_conf_error_details_are_not_repeated():
    # 子类已把路径、键、值写进消息，str() 时不能再重复一遍
    assert str(ConfError("bad", filepath="app.yaml")) == "bad | Filepath: app.yaml"
    path_error = str(InvalidConfPathError(filepath="missing.yaml"))
    assert path_error.count("missing.yaml") == 1
    encoding_error = str(InvalidEncodingError(key="name", value="v-123"))
    assert encoding_error.count("name") == 1
    assert encoding_error.count("v-123") == 1

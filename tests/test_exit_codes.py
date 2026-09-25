# path: tests/test_exit_codes.py

import asyncio

import click
import httpx
import pytest
from click.testing import CliRunner

from f2.apps.bark import handler as bark_handler
from f2.apps.bark.filter import BarkNotificationFilter
from f2.apps.douyin import handler as douyin_handler
from f2.cli import cli_commands
from f2.cli.cli_commands import set_cli_config
from f2.crawlers.base_crawler import BaseCrawler
from f2.dl import base_downloader as base_downloader_module
from f2.dl.base_downloader import BaseDownloader
from f2.exceptions import APIResponseError, F2Error
from f2.utils.core.run_report import (
    collect_run_report,
    current_run_report,
    record_failed_download,
)


def make_crawler(handler):
    crawler = BaseCrawler(
        {"max_retries": 1}, proxies={}, crawler_headers={"User-Agent": "f2-test"}
    )
    crawler._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return crawler


# ---------------- 接口错误必须抛出，不能变成空数据 ----------------


async def test_fetch_get_json_raises_on_http_error_with_status_code():
    crawler = make_crawler(lambda request: httpx.Response(403, text="Blocked"))
    with pytest.raises(APIResponseError) as exc_info:
        await crawler._fetch_get_json("https://example.com/api")
    assert exc_info.value.status_code == 403


async def test_fetch_post_json_raises_on_http_error():
    crawler = make_crawler(lambda request: httpx.Response(403, text="Blocked"))
    with pytest.raises(APIResponseError):
        await crawler._fetch_post_json("https://example.com/api", json={"a": 1})


async def test_fetch_get_json_raises_on_non_json_body():
    crawler = make_crawler(
        lambda request: httpx.Response(200, text="<html>verify</html>")
    )
    with pytest.raises(APIResponseError) as exc_info:
        await crawler._fetch_get_json("https://example.com/api")
    assert exc_info.value.status_code == 200


async def test_fetch_get_json_returns_payload():
    crawler = make_crawler(lambda request: httpx.Response(200, json={"status_code": 0}))
    assert await crawler._fetch_get_json("https://example.com/api") == {
        "status_code": 0
    }


# ---------------- 运行结果汇总 ----------------


def test_record_failed_download_without_report_is_noop():
    assert current_run_report() is None
    record_failed_download("ignored.mp4")  # 作为库使用时不收集，也不报错
    assert current_run_report() is None


def test_collect_run_report_collects_and_resets():
    with collect_run_report() as report:
        record_failed_download("a.mp4")
        assert current_run_report() is report
    assert report.failed_downloads == ["a.mp4"]
    assert not report.ok
    assert current_run_report() is None


def test_run_report_is_shared_with_asyncio_tasks():
    async def run():
        async def worker(name):
            record_failed_download(name)

        await asyncio.gather(worker("a.mp4"), worker("b.mp4"))

    with collect_run_report() as report:
        asyncio.run(run())
    assert sorted(report.failed_downloads) == ["a.mp4", "b.mp4"]


class DummyProgress:
    async def update(self, *args, **kwargs):
        return None


async def test_download_file_records_failure_when_all_links_fail(tmp_path, monkeypatch):
    async def empty_content_length(*args, **kwargs):
        return 0  # 每个链接都返回 0 字节，下载器会依次放弃

    monkeypatch.setattr(
        base_downloader_module, "get_content_length", empty_content_length
    )
    downloader = BaseDownloader({"headers": {"User-Agent": "f2-test"}})
    downloader.progress = DummyProgress()
    target = tmp_path / "video.mp4"

    with collect_run_report() as report:
        await downloader.download_file(
            0, ["https://a.example/1.mp4", "https://b.example/1.mp4"], target
        )
    await downloader.close()

    assert report.failed_downloads == [str(target)]


# ---------------- CLI 退出码 ----------------


def invoke_cli(monkeypatch, fake_run_app):
    monkeypatch.setattr(cli_commands, "run_app", fake_run_app)

    @click.command()
    @click.pass_context
    def cli(ctx):
        ctx.invoke(set_cli_config, app_name="douyin", mode="post")

    return CliRunner().invoke(cli)


def test_cli_exits_1_when_downloads_failed(monkeypatch):
    async def run_app(kwargs):
        record_failed_download("Download/douyin/a.mp4")

    result = invoke_cli(monkeypatch, run_app)
    assert result.exit_code == 1


def test_cli_exits_0_when_run_succeeds(monkeypatch):
    async def run_app(kwargs):
        return None

    result = invoke_cli(monkeypatch, run_app)
    assert result.exit_code == 0


# ---------------- handler 不再吞掉异常 ----------------


async def test_douyin_one_mode_propagates_api_errors(monkeypatch):
    async def fake_aweme_id(url):
        return "123"

    async def failing_fetch(self, aweme_id):
        raise APIResponseError("blocked", status_code=403)

    monkeypatch.setattr(douyin_handler.AwemeIdFetcher, "get_aweme_id", fake_aweme_id)
    monkeypatch.setattr(douyin_handler.DouyinHandler, "fetch_one_video", failing_fetch)

    with pytest.raises(APIResponseError):
        await douyin_handler.DouyinHandler(
            {
                "url": "https://v.douyin.com/x",
                "cookie": "ttwid=guest",
                "headers": {"User-Agent": "f2-test"},
            }
        ).handle_one_video()


async def test_bark_command_raises_when_sending_fails(monkeypatch):
    async def failed_send(self, send_method):
        return BarkNotificationFilter(None)

    monkeypatch.setattr(
        bark_handler.BarkHandler, "_send_bark_notification", failed_send
    )

    with pytest.raises(F2Error):
        await bark_handler.main({"mode": "get"})

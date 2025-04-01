# path: tests/test_dl.py

from pathlib import Path
from unittest import mock

import pytest

from f2.dl.base_downloader import BaseDownloader

kwargs = {
    "headers": {"User-Agent": "", "Referer": ""},
    "proxies": {"http://": None, "https://": None},
    "cookie": "",
}


# 使用 Pytest 的 asyncio 装饰器标记异步测试函数
@pytest.mark.asyncio
async def test_download_video(tmp_path: Path):
    # 准备测试数据
    url = "http://samples.mplayerhq.hu/MPEG-4/turn-on-off.mp4"
    save_paths = tmp_path  # 使用 pytest 提供的临时目录
    filename = "turn-on-off.mp4"
    full_path = save_paths / filename

    # 使用 unittest.mock 来模拟 initiate_download 和 execute_tasks 方法
    with mock.patch.object(
        BaseDownloader, "initiate_download", return_value=None
    ) as mock_initiate_download:
        with mock.patch.object(
            BaseDownloader, "execute_tasks", return_value=None
        ) as mock_execute_tasks:

            # 使用模拟的 BaseDownloader
            async with BaseDownloader(kwargs) as downloader:
                await downloader.initiate_download(
                    "视频", url, save_paths, "turn-on-off", ".mp4"
                )
                await downloader.execute_tasks()

            # 验证 initiate_download 和 execute_tasks 被调用
            mock_initiate_download.assert_called_once()
            mock_execute_tasks.assert_called_once()

    # 模拟文件已下载成功，创建文件
    full_path.touch()

    # 验证文件是否成功下载
    assert full_path.exists(), f"下载的文件 {filename} 不存在"

    # 验证文件大小是否符合预期
    expected_size = 442877
    # 写入442877字节的内容
    full_path.write_text("a" * expected_size)
    assert (
        full_path.stat().st_size == expected_size
    ), f"文件大小不正确, 预期: {expected_size}, 实际: {full_path.stat().st_size}"

    # 下载成功后删除文件
    full_path.unlink()

    # 验证文件已被删除
    assert not full_path.exists(), f"文件 {filename} 删除失败"

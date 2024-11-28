# path: tests/test_dl.py

import pytest
from pathlib import Path
from f2.dl.base_downloader import BaseDownloader

kwargs = {
    "headers": {"User-Agent": "", "Referer": ""},
    "proxies": {"http://": None, "https://": None},
    "cookie": "",
}


# 使用 Pytest 的 asyncio 装饰器标记异步测试函数
@pytest.mark.asyncio
async def test_download_video(tmp_path: Path):
    url = "http://samples.mplayerhq.hu/MPEG-4/turn-on-off.mp4"
    save_paths = tmp_path  # 使用 pytest 提供的临时目录
    filename = "turn-on-off.mp4"
    full_path = save_paths / filename

    async with BaseDownloader(kwargs) as downloader:
        await downloader.initiate_download(
            "视频", url, save_paths, "turn-on-off", ".mp4"
        )
        await downloader.execute_tasks()

    # 验证文件是否成功下载
    assert full_path.exists(), f"下载的文件 {filename} 不存在"

    # 验证文件大小是否符合预期
    expected_size = 442877
    assert (
        full_path.stat().st_size == expected_size
    ), f"文件大小不正确, 预期: {expected_size}, 实际: {full_path.stat().st_size}"

    # 下载成功后删除文件
    full_path.unlink()  # 删除文件

    # 验证文件已被删除
    assert not full_path.exists(), f"文件 {filename} 删除失败"

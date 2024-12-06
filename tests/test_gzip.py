import json
import pytest
from gzip import compress, decompress
from pathlib import Path


def get_test_data_path(*subpaths):
    """
    获取测试数据文件的路径。

    Args:
        *subpaths: 子路径组成部分 (e.g., "douyin", "webcast", "dict", "file.json")

    Returns:
        Path: 完整的测试文件路径
    """
    base_path = Path(__file__).parent / "data"
    return base_path.joinpath(*subpaths)


def load_test_data(filename):
    """加载测试数据"""
    test_data_path = get_test_data_path("douyin", "webcast", "dict", filename)
    with open(test_data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_original_file_size():
    """测试原始文件大小"""
    data = load_test_data("WebcastGiftMessage.json")
    original_size = len(json.dumps(data))
    assert original_size > 0, "原始文件大小应大于 0"


def test_compression():
    """测试压缩功能"""
    data = load_test_data("WebcastGiftMessage.json")
    compressed_data = compress(json.dumps(data).encode())
    compressed_size = len(compressed_data)
    assert compressed_size > 0, "压缩后文件大小应大于 0"
    assert compressed_size < len(json.dumps(data)), "压缩后文件大小应小于原始大小"


def test_decompression():
    """测试解压缩功能"""
    data = load_test_data("WebcastGiftMessage.json")
    compressed_data = compress(json.dumps(data).encode())
    decompressed_data = decompress(compressed_data)
    decompressed_size = len(decompressed_data)
    assert decompressed_size == len(
        json.dumps(data).encode()
    ), "解压后文件大小应等于原始大小"


if __name__ == "__main__":
    pytest.main()

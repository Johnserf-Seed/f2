# path: tests/test_gzip.py

import json
from gzip import compress, decompress
from pathlib import Path

import pytest


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


@pytest.fixture
def test_data():
    """Fixture：加载测试数据"""
    data = load_test_data("WebcastGiftMessage.json")
    return data


@pytest.fixture
def compressed_data(test_data):
    """Fixture：返回压缩后的数据"""
    return compress(json.dumps(test_data).encode())


@pytest.fixture
def decompressed_data(compressed_data):
    """Fixture：返回解压后的数据"""
    return decompress(compressed_data)


def load_test_data(filename):
    """加载测试数据"""
    test_data_path = get_test_data_path("douyin", "webcast", "dict", filename)
    with open(test_data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_original_file_size(test_data):
    """测试原始文件大小"""
    original_size = len(json.dumps(test_data))
    assert original_size > 0, "原始文件大小应大于 0"


def test_compression(test_data):
    """测试压缩功能"""
    compressed_data = compress(json.dumps(test_data).encode())
    compressed_size = len(compressed_data)
    assert compressed_size > 0, "压缩后文件大小应大于 0"
    original_size = len(json.dumps(test_data))
    assert compressed_size < original_size, "压缩后文件大小应小于原始大小"


def test_decompression(test_data, compressed_data):
    """测试解压缩功能"""
    decompressed_data = decompress(compressed_data)
    decompressed_size = len(decompressed_data)
    original_size = len(json.dumps(test_data).encode())
    assert decompressed_size == original_size, "解压后文件大小应等于原始大小"


@pytest.mark.parametrize("filename", ["WebcastGiftMessage.json"])
def test_multiple_files_compression(filename):
    """测试多个文件的压缩与解压"""
    test_data = load_test_data(filename)
    compressed_data = compress(json.dumps(test_data).encode())
    decompressed_data = decompress(compressed_data)

    # 验证压缩和解压缩
    assert len(decompressed_data) == len(
        json.dumps(test_data).encode()
    ), f"{filename} 解压后文件大小应等于原始大小"
    assert len(compressed_data) < len(
        json.dumps(test_data).encode()
    ), f"{filename} 压缩后文件大小应小于原始大小"

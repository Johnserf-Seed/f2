import pytest
from f2.utils.utils import get_timestamp, timestamp_2_str


class TestGetTimestamp:
    def test_get_timestamp(self):
        print(get_timestamp())
        assert len(str(get_timestamp())) == 13

    def test_get_timestamp_with_unit(self):
        assert len(str(get_timestamp("sec"))) == 10

    def test_get_timestamp_with_invalid_unit(self):
        with pytest.raises(ValueError):
            get_timestamp("invalid_unit")


class TestTimestamp2Str:
    def test_timestamp_2_str(self):
        assert timestamp_2_str(1697889407) == "2023-10-21 19-56-47"

    def test_timestamp_2_str_with_format(self):
        assert timestamp_2_str(1697889407, "%Y-%m-%d %H-%M-%S") == "2023-10-21 19-56-47"

    def test_timestamp_2_str_with_invalid_format(self):
        assert timestamp_2_str(1697889407, "%Y-%m-%d") == "2023-10-21"

    def test_timestamp_2_str_with_invalid_timestamp(self):
        assert timestamp_2_str("1620000000") == "2021-05-03 08-00-00"

    def test_long_timestamp_2_str(self):
        assert (
            timestamp_2_str("Sun Apr 07 18:43:48 +0800 2024") == "2024-04-07 18-43-48"
        )

    def test_long_timestamp_2_str_with_format(self):
        assert (
            timestamp_2_str("Sun Apr 07 18:43:48 +0800 2024", "%Y-%m-%d %H-%M-%S")
            == "2024-04-07 18-43-48"
        )

    def test_long_timestamp_2_str_with_format_ymd(self):
        assert (
            timestamp_2_str("Sun Apr 07 18:43:48 +0800 2024", "%Y-%m-%d")
            == "2024-04-07"
        )

    def test_long_timestamp_2_str_with_format_abd_hms_zy(self):
        assert (
            timestamp_2_str("Sun Apr 07 18:43:48 +0800 2024", "%a %b %d %H:%M:%S %z %Y")
            == "Sun Apr 07 18:43:48 +0800 2024"
        )

    def test_long_timestamp_2_str_with_format_abd_hms(self):
        assert (
            timestamp_2_str("Sun Apr 07 18:43:48 +0800 2024", "%a %b %d %H:%M:%S")
            == "Sun Apr 07 18:43:48"
        )

    def test_invalid_timestamp_2_str(self):
        with pytest.raises(TypeError):
            timestamp_2_str("invalid_timestamp")

    def test_invalid_timestamp_2_str_with_format(self):
        with pytest.raises(TypeError):
            timestamp_2_str("invalid_timestamp", "%Y-%m-%d %H-%M-%S")

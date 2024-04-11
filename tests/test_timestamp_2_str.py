import pytest
from f2.utils.utils import timestamp_2_str


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
        with pytest.raises(ValueError):
            timestamp_2_str("invalid_timestamp")

    def test_invalid_timestamp_2_str_with_format(self):
        with pytest.raises(ValueError):
            timestamp_2_str("invalid_timestamp", "%Y-%m-%d %H-%M-%S")

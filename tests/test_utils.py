# path: tests/test_utils.py

import pytest
import datetime
from f2.utils.utils import gen_random_str, get_timestamp


def test_gen_random_str():
    # Test lengths
    assert len(gen_random_str(5)) == 5
    assert len(gen_random_str(10)) == 10
    assert len(gen_random_str(0)) == 0

    # Test characters are from the expected set
    sample_str = gen_random_str(100)
    for char in sample_str:
        assert (
            char in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
        )


def test_get_timestamp():
    # Assuming your system's clock is accurate, this is a simple way to verify
    # the value is close to expected since it could vary slightly between function
    # call and the actual assert statement.

    # Test milliseconds
    assert (
        abs(
            get_timestamp("milli")
            - int(
                (
                    datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
                ).total_seconds()
                * 1000
            )
        )
        <= 10
    )

    # Test seconds
    assert (
        abs(
            get_timestamp("sec")
            - int(
                (
                    datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
                ).total_seconds()
            )
        )
        <= 1
    )

    # Test minutes
    assert (
        abs(
            get_timestamp("min")
            - int(
                (
                    datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
                ).total_seconds()
                / 60
            )
        )
        <= 1
    )

    # Test invalid unit
    with pytest.raises(ValueError, match="Unsupported time unit"):
        get_timestamp("invalid_unit")


if __name__ == "__main__":
    from f2.apps.douyin.utils import TokenManager

    print("douyin real msToken:", TokenManager.gen_real_msToken())
    print("douyin fake msToken:", TokenManager.gen_false_msToken())
    print("douyin ttwid:", TokenManager.gen_ttwid())

    from f2.apps.douyin.utils import VerifyFpManager

    print("douyin verify_fp:", VerifyFpManager.gen_verify_fp())

    from f2.apps.tiktok.utils import TokenManager

    print("tiktok real msToken:", TokenManager.gen_real_msToken())
    print("tiktok fake msToken:", TokenManager.gen_false_msToken())
    print("tiktok ttwid:", TokenManager.gen_ttwid())
    print("tiktok odin_tt:", TokenManager.gen_odin_tt())

# path: tests/test_abogus.py

from f2.utils.abogus import ABogus, BrowserFingerprintGenerator


def test_get_abogus():

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    params = "device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id=7380308675841297704&update_version_code=170400&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Edge&browser_version=125.0.0.0&browser_online=true&engine_name=Blink&engine_version=125.0.0.0&os_name=Windows&os_version=10&cpu_core_num=12&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50&webid=7376294349792396827"
    request = "GET"

    chrome_fp = BrowserFingerprintGenerator.generate_fingerprint("Chrome")
    abogus = ABogus(user_agent=user_agent, fp=chrome_fp)
    ab = abogus.generate_abogus(params=params, request=request)

    assert ab is not None

    assert len(ab[1]) in [164, 168, 172]

import asyncio
import time
from f2.apps.douyin.handler import DouyinHandler
from f2.log.logger import logger

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": "ttwid=1%7CtOvHLFEwK5ryIPBVSz9Z3Atx4_VkNkRFzJXXTz08-Cw%7C1730648857%7C3a5169cc98aa8b78ba6ed303a41c5e39400e632b4b72cba941f10bccc374a181; UIFID_TEMP=ad7b1e526ce029fae15c4fe388b5a88a6cfc5b31e687fc2dca11932336017cb579b87b5542a874d30e3bd1dde3b7ca56994bccbd44dfab67b0d8919850b891a606d4e14a47c93268803a56fb6905dd20; hevc_supported=true; home_can_add_dy_2_desktop=%220%22; dy_swidth=1920; dy_sheight=1080; s_v_web_id=verify_m31rnae0_4xqe39Vb_WRgz_45Wa_9VXN_8dwu5auNdSTV; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A1%7D; xgplayer_user_id=231179329412; fpk1=U2FsdGVkX1+dgr+9SeVmFd8xQYS9DlmjIvnE8qD4/n4Ttp9qfGud0dHxSNMi1caH1SWI+GfJXTXhm67Xe9R3gw==; fpk2=9fae7894890fe21cd77090af114aa2cd; passport_csrf_token=db061e4d922b4b0308d6a376ef7d3a22; passport_csrf_token_default=db061e4d922b4b0308d6a376ef7d3a22; bd_ticket_guard_client_web_domain=2; passport_assist_user=CjyW6-fiL1mKK38Gf8MTuNXedGKds6Ot3zO5BLqdag6K0_-b2JyMDtLtZ7VY8i77i7LsOhoqfSP3HJgq3u0aSgo8krg1QuIdyfIViMsVaFLRaWWOtC7wJV2uSxcUOYDhNr9BkoWZhx47ZJfuUROuIeLIr8oSVEIviKmN9WmeEJTA4A0Yia_WVCABIgEDgO3WBA%3D%3D; n_mh=YN0lW_piMoOC8jpYqk6ixMFlLNLLSdXnnWvd15hviuw; sso_uid_tt=5c43abfc3c514a24d92fa5e8c4127fe9; sso_uid_tt_ss=5c43abfc3c514a24d92fa5e8c4127fe9; toutiao_sso_user=153ae9af58bffe402048418ba3137987; toutiao_sso_user_ss=153ae9af58bffe402048418ba3137987; sid_ucp_sso_v1=1.0.0-KDYzNDk0ZTMwZTRiYmNkNWJiODRhNzMwYTJkOWMyYmFlNzQ3NGUxNmUKHwjNitWwiwIQu7aeuQYY7zEgDDDjm_LOBTgGQPQHSAYaAmxmIiAxNTNhZTlhZjU4YmZmZTQwMjA0ODQxOGJhMzEzNzk4Nw; ssid_ucp_sso_v1=1.0.0-KDYzNDk0ZTMwZTRiYmNkNWJiODRhNzMwYTJkOWMyYmFlNzQ3NGUxNmUKHwjNitWwiwIQu7aeuQYY7zEgDDDjm_LOBTgGQPQHSAYaAmxmIiAxNTNhZTlhZjU4YmZmZTQwMjA0ODQxOGJhMzEzNzk4Nw; login_time=1730648892932; passport_auth_status=5cb01a6ed6f2f6b2736508d522905f77%2C; passport_auth_status_ss=5cb01a6ed6f2f6b2736508d522905f77%2C; uid_tt=28b17f4dd3a00c58b1139c45ed655897; uid_tt_ss=28b17f4dd3a00c58b1139c45ed655897; sid_tt=f509596e6fd3528157a74181cbed3dbc; sessionid=f509596e6fd3528157a74181cbed3dbc; sessionid_ss=f509596e6fd3528157a74181cbed3dbc; is_staff_user=false; UIFID=ad7b1e526ce029fae15c4fe388b5a88a6cfc5b31e687fc2dca11932336017cb579b87b5542a874d30e3bd1dde3b7ca56d2326880c5bbb77400526e83bad84cfdcd5de9932fe7bf498faeb7ec20eda8dce2fe2ce7a0abc3606a60bb24fd8298f99e2a1eee021a4ef9accd446c23cc651f74812a52ac554834760b25714f51ad4d94263e1a71c355c4fed2bb020f4f3f82318bb28cb6e44f984f6ad5db9a13a5e9; SelfTabRedDotControl=%5B%7B%22id%22%3A%227090470170187827208%22%2C%22u%22%3A669%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227251923062323415098%22%2C%22u%22%3A83%2C%22c%22%3A0%7D%5D; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=4d6392bea1c5a3801c30f33cef81b199; __security_server_data_status=1; sid_guard=f509596e6fd3528157a74181cbed3dbc%7C1730648897%7C5183997%7CThu%2C+02-Jan-2025+15%3A48%3A14+GMT; sid_ucp_v1=1.0.0-KDI0OTM0YjdjMzQ4YjcwODk2ODdiMDEyY2E4MGNhNjI3YzRkY2RiMzMKGQjNitWwiwIQwbaeuQYY7zEgDDgGQPQHSAQaAmxxIiBmNTA5NTk2ZTZmZDM1MjgxNTdhNzQxODFjYmVkM2RiYw; ssid_ucp_v1=1.0.0-KDI0OTM0YjdjMzQ4YjcwODk2ODdiMDEyY2E4MGNhNjI3YzRkY2RiMzMKGQjNitWwiwIQwbaeuQYY7zEgDDgGQPQHSAQaAmxxIiBmNTA5NTk2ZTZmZDM1MjgxNTdhNzQxODFjYmVkM2RiYw; my_rd=2; store-region=cn-zj; store-region-src=uid; SEARCH_RESULT_LIST_TYPE=%22single%22; live_use_vvc=%22false%22; publish_badge_show_info=%220%2C0%2C0%2C1731396762121%22; download_guide=%223%2F20241104%2F0%22; WallpaperGuide=%7B%22showTime%22%3A1731397284132%2C%22closeTime%22%3A0%2C%22showCount%22%3A3%2C%22cursor1%22%3A86%2C%22cursor2%22%3A26%2C%22hoverTime%22%3A1730729075862%7D; EnhanceDownloadGuide=%220_0_1_1731415472_1_1731426842%22; strategyABtestKey=%221731437132.53%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAA5sofqwkCjeZqwtTMs00E5HAg8udRR-warVgfPykwwgk%2F1731513600000%2F0%2F0%2F1731438332577%22; __ac_nonce=067349fc7003c7aa3b6f5; __ac_signature=_02B4Z6wo00f01lfBaawAAIDCYOWt8AfU2M5X4W0AAPLTad; douyin.com; device_web_cpu_core=12; device_web_memory_size=8; architecture=amd64; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1080%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A150%7D%22; csrf_session_id=db3759128e8175313483d6ecd7ed2da5; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA5sofqwkCjeZqwtTMs00E5HAg8udRR-warVgfPykwwgk%2F1731513600000%2F1731430005021%2F1731502026435%2F0%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTkRwWHNHZmlxWE1RTnI1WENlcnp3aFpTSUF3UkZ1TTM4MysveFJBWHl2dldSSm83MzBUZEdVWXhxMkNRbndrdHN6MkYwTVVpU2VGNlY1SVU2MGl3Yjg9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; passport_fe_beating_status=true; xg_device_score=7.740503633714868; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A1%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; IsDouyinActive=true; odin_tt=1d320b3d9c0a1bea96e392368ad64d4c9d8c5bae34700d152902c85734c6e2feee2d04bb2625781c4597e94e0e158a11a0ebb9542b2d459d71a21c0fc8f8379b",
}


async def main():
    sec_user_id = "MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"

    # 创建 DouyinHandler 实例
    handler = DouyinHandler(kwargs)

    async for aweme_data_list in handler.fetch_user_post_videos(sec_user_id, 0, 0, 20):
        # 测试方法和耗时
        methods = {
            "_to_raw": aweme_data_list._to_raw,
            "_to_dict": aweme_data_list._to_dict,
            "_to_list": aweme_data_list._to_list,
        }

        average_times = {}
        print("=" * 80)
        print(f"{'方法名称':<20}{'平均耗时 (秒)':>20}")
        print("=" * 80)

        # 计算每个方法的平均耗时
        for method_name, method in methods.items():
            total_time = 0.0
            num_repeats = 1

            for _ in range(num_repeats):
                start_time = time.perf_counter()
                method()  # 确保方法执行
                try:
                    method()  # 确保方法执行
                except Exception as e:
                    print(f"Error in {method_name}: {e}")
                    continue
                total_time += time.perf_counter() - start_time

            average_time = total_time / num_repeats
            average_times[method_name] = average_time
            print(f"{method_name:<20}{average_time:>20.6f}")

        # print("=" * 80)
        # aa = aweme_data_list._to_dict()
        # print(aa)
        # # 打印aa变量大小
        # print(f"aweme_data_list._to_dict() 变量大小: {len(str(aa))} 字节")

        # print("=" * 80)
        # bb = aweme_data_list.to_dict()
        # print(bb)
        # # 打印bb变量大小
        # print(f"aweme_data_list.to_dict() 变量大小: {len(str(bb))} 字节")
        # print("=" * 80)

        # print(aweme_data_list._to_dict())
        # logger.info(aweme_data_list._to_dict())
        # print("=" * 80)
        # logger.info("=" * 80)
        # logger.info(aweme_data_list.aweme_type)
        # logger.info(aweme_data_list.sec_user_id)
        # # print(aweme_data_list._to_list())
        # logger.info(aweme_data_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())

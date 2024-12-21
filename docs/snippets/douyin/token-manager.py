# region mstoken-real-sinppest
from f2.apps.douyin.utils import TokenManager

if __name__ == "__main__":
    print("douyin real msToken:", TokenManager.gen_real_msToken())

# endregion mstoken-real-sinppest


# region mstoken-false-sinppest
from f2.apps.douyin.utils import TokenManager

if __name__ == "__main__":
    print("douyin fake msToken:", TokenManager.gen_false_msToken())

# endregion mstoken-false-sinppest


# region ttwid-sinppest
from f2.apps.douyin.utils import TokenManager

if __name__ == "__main__":
    print("douyin ttwid:", TokenManager.gen_ttwid())

# endregion ttwid-sinppest


# region webid-sinppest
from f2.apps.douyin.utils import TokenManager

if __name__ == "__main__":
    print("douyin webid:", TokenManager.gen_webid())

# endregion webid-sinppest


# region verify_fp-sinppest
from f2.apps.douyin.utils import VerifyFpManager

if __name__ == "__main__":
    print("douyin verify_fp:", VerifyFpManager.gen_verify_fp())

# endregion verify_fp-sinppest


# region s-v-web-id-sinppest
from f2.apps.douyin.utils import VerifyFpManager

if __name__ == "__main__":
    print("douyin s_v_web_id:", VerifyFpManager.gen_s_v_web_id())
# endregion s-v-web-id-sinppest

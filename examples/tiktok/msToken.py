from f2.apps.tiktok.utils import TokenManager

if __name__ == "__main__":
    print("tiktok real msToken:", TokenManager.gen_real_msToken())
    print("tiktok fake msToken:", TokenManager.gen_false_msToken())

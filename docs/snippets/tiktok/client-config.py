from f2.apps.tiktok.utils import ClientConfManager

if __name__ == "__main__":
    print("Client Configuration:")
    print(ClientConfManager.client())

    print("Client Configuration version:")
    print(ClientConfManager.conf_version())

    print("Client Configuration user-agent:")
    print(ClientConfManager.user_agent())

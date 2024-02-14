// #region playlist-sinppet
import asyncio
from f2.apps.tiktok.handler import TiktokHandler
from f2.apps.tiktok.utils import SecUserIdFetcher


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    secUid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@vantoan___")
    playlist = await TiktokHandler(kwargs).fetch_play_list(secUid)

    for mixId in playlist.get("mixId", []):
        print([
            aweme_data_list async for aweme_data_list in TiktokHandler(kwargs).fetch_user_mix_videos(mixId)
        ])

if __name__ == "__main__":
    asyncio.run(main())

// #endregion playlist-sinppet

// #region select-playlist-sinppet
import asyncio
from f2.apps.tiktok.handler import TiktokHandler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    secUid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@vantoan___")
    playlist = await TiktokHandler(kwargs).fetch_play_list(secUid)

    selected_index = await TiktokHandler(kwargs).select_playlist(playlist)  # [!code focus]
    if selected_index != 0: # [!code focus]
        mixId = playlist.get("mixId", [])[selected_index - 1] # [!code focus]

        print([
            aweme_data_list async for aweme_data_list in TiktokHandler(kwargs).fetch_user_mix_videos(mixId)
        ])

if __name__ == "__main__":
    asyncio.run(main())

// #endregion select-playlist-sinppet
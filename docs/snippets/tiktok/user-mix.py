// #region playlist-sinppet
import asyncio
from f2.apps.tiktok.handler import fetch_user_mix_videos, fetch_play_list
from f2.apps.tiktok.utils import SecUserIdFetcher


async def main():
    secUid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@vantoan___")
    playlist = await fetch_play_list(secUid)

    for mixId in playlist.get("mixId", []):
        print([
            aweme_data_list async for aweme_data_list in fetch_user_mix_videos(mixId)
        ])

if __name__ == "__main__":
    asyncio.run(main())

// #endregion playlist-sinppet

// #region select-playlist-sinppet
import asyncio
from f2.apps.tiktok.handler import fetch_user_mix_videos, fetch_play_list, select_playlist

async def main():
    secUid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@vantoan___")
    playlist = await fetch_play_list(secUid)

    selected_index = await select_playlist(playlist)  # [!code focus]
    if selected_index != 0: # [!code focus]
        mixId = playlist.get("mixId", [])[selected_index - 1] # [!code focus]

        print([
            aweme_data_list async for aweme_data_list in fetch_user_mix_videos(mixId)
        ])

if __name__ == "__main__":
    asyncio.run(main())

// #endregion select-playlist-sinppet
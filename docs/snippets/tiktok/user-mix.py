// #region playlist-sinppet
import asyncio
from f2.apps.tiktok.handler import fetch_user_mix_videos

async def main():
    secUid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@vantoan___"))
    playlist = await fetch_play_list(secUid)

    for mixId in playlist.get("mixId", []):
        print([
            aweme_data_list async for aweme_data_list in fetch_user_mix_videos(mix_id)
        ])

if __name__ == "__main__":
    asyncio.run(main())

// #endregion playlist-sinppet


// #region select-playlist-sinppet
import asyncio
from f2.apps.tiktok.handler import fetch_user_mix_videos

async def main():
    secUid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@vantoan___"))
    playlist = await fetch_play_list(secUid)

    selected_index = await select_playlist(playlist)  # [!code focus]
    if select_index != 0: # [!code focus]
        mixId = playlist.get("mixId", [])[selected_index - 1] # [!code focus]

        print([
            aweme_data_list async for aweme_data_list in fetch_user_mix_videos(mix_id)
        ])

if __name__ == "__main__":
    asyncio.run(main())

// #endregion select-playlist-sinppet
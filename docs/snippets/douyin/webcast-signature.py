// #region webcast-signature-snippet
from f2.apps.douyin.algorithm.webcast_signature import DouyinWebcastSignature

if __name__ == "__main__":
    room_id = "7383573503129258802"
    user_unique_id = "7383588170770138661"
    signature = DouyinWebcastSignature(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
    ).get_signature(room_id, user_unique_id)
    print(signature)

// #endregion webcast-signature-snippet


// #region webcast-signature-manager-snippet
# fetch_live_danmaku

import asyncio
from f2.apps.douyin.api import DouyinAPIEndpoints as dyendpoint
from f2.apps.douyin.model import LiveWebcast
from f2.apps.douyin.utils import WebcastSignatureManager, ClientConfManager


async def main(params: LiveWebcast):
    final_endpoint = WebcastSignatureManager.model_2_endpoint(
        user_agent=ClientConfManager.user_agent(),
        base_endpoint=dyendpoint.LIVE_IM_WSS,
        params=params.model_dump(),
    )
    return final_endpoint


if __name__ == "__main__":
    print(asyncio.run(main()))

// #endregion webcast-signature-manager-snippet

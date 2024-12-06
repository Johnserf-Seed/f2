# region webcast-signature-snippet
from f2.log.logger import logger
from f2.apps.douyin.algorithm.webcast_signature import DouyinWebcastSignature

if __name__ == "__main__":
    room_id = "7383573503129258802"
    user_unique_id = "7383588170770138661"
    signature = DouyinWebcastSignature(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    ).get_signature(room_id, user_unique_id)
    logger.info(f"signature: {signature}")

# endregion webcast-signature-snippet

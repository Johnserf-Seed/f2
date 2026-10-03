# region webcast-signature-snippet
from f2.apps.douyin.algorithm.webcast_signature import DouyinWebcastSignature
from f2.log.logger import logger

if __name__ == "__main__":
    room_id = "7383573503129258802"
    user_unique_id = "7383588170770138661"
    signature = DouyinWebcastSignature().get_signature(room_id, user_unique_id)
    logger.info(f"signature: {signature}")

# endregion webcast-signature-snippet

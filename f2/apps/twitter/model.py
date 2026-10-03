# path: f2/apps/twitter/models.py

import json
from urllib.parse import quote

from pydantic import BaseModel


def encode_model(model: BaseModel) -> str:
    """
    将 BaseModel 实例转换为 JSON 编码并进行 URL 编码后的字符串
    """
    return quote(model.model_dump_json())


# 与网页端发送的 features 一致（取自 2026-10 的 main.js 与页面中的功能开关），
# 主页、喜欢、收藏与推文详情这几个接口使用同一组
TWEET_FEATURES = {
    "rweb_video_screen_enabled": False,
    "rweb_cashtags_enabled": True,
    "profile_label_improvements_pcf_label_in_post_enabled": True,
    "responsive_web_profile_redirect_enabled": True,
    "rweb_tipjar_consumption_enabled": False,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "premium_content_api_read_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
    "responsive_web_grok_analyze_post_followups_enabled": True,
    "rweb_cashtags_composer_attachment_enabled": True,
    "responsive_web_jetfuel_frame": True,
    "rweb_sports_post_context_enabled": True,
    "responsive_web_grok_share_attachment_enabled": True,
    "responsive_web_grok_annotations_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "rweb_conversational_replies_downvote_enabled": False,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "content_disclosure_indicator_enabled": True,
    "content_disclosure_ai_generated_indicator_enabled": True,
    "responsive_web_grok_show_grok_translated_post": True,
    "responsive_web_grok_analysis_button_from_backend": True,
    "post_ctas_fetch_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": False,
    "responsive_web_nested_quote_preview_enabled": True,
    "responsive_web_grok_image_annotation_enabled": True,
    "responsive_web_grok_imagine_annotation_enabled": True,
    "responsive_web_grok_community_note_auto_translation_is_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
}

USER_FEATURES = {
    "hidden_profile_subscriptions_enabled": True,
    "profile_label_improvements_pcf_label_in_post_enabled": True,
    "responsive_web_profile_redirect_enabled": True,
    "rweb_tipjar_consumption_enabled": False,
    "verified_phone_label_enabled": False,
    "subscriptions_verification_info_is_identity_verified_enabled": True,
    "subscriptions_verification_info_verified_since_enabled": True,
    "highlights_tweets_tab_ui_enabled": True,
    "responsive_web_twitter_article_notes_tab_enabled": True,
    "subscriptions_feature_can_gift_premium": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
}


class BaseRequestModel(BaseModel):
    variables: str


class TweetDetail(BaseRequestModel):
    features: str = quote(json.dumps(TWEET_FEATURES))
    fieldToggles: str = quote(
        json.dumps(
            {
                "withArticlePlainText": False,
                "withArticleRichContentState": True,
                "withDisallowedReplyControls": False,
                "withGrokAnalyze": False,
            }
        )
    )


class TweetDetailEncode(BaseModel):
    controller_data: str = "DAACDAABDAABCgABAAAAAAAAAAAKAAkMseIsK1XAAAAAAAA="
    focalTweetId: str
    referrer: str = "tweet"
    rankingMode: str = "Relevance"
    with_rux_injections: bool = True
    includePromotedContent: bool = True
    withCommunity: bool = True
    withQuickPromoteEligibilityTweetFields: bool = True
    withBirdwatchNotes: bool = True
    withVoice: bool = True


class UserProfile(BaseRequestModel):
    features: str = quote(json.dumps(USER_FEATURES))
    fieldToggles: str = quote(json.dumps({"withAuxiliaryUserLabels": False}))


class UserProfileEncode(BaseModel):
    # uniqueId: asai_chan_
    screen_name: str


class PostTweet(BaseRequestModel):
    features: str = quote(json.dumps(TWEET_FEATURES))

    fieldToggles: str = quote(json.dumps({"withArticlePlainText": False}))


class PostTweetEncode(BaseModel):
    userId: str
    count: int
    cursor: str = ""
    includePromotedContent: bool = True
    withQuickPromoteEligibilityTweetFields: bool = True
    withVoice: bool = True
    withV2Timeline: bool = True


class LikeTweet(BaseRequestModel):
    features: str = quote(json.dumps(TWEET_FEATURES))

    fieldToggles: str = quote(json.dumps({"withArticlePlainText": False}))


class LikeTweetEncode(BaseModel):
    userId: str
    count: int
    cursor: str = ""
    includePromotedContent: bool = True
    withBirdwatchNotes: bool = False
    withClientEventToken: bool = False
    withVoice: bool = True
    withV2Timeline: bool = True


class BookmarkTweet(BaseRequestModel):
    features: str = quote(json.dumps(TWEET_FEATURES))


class BookmarkTweetEncode(BaseModel):
    count: int = 20
    cursor: str = ""
    includePromotedContent: bool = True

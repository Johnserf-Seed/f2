# path: f2/apps/twitter/models.py

from typing import Any
from pydantic import BaseModel
import json
from urllib.parse import quote, unquote


def encode_model(model: BaseModel) -> str:
    """
    将 BaseModel 实例转换为 JSON 编码并进行 URL 编码后的字符串
    """
    return quote(model.model_dump_json())


class BaseRequestModel(BaseModel):
    variables: str


class TweetDetail(BaseRequestModel):
    features: str = quote(
        json.dumps(
            {
                "rweb_tipjar_consumption_enabled": False,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "communities_web_enable_tweet_community_results_fetch": True,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "creator_subscriptions_quote_tweet_preview_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_enhance_cards_enabled": False,
            }
        )
    )
    fieldToggles: str = quote(
        json.dumps({"withArticleRichContentState": True, "withArticlePlainText": False})
    )


class TweetDetailEncode(BaseModel):
    focalTweetId: str
    cursor: str = ""
    referrer: str = "tweet"
    with_rux_injections: bool = True
    includePromotedContent: bool = True
    withCommunity: bool = True
    withQuickPromoteEligibilityTweetFields: bool = True
    withBirdwatchNotes: bool = True
    withVoice: bool = True
    withV2Timeline: bool = True


class UserProfile(BaseRequestModel):
    features: str = quote(
        json.dumps(
            {
                "hidden_profile_likes_enabled": True,
                "hidden_profile_subscriptions_enabled": True,
                "rweb_tipjar_consumption_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": True,
                "subscriptions_verification_info_is_identity_verified_enabled": True,
                "subscriptions_verification_info_verified_since_enabled": True,
                "highlights_tweets_tab_ui_enabled": True,
                "responsive_web_twitter_article_notes_tab_enabled": True,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True,
            }
        )
    )
    fieldToggles: str = quote(json.dumps({"withAuxiliaryUserLabels": False}))


class UserProfileEncode(BaseModel):
    # uniqueId: asai_chan_
    screen_name: str
    withSafetyModeUserFields: bool = True


class PostTweet(BaseRequestModel):
    features: str = quote(
        json.dumps(
            {
                "rweb_tipjar_consumption_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "communities_web_enable_tweet_community_results_fetch": True,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "articles_preview_enabled": False,
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "creator_subscriptions_quote_tweet_preview_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "tweet_with_visibility_results_prefer_gql_media_interstitial_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_enhance_cards_enabled": False,
            }
        )
    )

    fieldToggles: str = quote(json.dumps({"withArticlePlainText": False}))


class PostTweetEncode(BaseModel):
    userId: str
    count: int
    cursor: str = ""
    includePromotedContent: bool = True
    withQuickPromoteEligibilityTweetFields: bool = True
    withVoice: bool = True
    withV2Timeline: bool = True

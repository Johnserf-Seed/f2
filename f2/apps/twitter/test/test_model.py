from f2.apps.twitter.model import encode_model, TweetDetail, TweetDetailEncode

if __name__ == "__main__":

    # tweet_detail_encode = quote(
    #     TweetDetailEncode(focalTweetId="1777291676568166526").model_dump_json()
    # )
    # tweet_detail = TweetDetail(variables=tweet_detail_encode)
    # print(tweet_detail.model_dump())

    encoded_data = encode_model(TweetDetailEncode(focalTweetId="1777291676568166526"))
    tweet_detail = TweetDetail(variables=encoded_data)
    print(tweet_detail.model_dump())

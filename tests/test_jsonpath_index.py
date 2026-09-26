# path: tests/test_jsonpath_index.py

from f2.apps.twitter.filter import BookmarkTweetFilter, PostTweetFilter
from f2.utils.json.filter import JSONModel


def test_out_of_range_negative_index_is_missing():
    # jsonpath_ng 在只有 1 项时取 [-2] 会抛出 IndexError
    model = JSONModel({"a": [1], "b": []})
    assert model._get_attr_value("$.a[-2]") is None
    assert model._get_attr_value("$.a[-1]") == 1
    assert model._get_attr_value("$.b[-2]") is None


def test_list_values_are_padded_for_short_lists():
    model = JSONModel({"items": [{"tags": ["x", "y"]}, {"tags": ["z"]}, {}]})
    assert model._get_list_attr_value("$.items[*].tags[-2]") == ["x", None, None]


def timeline(entries):
    return {"timeline": {"instructions": [{"entries": entries}]}}


ONLY_CURSOR = [{"content": {"value": "cursor-bottom", "cursorType": "Bottom"}}]


def test_bookmark_page_with_one_entry():
    # 此前 _to_list、_to_dict 都会因为 min_cursor 抛出 IndexError，书签下载直接中断
    data = {"data": {"bookmark_timeline_v2": timeline(ONLY_CURSOR)}}
    tweets = BookmarkTweetFilter(data)
    assert tweets.min_cursor is None
    assert tweets.max_cursor == "cursor-bottom"
    # 每个条目对应一条记录，游标条目的推文字段为空，由下载器跳过
    [entry] = tweets._to_list()
    assert entry["min_cursor"] is None
    assert entry["max_cursor"] == "cursor-bottom"
    assert tweets._to_dict()["min_cursor"] is None


def test_post_page_with_one_entry():
    data = {"data": {"user": {"result": {"timeline_v2": timeline(ONLY_CURSOR)}}}}
    tweets = PostTweetFilter(data)
    assert tweets.min_cursor is None
    assert tweets.max_cursor == "cursor-bottom"
    assert len(tweets._to_list()) == 1

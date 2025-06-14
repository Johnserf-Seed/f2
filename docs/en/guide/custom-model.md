---
outline: deep
---

# Extend Default Data Models

This page shows how to extend the default `Filter` classes and data models in `F2` so you can customize parsed results when calling the API.

## Why Customize

The built-in `Filter` only extracts commonly used fields. If the API response does not fit your needs, you can inherit from `JSONModel` to parse additional fields.

## Create a Custom Filter

<<< @/snippets/custom-filter.py#custom-filter-snippet

The example above demonstrates how to subclass `JSONModel`, implement properties and a `_to_dict` method, then pass the response to your filter for parsing.

## Use in Your Code

The API response does not need to change. After you get the raw data, instantiate your custom filter:

```python
async with DouyinCrawler(kwargs) as crawler:
    params = UserProfile(sec_user_id="YOUR_SEC_UID")
    response = await crawler.fetch_user_profile(params)
    user = SimpleUserFilter(response)
    print(user._to_dict())
```

With this approach you can flexibly extend the default model or build a completely new one for your desired data.

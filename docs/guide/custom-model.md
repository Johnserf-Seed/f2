---
outline: deep
---

# 扩展默认数据模型

本文介绍如何扩展 `F2` 默认提供的 `Filter` 过滤器和数据模型，以便在调用接口时自定义解析结果。

## 为什么要自定义

默认的 `Filter` 仅抽取了常用字段。当接口返回的数据与业务需求不完全一致时，你可以通过继承 `JSONModel` 创建自己的过滤器来解析额外字段。

## 创建自定义 Filter

<<< @/snippets/custom-filter.py#custom-filter-snippet

上面的示例展示了如何继承 `JSONModel` 并实现属性及 `_to_dict` 方法，然后在爬虫获取到接口响应后将其传入自定义的 `Filter` 中解析。

## 在接口中使用

接口返回的原始数据无需修改，只需要在获取到响应后构造自定义 `Filter` 即可：

```python
async with DouyinCrawler(kwargs) as crawler:
    params = UserProfile(sec_user_id="YOUR_SEC_UID")
    response = await crawler.fetch_user_profile(params)
    user = SimpleUserFilter(response)
    print(user._to_dict())
```

通过这种方式，你可以灵活地扩展默认模型或完全构建新的数据模型，实现更符合需求的解析结果。

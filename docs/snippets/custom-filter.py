# region custom-filter-snippet
import asyncio

from f2.apps.douyin.crawler import DouyinCrawler
from f2.apps.douyin.model import UserProfile
from f2.utils.json.filter import JSONModel


class SimpleUserFilter(JSONModel):
    @property
    def nickname(self):
        return self._get_attr_value("$.user.nickname")

    def _to_dict(self):
        return {"nickname": self.nickname}


async def main():
    async with DouyinCrawler({}) as crawler:
        params = UserProfile(sec_user_id="YOUR_SEC_UID")
        response = await crawler.fetch_user_profile(params)
        user = SimpleUserFilter(response)
        print(user._to_dict())


if __name__ == "__main__":
    asyncio.run(main())
# endregion custom-filter-snippet

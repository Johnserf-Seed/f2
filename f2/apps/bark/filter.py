# path: f2/apps/bark/filter.py

from typing import Dict
from f2.utils.json_filter import JSONModel
from f2.utils.utils import timestamp_2_str


class BarkNotificationFilter(JSONModel):
    @property
    def code(self):
        return self._get_attr_value("$.code")

    @property
    def message(self):
        return self._get_attr_value("$.message")

    @property
    def timestamp(self):
        return timestamp_2_str(str(self._get_attr_value("$.timestamp")))

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from domain.date_range import DateRangeJST
from domain.models import NewsItem
from usecases.fetch_and_filter import FetchAndFilterUseCase

JST = ZoneInfo("Asia/Tokyo")


class FakeRssGateway:
    def __init__(self, items: list[NewsItem]):
        self._items = items
        self.fetch_called = 0

    def fetch_all(self) -> list[NewsItem]:
        self.fetch_called += 1
        return list(self._items)


def _item(day: int, hour: int, title: str = "t") -> NewsItem:
    return NewsItem(
        title=title,
        link=f"https://news.nullevi.app/{day}-{hour}",
        guid=f"https://news.nullevi.app/{day}-{hour}",
        pub_date_jst=datetime(2026, 5, day, hour, 0, 0, tzinfo=JST),
        description=f"body {day}-{hour}",
        categories=("AI",),
    )


def _range_for_5_11() -> DateRangeJST:
    return DateRangeJST.from_yesterday(datetime(2026, 5, 12, 0, 10, 0, tzinfo=JST))


def test_keeps_only_yesterday_items():
    items = [
        _item(10, 12, "Day before yesterday"),
        _item(11, 0, "Yesterday morning"),
        _item(11, 23, "Yesterday night"),
        _item(12, 0, "Today"),
        _item(12, 10, "After execution time"),
    ]
    gw = FakeRssGateway(items)
    uc = FetchAndFilterUseCase(rss_gateway=gw)

    result = uc.execute(date_range=_range_for_5_11())

    titles = [i.title for i in result]
    assert titles == ["Yesterday night", "Yesterday morning"]  # 降順


def test_zero_items_when_no_match():
    gw = FakeRssGateway([_item(12, 12, "Today")])
    uc = FetchAndFilterUseCase(rss_gateway=gw)
    assert uc.execute(date_range=_range_for_5_11()) == []


def test_calls_rss_gateway_once():
    gw = FakeRssGateway([])
    uc = FetchAndFilterUseCase(rss_gateway=gw)
    uc.execute(date_range=_range_for_5_11())
    assert gw.fetch_called == 1


def test_sorts_descending_by_pub_date():
    items = [
        _item(11, 5, "early"),
        _item(11, 20, "late"),
        _item(11, 12, "noon"),
    ]
    gw = FakeRssGateway(items)
    uc = FetchAndFilterUseCase(rss_gateway=gw)
    result = uc.execute(date_range=_range_for_5_11())
    assert [i.title for i in result] == ["late", "noon", "early"]

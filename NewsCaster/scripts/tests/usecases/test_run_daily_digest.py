from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from domain.models import NewsItem
from usecases.run_daily_digest import RunDailyDigestUseCase, RunResult

JST = ZoneInfo("Asia/Tokyo")


class FakeRssGateway:
    def __init__(self, items):
        self._items = items

    def fetch_all(self):
        return list(self._items)


class FakeMailGateway:
    def __init__(self):
        self.sent = []

    def send(self, **kwargs):
        self.sent.append(kwargs)


def _item(day: int, hour: int, title: str = "t") -> NewsItem:
    return NewsItem(
        title=title,
        link=f"https://news.nullevi.app/{day}-{hour}",
        guid=f"https://news.nullevi.app/{day}-{hour}",
        pub_date_jst=datetime(2026, 5, day, hour, 0, 0, tzinfo=JST),
        description="body",
        categories=("AI",),
    )


def _build_uc(rss_items):
    rss = FakeRssGateway(rss_items)
    mail = FakeMailGateway()
    uc = RunDailyDigestUseCase(
        rss_gateway=rss,
        mail_gateway=mail,
        sender="from@example.com",
        recipient="to@example.com",
    )
    return uc, mail


def test_full_flow_sends_email_when_yesterday_has_items():
    uc, mail = _build_uc([_item(11, 12, "yesterday")])
    result = uc.execute(now=datetime(2026, 5, 12, 0, 10, 0, tzinfo=JST))
    assert result.result == RunResult.SENT
    assert len(mail.sent) == 1


def test_skips_email_when_zero_items_yesterday():
    uc, mail = _build_uc([_item(12, 12, "today")])
    result = uc.execute(now=datetime(2026, 5, 12, 0, 10, 0, tzinfo=JST))
    assert result.result == RunResult.NO_ITEMS
    assert mail.sent == []


def test_sends_again_when_run_twice_for_same_target_date():
    uc, mail = _build_uc([_item(11, 12, "y")])
    first = uc.execute(now=datetime(2026, 5, 12, 0, 10, 0, tzinfo=JST))
    second = uc.execute(now=datetime(2026, 5, 12, 0, 10, 0, tzinfo=JST))
    assert first.result == RunResult.SENT
    assert second.result == RunResult.SENT
    assert len(mail.sent) == 2


def test_target_date_override_via_now():
    # 2026-05-13 0:10 で実行すると 5/12 が前日
    uc, mail = _build_uc([_item(12, 12, "in_range"), _item(11, 12, "out")])
    result = uc.execute(now=datetime(2026, 5, 13, 0, 10, 0, tzinfo=JST))
    assert result.result == RunResult.SENT
    assert len(mail.sent) == 1


def test_dry_run_skips_send():
    uc, mail = _build_uc([_item(11, 12, "y")])
    result = uc.execute(
        now=datetime(2026, 5, 12, 0, 10, 0, tzinfo=JST), dry_run=True
    )
    assert result.result == RunResult.DRY_RUN
    assert result.digest is not None
    assert mail.sent == []

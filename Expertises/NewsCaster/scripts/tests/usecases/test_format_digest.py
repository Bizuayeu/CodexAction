from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from domain.models import NewsItem
from usecases.format_digest import FormatDigestUseCase

JST = ZoneInfo("Asia/Tokyo")


def _item(hour: int, title: str, desc: str = "本文", cats: tuple = ("AI",)) -> NewsItem:
    return NewsItem(
        title=title,
        link=f"https://news.nullevi.app/{hour}",
        guid=f"https://news.nullevi.app/{hour}",
        pub_date_jst=datetime(2026, 5, 11, hour, 0, 0, tzinfo=JST),
        description=desc,
        categories=cats,
    )


def test_subject_contains_date_and_count():
    uc = FormatDigestUseCase()
    digest = uc.execute(
        target_date="2026-05-11",
        items=[_item(10, "A"), _item(12, "B")],
    )
    assert "2026-05-11" in digest.formatted_subject
    assert "2件" in digest.formatted_subject
    assert "ナルエビ" in digest.formatted_subject


def test_body_contains_each_item_title_and_link():
    uc = FormatDigestUseCase()
    digest = uc.execute(
        target_date="2026-05-11",
        items=[_item(10, "TitleAlpha", "Body alpha"), _item(12, "TitleBeta", "Body beta")],
    )
    assert "TitleAlpha" in digest.formatted_body
    assert "TitleBeta" in digest.formatted_body
    assert "https://news.nullevi.app/10" in digest.formatted_body
    assert "https://news.nullevi.app/12" in digest.formatted_body
    assert "Body alpha" in digest.formatted_body
    assert "Body beta" in digest.formatted_body


def test_body_includes_jst_pubdate_and_categories():
    uc = FormatDigestUseCase()
    digest = uc.execute(
        target_date="2026-05-11",
        items=[_item(15, "T", cats=("Cat1", "Cat2", "Cat3"))],
    )
    assert "15:00" in digest.formatted_body
    assert "Cat1" in digest.formatted_body
    assert "Cat2" in digest.formatted_body
    assert "Cat3" in digest.formatted_body


def test_zero_items_produces_silent_digest():
    uc = FormatDigestUseCase()
    digest = uc.execute(target_date="2026-05-11", items=[])
    assert digest.is_empty is True
    assert digest.target_date == "2026-05-11"
    # subject/body は空でない（DailyDigest が validation で要求するので "0件" の通知用文字列）
    assert digest.formatted_subject
    assert digest.formatted_body


def test_target_date_propagated():
    uc = FormatDigestUseCase()
    digest = uc.execute(target_date="2026-05-11", items=[_item(10, "A")])
    assert digest.target_date == "2026-05-11"


def test_items_tuple_preserved_order():
    uc = FormatDigestUseCase()
    a = _item(12, "first")
    b = _item(10, "second")
    digest = uc.execute(target_date="2026-05-11", items=[a, b])
    assert digest.items == (a, b)

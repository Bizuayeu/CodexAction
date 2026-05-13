from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from domain.digest import DailyDigest
from domain.models import NewsItem
from usecases.send_digest_email import SendDigestEmailUseCase

JST = ZoneInfo("Asia/Tokyo")


class FakeMailGateway:
    def __init__(self):
        self.sent: list[tuple[str, str, str, str]] = []

    def send(self, *, sender: str, to: str, subject: str, body: str) -> None:
        self.sent.append((sender, to, subject, body))


def _digest(target_date: str = "2026-05-11", with_item: bool = True) -> DailyDigest:
    items = (
        (
            NewsItem(
                title="t",
                link="https://x.example/",
                guid="g",
                pub_date_jst=datetime(2026, 5, 11, 12, 0, 0, tzinfo=JST),
                description="b",
                categories=(),
            ),
        )
        if with_item
        else ()
    )
    return DailyDigest(
        target_date=target_date,
        items=items,
        formatted_subject="件名",
        formatted_body="本文",
    )


def test_sends_email():
    mail = FakeMailGateway()
    uc = SendDigestEmailUseCase(
        mail_gateway=mail,
        sender="from@example.com",
        recipient="to@example.com",
    )

    uc.execute(digest=_digest())

    assert len(mail.sent) == 1
    sender, to, subject, body = mail.sent[0]
    assert sender == "from@example.com"
    assert to == "to@example.com"
    assert subject == "件名"
    assert body == "本文"


def test_sends_again_when_called_again_for_same_digest():
    mail = FakeMailGateway()
    uc = SendDigestEmailUseCase(
        mail_gateway=mail,
        sender="from@example.com",
        recipient="to@example.com",
    )

    uc.execute(digest=_digest())
    uc.execute(digest=_digest())

    assert len(mail.sent) == 2


def test_propagates_mail_failure():
    class FailingMail:
        def send(self, **_):
            raise RuntimeError("smtp down")

    uc = SendDigestEmailUseCase(
        mail_gateway=FailingMail(),
        sender="from@example.com",
        recipient="to@example.com",
    )

    with pytest.raises(RuntimeError):
        uc.execute(digest=_digest())

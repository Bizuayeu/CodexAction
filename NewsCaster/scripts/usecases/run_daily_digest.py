from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from domain.date_range import DateRangeJST
from domain.digest import DailyDigest
from usecases.fetch_and_filter import FetchAndFilterUseCase
from usecases.format_digest import FormatDigestUseCase
from usecases.ports import MailGatewayPort, RssGatewayPort
from usecases.send_digest_email import SendDigestEmailUseCase


class RunResult(str, Enum):
    SENT = "sent"
    NO_ITEMS = "no_items"
    DRY_RUN = "dry_run"


@dataclass(frozen=True)
class RunOutcome:
    result: RunResult
    target_date: str
    digest: DailyDigest | None = None


class RunDailyDigestUseCase:
    def __init__(
        self,
        *,
        rss_gateway: RssGatewayPort,
        mail_gateway: MailGatewayPort,
        sender: str,
        recipient: str,
    ) -> None:
        self._fetch_filter = FetchAndFilterUseCase(rss_gateway=rss_gateway)
        self._format = FormatDigestUseCase()
        self._send = SendDigestEmailUseCase(
            mail_gateway=mail_gateway,
            sender=sender,
            recipient=recipient,
        )

    def execute(
        self, *, now: datetime, dry_run: bool = False
    ) -> RunOutcome:
        date_range = DateRangeJST.from_yesterday(now)
        target_date = date_range.target_date_iso()

        items = self._fetch_filter.execute(date_range=date_range)
        if not items:
            return RunOutcome(RunResult.NO_ITEMS, target_date)

        digest = self._format.execute(target_date=target_date, items=items)

        if dry_run:
            return RunOutcome(RunResult.DRY_RUN, target_date, digest=digest)

        self._send.execute(digest=digest)
        return RunOutcome(RunResult.SENT, target_date, digest=digest)

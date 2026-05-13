from __future__ import annotations

from domain.digest import DailyDigest
from usecases.ports import MailGatewayPort


class SendDigestEmailUseCase:
    def __init__(
        self,
        *,
        mail_gateway: MailGatewayPort,
        sender: str,
        recipient: str,
    ) -> None:
        self._mail = mail_gateway
        self._sender = sender
        self._recipient = recipient

    def execute(self, *, digest: DailyDigest) -> None:
        self._mail.send(
            sender=self._sender,
            to=self._recipient,
            subject=digest.formatted_subject,
            body=digest.formatted_body,
        )

from __future__ import annotations

import base64
import os
import time
from pathlib import Path
from typing import Any

from google.auth.transport.requests import AuthorizedSession

from adapters.mail.mime_builder import build_mime
from domain.exceptions import AuthError, MailSendError
from infrastructure.google_oauth_provider import load_credentials

RETRYABLE_STATUS = {429, 500, 502, 503, 504}
AUTH_FAILURE_STATUS = {401, 403}


GMAIL_SEND_ENDPOINT = (
    "https://gmail.googleapis.com/gmail/v1/users/{user_id}/messages/send"
)


def build_service(creds: Any) -> Any:
    return GmailRestService(AuthorizedSession(creds))


class GmailRestService:
    def __init__(self, session: AuthorizedSession) -> None:
        self._session = session

    def users(self) -> "GmailRestService":
        return self

    def messages(self) -> "GmailRestService":
        return self

    def send(self, *, userId: str, body: dict[str, str]) -> "GmailRestRequest":
        return GmailRestRequest(session=self._session, user_id=userId, body=body)


class GmailRestRequest:
    def __init__(
        self, *, session: AuthorizedSession, user_id: str, body: dict[str, str]
    ) -> None:
        self._session = session
        self._user_id = user_id
        self._body = body

    def execute(self) -> dict[str, Any]:
        response = self._session.post(
            GMAIL_SEND_ENDPOINT.format(user_id=self._user_id),
            json=self._body,
            timeout=60,
        )
        if response.status_code >= 400:
            raise GmailRestError(response)
        if not response.content:
            return {}
        return response.json()


class GmailRestError(Exception):
    def __init__(self, response: Any) -> None:
        self.response = response
        self.status_code = response.status_code
        self.resp = type("ResponseStatus", (), {"status": response.status_code})()
        super().__init__(_format_response_error(response))


def _format_response_error(response: Any) -> str:
    try:
        detail = response.json()
    except ValueError:
        detail = response.text
    return f"Gmail API HTTP {response.status_code}: {detail}"


class GmailApiMailGateway:
    def __init__(
        self,
        *,
        oauth_token_path: Path | None,
        oauth_token_json: str | None,
        retry_count: int = 3,
    ) -> None:
        self._token_path = oauth_token_path
        self._token_json = oauth_token_json
        self._retry_count = max(1, retry_count)
        linux_ca = "/etc/ssl/certs/ca-certificates.crt"
        if os.environ.get("HTTPLIB2_CA_CERTS") is None and os.path.exists(linux_ca):
            os.environ["HTTPLIB2_CA_CERTS"] = linux_ca

    def send(self, *, sender: str, to: str, subject: str, body: str) -> None:
        if not sender or not to or not subject or not body:
            raise MailSendError("sender/to/subject/body are all required")

        mime = build_mime(sender=sender, to=to, subject=subject, body=body)
        raw = base64.urlsafe_b64encode(mime.as_bytes()).decode("ascii")
        request_body = {"raw": raw}

        creds = load_credentials(
            token_path=self._token_path, token_json=self._token_json
        )
        service = build_service(creds)

        last: Exception | None = None
        for attempt in range(self._retry_count):
            try:
                service.users().messages().send(
                    userId="me", body=request_body
                ).execute()
                return
            except Exception as e:
                status = _extract_status(e)
                if status in AUTH_FAILURE_STATUS:
                    raise AuthError(
                        f"Gmail API authentication failed (status={status}): {e}"
                    ) from e
                if status in RETRYABLE_STATUS:
                    last = e
                    if attempt < self._retry_count - 1:
                        time.sleep(2**attempt)
                        continue
                    break
                raise MailSendError(
                    f"Gmail API send failed (status={status}): {e}"
                ) from e

        raise MailSendError(
            f"Gmail API send failed after {self._retry_count} retries: {last}"
        )


def _extract_status(exc: Exception) -> int | None:
    resp = getattr(exc, "resp", None)
    if resp is not None:
        status = getattr(resp, "status", None)
        if status is not None:
            try:
                return int(status)
            except (TypeError, ValueError):
                return None
    status_code = getattr(exc, "status_code", None)
    if status_code is not None:
        try:
            return int(status_code)
        except (TypeError, ValueError):
            return None
    return None

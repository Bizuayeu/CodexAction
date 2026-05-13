from __future__ import annotations

from typing import Protocol, runtime_checkable

from domain.models import NewsItem


@runtime_checkable
class RssGatewayPort(Protocol):
    def fetch_all(self) -> list[NewsItem]:
        """RSSフィードを取得し全itemをパースして返す。

        ネットワーク・パース失敗時は RssFetchError を raise。
        """
        ...


@runtime_checkable
class MailGatewayPort(Protocol):
    def send(self, *, sender: str, to: str, subject: str, body: str) -> None:
        """メールを送信する。失敗時は MailSendError / AuthError を raise。"""
        ...

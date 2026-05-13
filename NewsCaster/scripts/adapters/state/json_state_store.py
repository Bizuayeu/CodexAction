from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any


class JsonStateStore:
    def __init__(self, *, state_dir: Path) -> None:
        self._state_dir = state_dir
        self._state_file = state_dir / "sent_dates.json"

    def is_sent(self, target_date: str) -> bool:
        return target_date in self._read_sent_dates()

    def mark_sent(self, target_date: str) -> None:
        sent = set(self._read_sent_dates())
        sent.add(target_date)
        sent = self._prune(sent, target_date)
        self._write_sent_dates(sorted(sent))

    def _read_sent_dates(self) -> list[str]:
        try:
            raw = json.loads(self._state_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        sent = raw.get("sent") if isinstance(raw, dict) else None
        if not isinstance(sent, list):
            return []
        return [value for value in sent if isinstance(value, str)]

    def _write_sent_dates(self, sent: list[str]) -> None:
        self._state_dir.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {"sent": sent}
        self._state_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _prune(sent: set[str], target_date: str) -> set[str]:
        try:
            cutoff = date.fromisoformat(target_date) - timedelta(days=90)
        except ValueError:
            return sent

        kept: set[str] = set()
        for value in sent:
            try:
                if date.fromisoformat(value) >= cutoff:
                    kept.add(value)
            except ValueError:
                kept.add(value)
        return kept

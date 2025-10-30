"""JSON-backed store tracking recent submission attempts per dealer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional


DEFAULT_HISTORY_PATH = Path("data/submission_history.json")
DEFAULT_COOLDOWN_HOURS = 12


@dataclass
class SubmissionRecord:
    slug: str
    last_status: str
    last_attempt: datetime

    def to_dict(self) -> Dict[str, str]:
        return {
            "slug": self.slug,
            "last_status": self.last_status,
            "last_attempt": self.last_attempt.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, str]) -> "SubmissionRecord":
        return cls(
            slug=payload.get("slug", ""),
            last_status=payload.get("last_status", ""),
            last_attempt=datetime.fromisoformat(payload.get("last_attempt", datetime.now(timezone.utc).isoformat())),
        )


class SubmissionHistory:
    def __init__(
        self,
        path: Path = DEFAULT_HISTORY_PATH,
        cooldown_hours: int = DEFAULT_COOLDOWN_HOURS,
    ) -> None:
        self.path = path
        self.cooldown = timedelta(hours=cooldown_hours)
        self.records: Dict[str, SubmissionRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return
        for entry in payload:
            record = SubmissionRecord.from_dict(entry)
            self.records[record.slug] = record

    def save(self) -> None:
        serialised = [record.to_dict() for record in self.records.values()]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(serialised, indent=2, sort_keys=True), encoding="utf-8")

    def should_skip(self, slug: str, now: Optional[datetime] = None) -> bool:
        record = self.records.get(slug)
        if not record:
            return False
        now = now or datetime.now(timezone.utc)
        return now - record.last_attempt < self.cooldown

    def record(self, slug: str, status: str, now: Optional[datetime] = None) -> None:
        now = now or datetime.now(timezone.utc)
        self.records[slug] = SubmissionRecord(slug=slug, last_status=status, last_attempt=now)
        self.save()

    def clear(self, slug: str) -> None:
        if slug in self.records:
            del self.records[slug]
            self.save()

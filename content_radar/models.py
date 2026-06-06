"""Immutable domain model for a collected signal.

An `Item` is one piece of trend signal from any source (a Hacker News story, an
arXiv paper, a trending repo, a Reddit thread, a tweet). State is never mutated;
helpers return new objects.
"""
from __future__ import annotations

import email.utils
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

_RFC2822_LIKE = re.compile(r"^[A-Za-z]{3},\s")


def normalize_datetime(raw: str) -> str:
    """Best-effort normalise a date(time) string to ISO-8601.

    Handles RFC 2822 (email Date headers) and passes through ISO strings unchanged.
    Returns the original string when parsing fails so no data is lost.
    """
    if not raw:
        return raw
    if _RFC2822_LIKE.match(raw):
        parsed = email.utils.parsedate_to_datetime(raw)
        return parsed.astimezone(timezone.utc).isoformat()
    return raw


@dataclass(frozen=True)
class Item:
    source: str          # hackernews | arxiv | github | reddit | x
    id: str              # stable id within the source
    title: str
    url: str
    text: str = ""       # abstract / selftext / tweet body / summary
    score: int = 0       # points / upvotes / stars / likes
    author: str = ""
    created: str = ""     # ISO-8601 date or datetime string
    first_seen: str = ""  # ISO date when our system first collected this item
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        """Globally unique dedup key."""
        return f"{self.source}:{self.id}"

    def to_dict(self) -> dict:
        d = {
            "source": self.source,
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "text": self.text,
            "score": self.score,
            "author": self.author,
            "created": self.created,
            "extra": dict(self.extra),
        }
        if self.first_seen:
            d["first_seen"] = self.first_seen
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        return cls(
            source=data["source"],
            id=str(data["id"]),
            title=data.get("title", ""),
            url=data.get("url", ""),
            text=data.get("text", ""),
            score=int(data.get("score", 0)),
            author=data.get("author", ""),
            created=data.get("created", ""),
            first_seen=data.get("first_seen", ""),
            extra=dict(data.get("extra", {})),
        )

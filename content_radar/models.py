"""Immutable domain model for a collected signal.

An `Item` is one piece of trend signal from any source (a Hacker News story, an
arXiv paper, a trending repo, a Reddit thread, a tweet). State is never mutated;
helpers return new objects.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        """Globally unique dedup key."""
        return f"{self.source}:{self.id}"

    def to_dict(self) -> dict:
        return {
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
            extra=dict(data.get("extra", {})),
        )

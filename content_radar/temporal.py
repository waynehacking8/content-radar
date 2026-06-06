"""Temporal query analysis for date-aware retrieval.

Classifies user queries into temporal intent tiers so the retrieval pipeline
can apply appropriate date filtering or recency weighting. Inspired by
Perplexity's query-intent routing to trending vs. evergreen indexes.

Three tiers:
  EXPLICIT — hard date filter ("today", "昨天", "this week")
  IMPLICIT — soft recency boost ("latest", "最新", "recent trends")
  NONE     — pure semantic search ("explain transformer architecture")
"""
from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass
from enum import Enum


class TemporalTier(Enum):
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    NONE = "none"


@dataclass(frozen=True)
class TemporalIntent:
    tier: TemporalTier
    date_from: _dt.datetime | None = None
    date_to: _dt.datetime | None = None


_EXPLICIT_PATTERNS: dict[str, tuple[int, int]] = {
    "today": (0, 0),
    "today's": (0, 0),
    "今天": (0, 0),
    "今日": (0, 0),
    "yesterday": (1, 1),
    "昨天": (1, 1),
    "昨日": (1, 1),
    "this week": (7, 0),
    "這週": (7, 0),
    "這禮拜": (7, 0),
    "本週": (7, 0),
    "this month": (30, 0),
    "本月": (30, 0),
    "這個月": (30, 0),
}

_IMPLICIT_KEYWORDS: set[str] = {
    "latest", "recent", "new", "breaking", "just", "current",
    "最新", "最近", "近期", "剛剛", "新的", "目前",
}

_QUERY_NORM_RE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _QUERY_NORM_RE.sub(" ", text.strip().lower())


def detect_temporal_intent(
    query: str,
    *,
    now: _dt.datetime | None = None,
) -> TemporalIntent:
    now = now or _dt.datetime.now(_dt.timezone.utc)
    normed = _normalize(query)

    for pattern, (start_offset, end_offset) in _EXPLICIT_PATTERNS.items():
        if pattern in normed:
            start = (now - _dt.timedelta(days=start_offset)).replace(
                hour=0, minute=0, second=0, microsecond=0,
            )
            if end_offset > 0:
                end = (now - _dt.timedelta(days=end_offset)).replace(
                    hour=23, minute=59, second=59, microsecond=999999,
                )
            else:
                end = now
            return TemporalIntent(
                tier=TemporalTier.EXPLICIT,
                date_from=start,
                date_to=end,
            )

    if any(kw in normed for kw in _IMPLICIT_KEYWORDS):
        start = (now - _dt.timedelta(days=3)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        return TemporalIntent(
            tier=TemporalTier.IMPLICIT,
            date_from=start,
            date_to=now,
        )

    return TemporalIntent(tier=TemporalTier.NONE)

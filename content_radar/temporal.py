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


_EXPLICIT_PATTERNS: dict[str, int] = {
    "today": 0,
    "today's": 0,
    "今天": 0,
    "今日": 0,
    "yesterday": 1,
    "昨天": 1,
    "昨日": 1,
    "this week": 7,
    "這週": 7,
    "這禮拜": 7,
    "本週": 7,
    "this month": 30,
    "本月": 30,
    "這個月": 30,
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

    for pattern, lookback_days in _EXPLICIT_PATTERNS.items():
        if pattern in normed:
            start = (now - _dt.timedelta(days=lookback_days)).replace(
                hour=0, minute=0, second=0, microsecond=0,
            )
            return TemporalIntent(
                tier=TemporalTier.EXPLICIT,
                date_from=start,
                date_to=now,
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

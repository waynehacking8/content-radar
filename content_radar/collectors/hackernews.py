"""Hacker News collector via the free Algolia API (no key required)."""
from __future__ import annotations

from ..config import Interests
from ..models import Item
from .base import get, warn

SEARCH = "https://hn.algolia.com/api/v1/search"
SOURCE = "hackernews"


def collect(interests: Interests) -> list[Item]:
    floor = interests.min_score.get(SOURCE, 0)
    seen: dict[str, Item] = {}
    for kw in interests.keywords:
        try:
            resp = get(SEARCH, params={
                "query": kw,
                "tags": "story",
                "numericFilters": f"points>={floor}",
                "hitsPerPage": 15,
            })
            resp.raise_for_status()
            for hit in resp.json().get("hits", []):
                oid = str(hit.get("objectID"))
                if not oid or oid in seen:
                    continue
                seen[oid] = Item(
                    source=SOURCE,
                    id=oid,
                    title=hit.get("title") or hit.get("story_title") or "",
                    url=hit.get("url") or f"https://news.ycombinator.com/item?id={oid}",
                    text=(hit.get("story_text") or "")[:1000],
                    score=int(hit.get("points") or 0),
                    author=hit.get("author") or "",
                    created=hit.get("created_at") or "",
                    extra={"comments": hit.get("num_comments") or 0, "matched": kw},
                )
        except Exception as exc:  # noqa: BLE001 - collectors must not raise
            warn(SOURCE, exc)
    return list(seen.values())

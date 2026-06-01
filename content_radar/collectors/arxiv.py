"""arXiv collector via the free export API (Atom feed, no key required)."""
from __future__ import annotations

import time

import feedparser

from ..config import Interests
from ..models import Item
from .base import get, warn

API = "http://export.arxiv.org/api/query"
SOURCE = "arxiv"
# arXiv asks clients to throttle; it returns 429 on bursts from shared IPs.
RETRIES = 3
BACKOFF_SECONDS = 3


def collect(interests: Interests) -> list[Item]:
    cats = " OR ".join(f"cat:{c}" for c in interests.arxiv_categories)
    params = {
        "search_query": cats,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": 30,
    }
    resp = None
    for attempt in range(RETRIES):
        try:
            resp = get(API, params=params)
            if resp.status_code == 429:
                time.sleep(BACKOFF_SECONDS * (attempt + 1))
                continue
            resp.raise_for_status()
            break
        except Exception as exc:  # noqa: BLE001
            if attempt == RETRIES - 1:
                warn(SOURCE, exc)
                return []
            time.sleep(BACKOFF_SECONDS)
    if resp is None or resp.status_code != 200:
        warn(SOURCE, RuntimeError(f"arxiv unavailable after {RETRIES} tries"))
        return []

    feed = feedparser.parse(resp.text)
    items: list[Item] = []
    for entry in feed.entries:
        arxiv_id = entry.get("id", "").rsplit("/", 1)[-1]
        if not arxiv_id:
            continue
        items.append(Item(
            source=SOURCE,
            id=arxiv_id,
            title=entry.get("title", "").replace("\n", " ").strip(),
            url=entry.get("link", ""),
            text=entry.get("summary", "").replace("\n", " ").strip()[:1200],
            score=0,  # arXiv has no score; relevance handled at synthesis
            author=", ".join(a.get("name", "") for a in entry.get("authors", []))[:200],
            created=entry.get("published", ""),
            extra={"categories": [t.get("term") for t in entry.get("tags", [])]},
        ))
    return items

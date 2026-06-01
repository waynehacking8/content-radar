"""X / Twitter collector via twitterapi.io (third-party, pay-as-you-go).

Chosen over the official API ($0.005/read) and over self-scraping (fragile +
account-ban risk). twitterapi.io is ~$0.15 / 1,000 tweets, no monthly fee, and
runs the scraping infrastructure for you. Disabled unless TWITTERAPI_IO_KEY is set.

Docs: https://twitterapi.io
"""
from __future__ import annotations

from ..config import Interests, twitterapi_io_key
from ..models import Item
from .base import warn
import requests

BASE = "https://api.twitterapi.io"
ADVANCED_SEARCH = f"{BASE}/twitter/tweet/advanced_search"
SOURCE = "x"
TIMEOUT = 20


def _search(query: str, api_key: str) -> list[dict]:
    resp = requests.get(
        ADVANCED_SEARCH,
        params={"query": query, "queryType": "Latest"},
        headers={"X-API-Key": api_key},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()
    # twitterapi.io returns {"tweets": [...]} (key tolerated defensively).
    return payload.get("tweets") or payload.get("data") or []


def collect(interests: Interests) -> list[Item]:
    api_key = twitterapi_io_key()
    if not api_key:
        return []  # silently disabled until a key is configured
    floor = interests.min_score.get(SOURCE, 0)
    seen: dict[str, Item] = {}
    for query in interests.x_queries:
        try:
            for tw in _search(query, api_key):
                tid = str(tw.get("id") or tw.get("id_str") or "")
                if not tid or tid in seen:
                    continue
                likes = int(tw.get("likeCount") or tw.get("favorite_count") or 0)
                if likes < floor:
                    continue
                author = (tw.get("author") or {}).get("userName") or tw.get("username") or ""
                seen[tid] = Item(
                    source=SOURCE,
                    id=tid,
                    title=(tw.get("text") or "")[:120],
                    url=tw.get("url") or f"https://x.com/i/web/status/{tid}",
                    text=tw.get("text") or "",
                    score=likes,
                    author=author,
                    created=tw.get("createdAt") or "",
                    extra={"retweets": tw.get("retweetCount") or 0, "matched": query},
                )
        except requests.RequestException as exc:
            warn(SOURCE, exc)
    return list(seen.values())

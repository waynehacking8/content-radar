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
USER_LAST_TWEETS = f"{BASE}/twitter/user/last_tweets"
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


def _user_tweets(username: str, api_key: str) -> list[dict]:
    resp = requests.get(
        USER_LAST_TWEETS,
        params={"userName": username, "includeReplies": "false"},
        headers={"X-API-Key": api_key},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("tweets") or payload.get("data") or []


def _to_item(tw: dict, matched: str) -> Item | None:
    tid = str(tw.get("id") or tw.get("id_str") or "")
    if not tid:
        return None
    likes = int(tw.get("likeCount") or tw.get("favorite_count") or 0)
    author = (tw.get("author") or {}).get("userName") or tw.get("username") or ""
    return Item(
        source=SOURCE,
        id=tid,
        title=(tw.get("text") or "")[:120],
        url=tw.get("url") or f"https://x.com/i/web/status/{tid}",
        text=tw.get("text") or "",
        score=likes,
        author=author,
        created=tw.get("createdAt") or "",
        extra={"retweets": tw.get("retweetCount") or 0, "matched": matched},
    )


def collect(interests: Interests) -> list[Item]:
    api_key = twitterapi_io_key()
    if not api_key:
        return []  # silently disabled until a key is configured
    floor = interests.min_score.get(SOURCE, 0)
    seen: dict[str, Item] = {}

    # 1) keyword/advanced search
    for query in interests.x_queries:
        try:
            for tw in _search(query, api_key):
                item = _to_item(tw, matched=query)
                if item and item.id not in seen and item.score >= floor:
                    seen[item.id] = item
        except requests.RequestException as exc:
            warn(SOURCE, exc)

    # 2) curated account timelines (the AINews "N twitters" pattern)
    for username in interests.x_accounts:
        try:
            for tw in _user_tweets(username, api_key):
                item = _to_item(tw, matched=f"@{username}")
                if item and item.id not in seen and item.score >= floor:
                    seen[item.id] = item
        except requests.RequestException as exc:
            warn(SOURCE, exc)

    return list(seen.values())

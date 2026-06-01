"""Reddit collector.

Reddit blocks anonymous JSON in 2026, so the reliable path is app-only OAuth
(free): create a "script" app at https://www.reddit.com/prefs/apps and set
REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET. Without credentials the collector tries
the public JSON once and, if blocked, logs and skips — the run still succeeds.
"""
from __future__ import annotations

import os

import requests

from ..config import Interests
from ..models import Item
from .base import USER_AGENT, get, warn

SOURCE = "reddit"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
OAUTH_ROOT = "https://oauth.reddit.com"
TIMEOUT = 20


def _oauth_token() -> str | None:
    cid = os.environ.get("REDDIT_CLIENT_ID")
    secret = os.environ.get("REDDIT_CLIENT_SECRET")
    if not cid or not secret:
        return None
    resp = requests.post(
        TOKEN_URL,
        auth=(cid, secret),
        data={"grant_type": "client_credentials"},
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("access_token")


def _parse(payload: dict, sub: str, floor: int) -> list[Item]:
    items: list[Item] = []
    for child in payload.get("data", {}).get("children", []):
        d = child.get("data", {})
        score = int(d.get("score") or 0)
        if score < floor or not d.get("id"):
            continue
        items.append(Item(
            source=SOURCE,
            id=d["id"],
            title=d.get("title", ""),
            url="https://www.reddit.com" + d.get("permalink", ""),
            text=(d.get("selftext") or "")[:1200],
            score=score,
            author=d.get("author", ""),
            created="",
            extra={"subreddit": sub, "comments": d.get("num_comments") or 0,
                   "external_url": d.get("url", "")},
        ))
    return items


def collect(interests: Interests) -> list[Item]:
    floor = interests.min_score.get(SOURCE, 0)
    out: list[Item] = []
    try:
        token = _oauth_token()
    except Exception as exc:  # noqa: BLE001
        warn(SOURCE, exc)
        token = None

    for sub in interests.subreddits:
        try:
            if token:
                resp = requests.get(
                    f"{OAUTH_ROOT}/r/{sub}/top",
                    params={"t": "day", "limit": 25},
                    headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
                    timeout=TIMEOUT,
                )
            else:
                resp = get(f"https://www.reddit.com/r/{sub}/top.json",
                           params={"t": "day", "limit": 25})
            resp.raise_for_status()
            out.extend(_parse(resp.json(), sub, floor))
        except Exception as exc:  # noqa: BLE001
            warn(SOURCE, exc)
    return out

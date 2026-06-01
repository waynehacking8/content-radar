"""Collector registry. Each module exposes `collect(interests) -> list[Item]`."""
from __future__ import annotations

from ..config import Interests
from ..models import Item
from . import (
    arxiv,
    discord_collector,
    github_trending,
    gmail_imap,
    hackernews,
    reddit,
    x_twitterapi,
)

REGISTRY = {
    "hackernews": hackernews.collect,
    "arxiv": arxiv.collect,
    "github": github_trending.collect,
    "reddit": reddit.collect,
    "x": x_twitterapi.collect,
    "discord": discord_collector.collect,
    "gmail": gmail_imap.collect,
}


def collect_all(interests: Interests, sources=None) -> list[Item]:
    chosen = sources or list(REGISTRY)
    items: list[Item] = []
    for name in chosen:
        fn = REGISTRY.get(name)
        if fn:
            items.extend(fn(interests))
    return items

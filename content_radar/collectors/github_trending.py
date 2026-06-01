"""GitHub Trending collector.

GitHub has no official trending API, so we parse the public trending page. Kept
deliberately tolerant: a markup change degrades to fewer/zero items, never a crash.
"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ..config import Interests
from ..models import Item
from .base import get, warn

TRENDING = "https://github.com/trending"
SOURCE = "github"
_STARS_RE = re.compile(r"([\d,]+)\s+stars?\s+today")


def _collect_lang(lang: str, floor: int) -> list[Item]:
    params = {"since": "daily"}
    url = f"{TRENDING}/{lang}" if lang else TRENDING
    resp = get(url, params=params)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    items: list[Item] = []
    for article in soup.select("article.Box-row"):
        link = article.select_one("h2 a")
        if not link:
            continue
        repo = link.get("href", "").strip("/")
        if not repo:
            continue
        desc_el = article.select_one("p")
        desc = desc_el.get_text(strip=True) if desc_el else ""
        stars_today = 0
        m = _STARS_RE.search(article.get_text(" ", strip=True))
        if m:
            stars_today = int(m.group(1).replace(",", ""))
        if stars_today < floor:
            continue
        items.append(Item(
            source=SOURCE,
            id=repo,
            title=repo,
            url=f"https://github.com/{repo}",
            text=desc[:600],
            score=stars_today,
            author=repo.split("/")[0],
            created="",
            extra={"lang": lang or "all", "stars_today": stars_today},
        ))
    return items


def collect(interests: Interests) -> list[Item]:
    floor = interests.min_score.get(SOURCE, 0)
    seen: dict[str, Item] = {}
    for lang in interests.github_languages:
        try:
            for item in _collect_lang(lang, floor):
                if item.id not in seen or item.score > seen[item.id].score:
                    seen[item.id] = item
        except Exception as exc:  # noqa: BLE001
            warn(SOURCE, exc)
    return list(seen.values())

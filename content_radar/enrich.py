"""Phase 3 — recursive link enrichment.

AINews doesn't just summarise a post; it clicks through the link and summarises
the article too. This fetches the top items' URLs, extracts readable text, and
attaches it to the item so the digest synthesises real content, not just titles.

Best-effort: a fetch failure leaves the item untouched, never breaks the run.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from bs4 import BeautifulSoup

from .collectors.base import get, warn
from .models import Item

# Listing pages (already carry a good description) gain little from a full fetch.
SKIP_HOST_FRAGMENTS = ("github.com/trending", "news.ycombinator.com")
_STRIP_TAGS = ("script", "style", "nav", "header", "footer", "aside", "form")


def fetch_readable_text(url: str, max_chars: int = 2000) -> str:
    resp = get(url)
    resp.raise_for_status()
    ctype = resp.headers.get("content-type", "")
    if "html" not in ctype and "text" not in ctype:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(_STRIP_TAGS):
        tag.decompose()
    body = soup.find("article") or soup.find("main") or soup.body or soup
    text = " ".join(body.get_text(" ").split())
    return text[:max_chars]


def _should_enrich(item: Item) -> bool:
    if not item.url or len(item.text) > 600:
        return False
    return not any(frag in item.url for frag in SKIP_HOST_FRAGMENTS)


def enrich_items(items: Iterable[Item], top_n: int = 12, max_chars: int = 2000) -> list[Item]:
    """Fetch + attach article text for the top_n items that lack body content."""
    out: list[Item] = []
    budget = top_n
    for item in items:
        if budget > 0 and _should_enrich(item):
            try:
                extra = fetch_readable_text(item.url, max_chars)
                if extra:
                    merged = (item.text + "\n" + extra).strip()[:max_chars]
                    item = replace(item, text=merged, extra={**item.extra, "enriched": True})
                budget -= 1
            except Exception as exc:  # noqa: BLE001 - never break the run
                warn("enrich", exc)
                budget -= 1
        out.append(item)
    return out

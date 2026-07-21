"""AINews watcher — forward the newest unprocessed newsletter.

The scheduled GitHub Actions workflow (.github/workflows/ainews-watch.yml)
checks once daily after the usual arrival window. A missing issue is a cheap
no-op; a delayed issue remains eligible on the next day's run.

All dedup state lives in Gmail itself: a successful forward applies
config.ainews_forwarded_label() to the original mail, and the watch query
excludes that label — every poll is idempotent, with no state files and no
races between overlapping runs.
"""
from __future__ import annotations

from . import config
from .collectors import gmail_imap
from .models import Item


def pending_count(query: str | None = None) -> int:
    """How many fresh, not-yet-forwarded newsletters are waiting.

    Headers-only IMAP search — cheap enough to run on every poll before any
    heavy dependencies are installed.
    """
    return gmail_imap.search_count(query or config.ainews_watch_query())


def find_unforwarded(query: str | None = None,
                     max_chars: int = gmail_imap.FULL_CHARS) -> Item | None:
    """Fetch the newest fresh, not-yet-forwarded newsletter in full, or None."""
    items = gmail_imap.fetch(query or config.ainews_watch_query(),
                             limit=1, max_chars=max_chars)
    return items[0] if items else None


def mark_forwarded(item: Item) -> bool:
    """Label the original newsletter so later polls skip it (Gmail-side dedup)."""
    return gmail_imap.add_label(item.id, config.ainews_forwarded_label())

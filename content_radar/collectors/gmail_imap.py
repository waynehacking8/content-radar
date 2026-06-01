"""Gmail collector — fold AI-news newsletters from your own inbox into the digest.

Newsletters like AINews are already expert-curated, so they're the highest-signal,
lowest-cost input you can add. This reads matching emails over IMAP; Gmail's
`X-GM-RAW` lets us use normal Gmail search syntax (see Interests.gmail_query).

Auth uses a FREE Gmail App Password (not your login password, no paid API):
  https://myaccount.google.com/apppasswords
Then set GMAIL_USER + GMAIL_APP_PASSWORD. Disabled unless both are present.
"""
from __future__ import annotations

import email
import imaplib
import os
import re
from email.header import decode_header, make_header

from bs4 import BeautifulSoup

from ..config import Interests
from ..models import Item
from .base import warn

SOURCE = "gmail"
IMAP_HOST = "imap.gmail.com"
MAX_EMAILS = 12
MAX_CHARS = 4000           # enough for digest synthesis (keeps the corpus lean)
FULL_CHARS = 60_000        # for faithful full-newsletter translation


def _creds() -> tuple[str | None, str | None]:
    return os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD")


def _decode(value: str) -> str:
    try:
        return str(make_header(decode_header(value)))
    except Exception:  # noqa: BLE001
        return value or ""


def _normalize(text: str) -> str:
    """Trim each line and collapse runs of blank lines — keeps section/paragraph
    structure (so a faithful translation can mirror it) without runaway whitespace."""
    lines = [ln.strip() for ln in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _body_text(msg) -> str:
    html = text = ""
    for part in msg.walk():
        ctype = part.get_content_type()
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        decoded = payload.decode(part.get_content_charset() or "utf-8", "ignore")
        if ctype == "text/html" and not html:
            html = decoded
        elif ctype == "text/plain" and not text:
            text = decoded
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        # newline separator preserves the newsletter's sections and bullet items
        return _normalize(soup.get_text("\n"))
    return _normalize(text)


def fetch(query: str, limit: int = MAX_EMAILS, max_chars: int = MAX_CHARS) -> list[Item]:
    """Fetch up to `limit` emails matching a Gmail-syntax query (X-GM-RAW).

    Each Item carries the email's Date in `created` (so history is dated). Set a
    large limit to import a whole newsletter archive; raise `max_chars` (e.g.
    FULL_CHARS) to keep the full body for faithful translation.
    """
    user, password = _creds()
    if not user or not password or not query:
        return []
    items: list[Item] = []
    try:
        conn = imaplib.IMAP4_SSL(IMAP_HOST)
        conn.login(user, password)
        conn.select("INBOX")
        typ, data = conn.search(None, "X-GM-RAW", f'"{query}"')
        ids = data[0].split() if (typ == "OK" and data and data[0]) else []
        for num in reversed(ids[-limit:]):
            typ, raw = conn.fetch(num, "(RFC822)")
            if typ != "OK" or not raw or not raw[0]:
                continue
            msg = email.message_from_bytes(raw[0][1])
            subject = _decode(msg.get("Subject", ""))
            sender = _decode(msg.get("From", ""))
            body = _body_text(msg)[:max_chars]
            items.append(Item(
                source=SOURCE,
                id=str(msg.get("Message-ID") or num.decode()),
                title=subject[:160],
                url="",  # newsletters: no single canonical URL
                text=f"{sender}: {body}",
                score=0,
                author=sender,
                created=msg.get("Date", ""),  # the email's date — history is dated
                extra={"newsletter": True},
            ))
        conn.logout()
    except Exception as exc:  # noqa: BLE001 - never break the run
        warn(SOURCE, exc)
    return items


def collect(interests: Interests) -> list[Item]:
    return fetch(interests.gmail_query, MAX_EMAILS)

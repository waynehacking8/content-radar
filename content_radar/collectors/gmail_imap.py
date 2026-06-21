"""Gmail collector — fold AI-news newsletters from your own inbox into the digest.

Newsletters like AINews are already expert-curated, so they're the highest-signal,
lowest-cost input you can add. This reads matching emails over IMAP; Gmail's
`X-GM-RAW` lets us use normal Gmail search syntax (see Interests.gmail_query).

Auth uses a FREE Gmail App Password (not your login password, no paid API):
  https://myaccount.google.com/apppasswords
Then set GMAIL_USER + GMAIL_APP_PASSWORD. Disabled unless both are present.
"""
from __future__ import annotations

import base64
import contextlib
import email
import imaplib
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.header import decode_header, make_header

import requests as _requests
from bs4 import BeautifulSoup

from ..config import Interests
from ..models import Item, normalize_datetime
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
    lines = [ln.strip() for ln in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


# ---------------------------------------------------------------------------
# URL-preserving HTML → text
# ---------------------------------------------------------------------------

_REDIRECT_B64_RE = re.compile(r"https://substack\.com/redirect/2/([A-Za-z0-9_-]+)")


def _resolve_substack_url(href: str) -> str | None:
    """Decode or follow a Substack redirect to get the real destination URL."""
    m = _REDIRECT_B64_RE.match(href)
    if m:
        try:
            padded = m.group(1) + "=" * (4 - len(m.group(1)) % 4)
            obj = json.loads(base64.urlsafe_b64decode(padded))
            url = obj.get("e", "")
            return url.split("?")[0] if url else None
        except Exception:  # noqa: BLE001
            pass
    if "substack.com/redirect/" in href:
        try:
            resp = _requests.head(href, allow_redirects=True, timeout=3)
            url = resp.url.split("?")[0]
            if "substack.com" not in url:
                return url
        except Exception:  # noqa: BLE001
            pass
        return None
    if "/profile/" in href or "/app-link/" in href or "substack.com" in href:
        return None
    return href.split("?")[0]


def _resolve_urls_bulk(hrefs: set[str]) -> dict[str, str | None]:
    """Resolve a set of Substack redirect URLs in parallel."""
    resolved: dict[str, str | None] = {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(_resolve_substack_url, h): h for h in hrefs}
        for f in as_completed(futures):
            href = futures[f]
            try:
                resolved[href] = f.result()
            except Exception:  # noqa: BLE001
                resolved[href] = None
    return resolved


def _html_and_text(msg) -> tuple[str, str]:
    """Pull the first text/html and text/plain parts out of a MIME message."""
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
    return html, text


def _body_text_with_urls(msg) -> str:
    """Extract body text from an email, preserving real URLs inline.

    For HTML emails (e.g. Substack newsletters), resolves redirect URLs and
    inlines them as `text (https://real-url)` so chunked text retains source
    attribution for every story.
    """
    html, text = _html_and_text(msg)
    if not html:
        return _normalize(text)

    soup = BeautifulSoup(html, "html.parser")

    # Collect and resolve all anchor hrefs
    all_hrefs = {a["href"] for a in soup.find_all("a", href=True)}
    resolved = _resolve_urls_bulk(all_hrefs) if all_hrefs else {}

    # Replace anchor tags with text (URL) inline
    for a in soup.find_all("a", href=True):
        url = resolved.get(a["href"])
        anchor_text = a.get_text().strip()
        if url and anchor_text:
            a.replace_with(f"{anchor_text} ({url})")
        else:
            a.replace_with(anchor_text or "")

    for tag in soup(["script", "style"]):
        tag.decompose()

    return _normalize(soup.get_text("\n"))


def _body_text(msg) -> str:
    """Legacy fast path — strips URLs (used when max_chars is small)."""
    html, text = _html_and_text(msg)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return _normalize(soup.get_text("\n"))
    return _normalize(text)


# ---------------------------------------------------------------------------
# IMAP session
# ---------------------------------------------------------------------------

class GmailAuthError(RuntimeError):
    """Gmail IMAP login was rejected (bad/expired app password, wrong user).

    Distinct from "no new mail" so callers can fail loudly instead of silently
    reporting an empty result — an auth outage that returns 0 looks identical to
    a genuinely empty inbox and hides a broken pipeline for days.
    """


@contextlib.contextmanager
def _session(readonly: bool = False):
    user, password = _creds()
    if not user or not password:
        yield None
        return
    conn = imaplib.IMAP4_SSL(IMAP_HOST)
    try:
        try:
            conn.login(user, password)
        except imaplib.IMAP4.error as exc:
            raise GmailAuthError(
                f"Gmail login rejected for {user!r}: {exc}. The GMAIL_APP_PASSWORD "
                "is likely expired/revoked — regenerate at "
                "https://myaccount.google.com/apppasswords and update the secret."
            ) from exc
        conn.select("INBOX", readonly=readonly)
        yield conn
    finally:
        with contextlib.suppress(Exception):
            conn.logout()


def _gmail_search(conn, query: str) -> list[bytes]:
    typ, data = conn.search(None, "X-GM-RAW", f'"{query}"')
    return data[0].split() if (typ == "OK" and data and data[0]) else []


def search_count(query: str) -> int:
    if not query:
        return 0
    try:
        with _session(readonly=True) as conn:
            return len(_gmail_search(conn, query)) if conn is not None else 0
    except GmailAuthError:
        raise  # auth failure is not "0 results" — let the caller fail loudly
    except Exception as exc:  # noqa: BLE001
        warn(SOURCE, exc)
        return 0


def add_label(message_id: str, label: str) -> bool:
    if not message_id or not label:
        return False
    try:
        with _session() as conn:
            if conn is None:
                return False
            typ, data = conn.search(None, "HEADER", "Message-ID", f'"{message_id}"')
            ids = data[0].split() if (typ == "OK" and data and data[0]) else []
            if not ids:
                return False
            for num in ids:
                typ, _ = conn.store(num, "+X-GM-LABELS", f'("{label}")')
                if typ != "OK":
                    return False
            return True
    except Exception as exc:  # noqa: BLE001
        warn(SOURCE, exc)
        return False


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def fetch(query: str, limit: int = MAX_EMAILS, max_chars: int = MAX_CHARS,
          resolve_urls: bool | None = None) -> list[Item]:
    """Fetch emails matching a Gmail-syntax query.

    When resolve_urls is True (default when max_chars >= FULL_CHARS), Substack
    redirect URLs are resolved to real destinations and inlined into the text.
    """
    if not query:
        return []
    if resolve_urls is None:
        resolve_urls = max_chars >= FULL_CHARS
    items: list[Item] = []
    try:
        with _session() as conn:
            if conn is None:
                return []
            ids = _gmail_search(conn, query)
            for num in reversed(ids[-limit:]):
                typ, raw = conn.fetch(num, "(RFC822)")
                if typ != "OK" or not raw or not raw[0]:
                    continue
                msg = email.message_from_bytes(raw[0][1])
                subject = _decode(msg.get("Subject", ""))
                sender = _decode(msg.get("From", ""))
                if resolve_urls:
                    body = _body_text_with_urls(msg)[:max_chars]
                else:
                    body = _body_text(msg)[:max_chars]
                items.append(Item(
                    source=SOURCE,
                    id=str(msg.get("Message-ID") or num.decode()),
                    title=subject[:160],
                    url="",
                    text=f"{sender}: {body}",
                    score=0,
                    author=sender,
                    created=normalize_datetime(msg.get("Date", "")),
                    extra={"newsletter": True},
                ))
    except Exception as exc:  # noqa: BLE001
        warn(SOURCE, exc)
    return items


def collect(interests: Interests) -> list[Item]:
    return fetch(interests.gmail_query, MAX_EMAILS, max_chars=FULL_CHARS)

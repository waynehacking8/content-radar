"""SQLite FTS5 knowledge base over the collected corpus.

The durable record is the per-day JSON in the store (committed to the repo). This
builds a fast full-text index (FTS5 + BM25) from it on demand, so the bot can
search the whole history in milliseconds — no server, no embeddings.
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from .models import Item, dedup_by_key

_SCHEMA = """
CREATE VIRTUAL TABLE items USING fts5(
    key UNINDEXED, source, title, url UNINDEXED, text,
    created UNINDEXED, score UNINDEXED,
    tokenize = 'porter unicode61'
);
"""

# module-level cache so a long-running bot builds the index once
_CACHE: dict[str, tuple[int, sqlite3.Connection]] = {}


def load_corpus(store_dir: str | Path) -> list[Item]:
    """All items across every committed day, deduped by key (newest score wins)."""
    raw = Path(store_dir) / "raw"
    items: list[Item] = []
    for f in sorted(raw.glob("*.json")):
        try:
            items.extend(Item.from_dict(d) for d in json.loads(f.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return dedup_by_key(items)


def build_index(items: list[Item], db_path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(_SCHEMA)
    conn.executemany(
        "INSERT INTO items(key, source, title, url, text, created, score) "
        "VALUES (?,?,?,?,?,?,?)",
        [(i.key, i.source, i.title, i.url, i.text, i.created, i.score) for i in items],
    )
    conn.commit()
    return conn


def _fts_query(text: str) -> str | None:
    """Turn free text into a safe FTS5 OR-query (relevance match)."""
    terms = re.findall(r"[\w]+", text, flags=re.UNICODE)
    terms = [t for t in terms if len(t) > 1]
    if not terms:
        return None
    return " OR ".join(f'"{t}"' for t in terms)


def search(conn: sqlite3.Connection, query: str, limit: int = 25) -> list[Item]:
    fts = _fts_query(query)
    if fts is None:
        rows = conn.execute(
            "SELECT key, source, title, url, text, created, score FROM items "
            "ORDER BY score DESC LIMIT ?", (limit,)
        ).fetchall()
    else:
        try:
            rows = conn.execute(
                "SELECT key, source, title, url, text, created, score FROM items "
                "WHERE items MATCH ? ORDER BY bm25(items), score DESC LIMIT ?",
                (fts, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
    return [
        Item(key_split(k)[0], key_split(k)[1], title, url, text, int(score or 0),
             created=created)
        for (k, source, title, url, text, created, score) in rows
    ]


def key_split(key: str) -> tuple[str, str]:
    source, _, ident = key.partition(":")
    return source, ident


def get_index(store_dir: str | Path) -> sqlite3.Connection:
    """Cached index; rebuilds when the corpus file count changes."""
    raw = Path(store_dir) / "raw"
    fingerprint = sum(1 for _ in raw.glob("*.json")) if raw.exists() else 0
    cached = _CACHE.get(str(store_dir))
    if cached and cached[0] == fingerprint:
        return cached[1]
    conn = build_index(load_corpus(store_dir))
    _CACHE[str(store_dir)] = (fingerprint, conn)
    return conn

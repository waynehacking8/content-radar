"""Dated JSON store with dedup by Item.key.

Each collection run merges into one file per day (`store/raw/YYYY-MM-DD.json`).
Re-running on the same day is idempotent: items already seen are not duplicated,
and the higher score wins on conflict.

The `seen.json` registry tracks `first_seen` — the earliest date each Item.key
was collected. This lets the chat bot distinguish genuinely new stories from
multi-day trending items.
"""
from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Iterable

from .models import Item


def _day_path(store_dir: Path, day: date) -> Path:
    raw = Path(store_dir) / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    return raw / f"{day.isoformat()}.json"


def _seen_path(store_dir: Path) -> Path:
    raw = Path(store_dir) / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    return raw / "seen.json"


def load_seen(store_dir: Path) -> dict[str, str]:
    path = _seen_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_seen(store_dir: Path, seen: dict[str, str]) -> None:
    path = _seen_path(store_dir)
    path.write_text(json.dumps(seen, ensure_ascii=False), encoding="utf-8")


def load_day(store_dir: Path, day: date) -> tuple[Item, ...]:
    path = _day_path(store_dir, day)
    if not path.exists():
        return ()
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(Item.from_dict(d) for d in data)


def merge(existing: Iterable[Item], incoming: Iterable[Item]) -> tuple[Item, ...]:
    """Dedup by key; on collision keep the higher-scored item."""
    by_key: dict[str, Item] = {}
    for item in list(existing) + list(incoming):
        current = by_key.get(item.key)
        if current is None or item.score >= current.score:
            by_key[item.key] = item
    return tuple(sorted(by_key.values(), key=lambda i: i.score, reverse=True))


def stamp_first_seen(items: Iterable[Item], store_dir: Path, day: date) -> list[Item]:
    """Stamp each item with its first_seen date from the registry."""
    seen = load_seen(store_dir)
    today_str = day.isoformat()
    stamped = []
    for item in items:
        fs = seen.get(item.key, today_str)
        if item.key not in seen:
            seen[item.key] = today_str
        stamped.append(replace(item, first_seen=fs))
    save_seen(store_dir, seen)
    return stamped


def save_day(store_dir: Path, day: date, items: Iterable[Item]) -> Path:
    items_list = stamp_first_seen(list(items), store_dir, day)
    merged = merge(load_day(store_dir, day), items_list)
    path = _day_path(store_dir, day)
    path.write_text(
        json.dumps([i.to_dict() for i in merged], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path

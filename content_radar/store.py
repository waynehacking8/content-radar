"""Dated JSON store with dedup by Item.key.

Each collection run merges into one file per day (`store/raw/YYYY-MM-DD.json`).
Re-running on the same day is idempotent: items already seen are not duplicated,
and the higher score wins on conflict.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable

from .models import Item


def _day_path(store_dir: Path, day: date) -> Path:
    raw = Path(store_dir) / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    return raw / f"{day.isoformat()}.json"


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
        if current is None or item.score > current.score:
            by_key[item.key] = item
    return tuple(sorted(by_key.values(), key=lambda i: i.score, reverse=True))


def save_day(store_dir: Path, day: date, items: Iterable[Item]) -> Path:
    merged = merge(load_day(store_dir, day), items)
    path = _day_path(store_dir, day)
    path.write_text(
        json.dumps([i.to_dict() for i in merged], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path

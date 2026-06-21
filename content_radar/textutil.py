"""Shared text helpers: pull JSON out of LLM output, format item blocks.

Both jobs were hand-rolled in 3-4 places (synthesize/digest/eval_qa). One copy
each here so the fragile fence-stripping regex lives in exactly one spot.
"""
from __future__ import annotations

import json
import re
from typing import Iterable

from .models import Item

_CLOSE = {"[": "]", "{": "}"}


def extract_json(text: str, kind: str = "["):
    """Parse the first JSON array (kind="[") or object (kind="{") out of model
    output, tolerating ``` fences and surrounding prose."""
    close = _CLOSE[kind]
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
    start, end = text.find(kind), text.rfind(close)
    if start == -1 or end == -1:
        noun = "array" if kind == "[" else "object"
        raise ValueError(f"no JSON {noun} in model output: {text[:200]}")
    return json.loads(text[start:end + 1])


def items_block(items: Iterable[Item], limit: int, snip: int = 280) -> str:
    """Numbered '[source · score] title / url / snippet' block for an LLM prompt."""
    lines = []
    for i, it in enumerate(list(items)[:limit], 1):
        snippet = (it.text or "").replace("\n", " ")[:snip]
        lines.append(
            f"{i}. [{it.source} · score {it.score}] {it.title}\n"
            f"   {it.url}\n   {snippet}"
        )
    return "\n".join(lines)

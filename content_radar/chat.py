"""Conversational layer over the radar (RAG-over-radar).

Grounds answers in the collected items + recent digests so the bot talks about
*your* AI-news feed, not its training data. Runs on the local `claude` CLI
(subscription), same as the digest — no API key.
"""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from . import config
from .models import Item
from .store import load_day
from .synthesize import run_claude_cli

_STOPWORDS = {
    "the", "and", "for", "what", "whats", "with", "this", "that", "how", "why",
    "are", "was", "were", "has", "have", "about", "tell", "show", "give", "any",
    "new", "news", "latest", "today", "did", "does", "can", "you", "your",
}


def _recent_items(store_dir: Path, days: int, today: _dt.date) -> list[Item]:
    items: list[Item] = []
    for delta in range(days):
        items.extend(load_day(store_dir, today - _dt.timedelta(days=delta)))
    return items


def _terms(question: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", question.lower())
            if len(w) > 2 and w not in _STOPWORDS]


def _overlap(item: Item, terms: list[str]) -> int:
    text = f"{item.title} {item.text}".lower()
    return sum(text.count(t) for t in terms)


def relevant_items(items: list[Item], question: str, k: int = 20) -> list[Item]:
    terms = _terms(question)
    if not terms:
        return sorted(items, key=lambda i: i.score, reverse=True)[:k]
    ranked = sorted(items, key=lambda i: (_overlap(i, terms), i.score), reverse=True)
    hits = [i for i in ranked if _overlap(i, terms) > 0]
    return (hits or ranked)[:k]


def recent_digests(digests_dir: Path, n: int = 2) -> str:
    files = sorted(Path(digests_dir).glob("digest-*.md"), reverse=True)[:n]
    return "\n\n".join(f.read_text(encoding="utf-8") for f in files)


def build_chat_prompt(question: str, items: list[Item], digest_text: str) -> str:
    ctx = "\n".join(
        f"- [{i.source}|score {i.score}] {i.title}\n  {i.url}\n  {(i.text or '')[:300]}"
        for i in items
    )
    return (
        "You are an AI-news assistant. Answer the user's question using the context "
        "below (recently collected signal + digests). Be concise and concrete, cite "
        "sources with their URLs inline, and if the context doesn't cover it, say so "
        "rather than guessing.\n"
        "ALWAYS reply in Traditional Chinese (繁體中文,台灣用語/詞彙),never Simplified "
        "Chinese, regardless of the language of the question or the sources. Keep "
        "technical terms (model names, etc.) in their original form.\n\n"
        f"=== RECENT DIGESTS ===\n{digest_text[:4000]}\n\n"
        f"=== RELEVANT SIGNAL ===\n{ctx[:6000]}\n\n"
        f"=== QUESTION ===\n{question}"
    )


def answer(question: str, *, store_dir: Path | None = None, digests_dir: Path | None = None,
           model: str | None = None, days: int = 7, k: int = 20) -> str:
    store_dir = store_dir or config.STORE_DIR
    digests_dir = digests_dir or config.DIGESTS_DIR
    model = model or config.synth_model()
    today = _dt.date.today()
    items = _recent_items(store_dir, days, today)
    chosen = relevant_items(items, question, k)
    prompt = build_chat_prompt(question, chosen, recent_digests(digests_dir))
    return run_claude_cli(prompt, model)

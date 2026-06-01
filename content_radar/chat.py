"""Conversational layer over the radar (RAG-over-radar).

Grounds answers in the collected items + recent digests so the bot talks about
*your* AI-news feed, not its training data. Runs on the local `claude` CLI
(subscription), same as the digest — no API key.
"""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from . import config, kb, rag
from .models import Item
from .store import load_day
from .synthesize import run_claude_cli

_STOPWORDS = {
    "the", "and", "for", "what", "whats", "with", "this", "that", "how", "why",
    "are", "was", "were", "has", "have", "about", "tell", "show", "give", "any",
    "new", "news", "latest", "today", "did", "does", "can", "you", "your",
}

# Agentic tool the model may use to fill knowledge-base gaps from the live web.
_WEB_TOOLS = ["WebSearch"]
# One-shot answer timeout (s). The web-fallback path adds tool-use turns, so it
# gets more headroom than the pure KB path.
_ANSWER_TIMEOUT_S = 300
_WEB_ANSWER_TIMEOUT_S = 420


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


def _fetch_url(url: str, timeout: int = 4) -> str | None:
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 (fixed scheme)
            if getattr(resp, "status", 200) == 200:
                return resp.read().decode("utf-8")
    except Exception:  # noqa: BLE001 - network best-effort; fall back to disk
        return None
    return None


def recent_digests(digests_dir: Path, n: int = 2, *, raw_base: str | None = None,
                   today: _dt.date | None = None) -> str:
    """The latest n digests for recency framing.

    Prefers the live repo over HTTP (raw GitHub) so a freshly-committed digest is
    visible within the CDN window (~5 min), not after the bot's 6-hourly restart.
    Falls back to local disk when HTTP is disabled/unreachable.
    """
    raw_base = config.digest_raw_base() if raw_base is None else raw_base
    if raw_base:
        today = today or _dt.date.today()
        texts = []
        for delta in range(n):
            day = today - _dt.timedelta(days=delta)
            md = _fetch_url(f"{raw_base.rstrip('/')}/digest-{day.isoformat()}.md")
            if md:
                texts.append(md)
        if texts:
            return "\n\n".join(texts)
    files = sorted(Path(digests_dir).glob("digest-*.md"), reverse=True)[:n]
    return "\n\n".join(f.read_text(encoding="utf-8") for f in files)


def build_chat_prompt(question: str, items: list[Item], digest_text: str,
                      web_fallback: bool = False) -> str:
    # Context engineering: full chunk text (no truncation), most relevant first,
    # each tagged with source + date. The long-context model handles it.
    ctx = "\n\n".join(
        f"[{i.source} · {i.created or 'n/a'}] {i.title}\n{i.url}\n{i.text}"
        for i in items
    )
    # Agentic RAG: prefer the retrieved KB (fast, grounded); only reach for the
    # web when the KB genuinely can't answer. Keeps well-covered questions instant.
    gap_policy = (
        "Prefer the retrieved context — it is your primary, trusted source. If it "
        "fully covers the question, answer from it WITHOUT searching the web. But if "
        "it lacks the specifics the question demands (exact hardware specs, precise "
        "funding figures, a niche vertical, or very recent news), you MUST use the "
        "WebSearch tool to fill the gap NOW — actually search; never merely suggest "
        "that the user search. For list/enumeration questions ('which companies…', "
        "'有哪些…'), if the context covers only part of the list, search to complete "
        "it rather than answering with a partial list. Grounding rules: (1) attach a "
        "specific date to every event/figure you state; (2) include ONLY items that "
        "fall inside the exact time window the question asks about — drop anything "
        "outside it; (3) every name, figure, or claim must come from the retrieved "
        "context or a web result you actually opened — cite its URL; never state a "
        "fact you cannot source, and never blur dates across periods."
        if web_fallback else
        "If the context genuinely doesn't cover it, say so rather than guessing."
    )
    return (
        "You are an AI-news assistant. Answer the user's question primarily from the "
        "retrieved context below (the most relevant passages first, each tagged with "
        "its source and date). Be concrete, synthesise across passages, cite sources "
        "with their URLs inline, and include dates when the question is about timing. "
        f"{gap_policy}\n"
        "Write ONLY the answer for the reader: never mention tools, web searches, "
        "retrieval, workflows, or any internal/system state (no 'Workflow…', no "
        "'根據已檢索的…' meta-narration). "
        "Label every monetary figure precisely — distinguish 募資金額 (raise) from "
        "估值 (valuation) from ARR/營收; never put one under another's label, and if a "
        "figure's type is unclear from the source, say so instead of guessing. "
        "ALWAYS reply in Traditional Chinese (繁體中文,台灣用語/詞彙),never Simplified "
        "Chinese, regardless of the language of the question or the sources. Keep "
        "technical terms (model names, etc.) in their original form.\n\n"
        f"=== RETRIEVED CONTEXT (most relevant first) ===\n{ctx}\n\n"
        f"=== TODAY'S DIGEST (for recency framing) ===\n{digest_text[:2500]}\n\n"
        f"=== QUESTION ===\n{question}"
    )


def answer(question: str, *, store_dir: Path | None = None, digests_dir: Path | None = None,
           model: str | None = None, k: int = 12, web_fallback: bool | None = None) -> str:
    store_dir = store_dir or config.STORE_DIR
    digests_dir = digests_dir or config.DIGESTS_DIR
    model = model or config.synth_model()
    web_fallback = config.web_fallback_enabled() if web_fallback is None else web_fallback
    # Industry-standard vector retrieval (Qdrant + fastembed) when configured,
    # else local SQLite FTS over the committed corpus.
    if rag.configured():
        chosen = rag.search(question, limit=k)
    else:
        chosen = kb.search(kb.get_index(store_dir), question, limit=k)
    prompt = build_chat_prompt(question, chosen, recent_digests(digests_dir),
                               web_fallback=web_fallback)
    tools = _WEB_TOOLS if web_fallback else None
    timeout = _WEB_ANSWER_TIMEOUT_S if web_fallback else _ANSWER_TIMEOUT_S
    return run_claude_cli(prompt, model, timeout=timeout, allowed_tools=tools)

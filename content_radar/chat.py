"""Conversational layer over the radar (RAG-over-radar).

Two modes:
  MCP (default) — the LLM calls search_news / get_digest tools via the MCP
    server. It decides what to search for, can refine queries, and uses
    first_seen filtering to exclude multi-day trending repeats.
  Classic — single-shot RAG prompt-stuffing fallback (no MCP needed).

Set CHAT_MODE=classic to use the legacy path.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
from pathlib import Path

from . import config, kb, rag
from .models import Item, normalize_datetime
from .synthesize import run_claude_cli
from .temporal import TemporalIntent, TemporalTier, detect_temporal_intent

_MCP_CONFIG = str(Path(__file__).resolve().parent.parent / "mcp_config.json")

_ANSWER_TIMEOUT_S = 300
_TOOL_ANSWER_TIMEOUT_S = 420

_STOPWORDS = {
    "the", "and", "for", "what", "whats", "with", "this", "that", "how", "why",
    "are", "was", "were", "has", "have", "about", "tell", "show", "give", "any",
    "new", "news", "latest", "today", "did", "does", "can", "you", "your",
    "的", "了", "是", "在", "和", "也", "都", "但", "與", "及",
}

# ---------------------------------------------------------------------------
# MCP tool-calling path (default)
# ---------------------------------------------------------------------------

def _build_tool_prompt(question: str, temporal: TemporalIntent,
                       today: _dt.date) -> str:
    """System prompt that instructs the LLM to use the MCP tools."""
    date_hint = ""
    if temporal.tier == TemporalTier.EXPLICIT and temporal.date_from:
        d = temporal.date_from.strftime("%Y-%m-%d")
        date_hint = (
            f"\nThe user is asking about {d}. Use the search_news tool with "
            f"first_seen_from=\"{d}\" and first_seen_to=\"{d}\" to find "
            "stories first collected on that date. This filters out stories "
            "that were trending for multiple days — only genuinely new items "
            "from that date are returned. Do NOT include stories that were "
            "already reported on earlier dates."
        )
    elif temporal.tier == TemporalTier.IMPLICIT:
        date_hint = (
            "\nThe user wants recent/latest news. Use search_news without "
            "date filters to get the most relevant items, but prefer newer ones."
        )

    return (
        f"Today is {today.isoformat()} (UTC). "
        "You are an AI-news assistant with access to a knowledge base of "
        "collected AI/ML news items. Use the search_news tool to find relevant "
        "items. You can call it multiple times with different queries to get "
        "comprehensive coverage."
        f"{date_hint}\n\n"
        "Response rules:\n"
        "- Be concrete, cite sources with URLs inline\n"
        "- ALWAYS reply in Traditional Chinese (繁體中文,台灣用語)\n"
        "- Keep technical terms in their original form\n"
        "- Write ONLY the answer — never mention tools, searches, or retrieval\n"
        "- Label monetary figures precisely (募資 vs 估值 vs 營收)\n\n"
        f"Question: {question}"
    )


def _answer_mcp(question: str, model: str, web_fallback: bool) -> str:
    """Answer using MCP tool calling — the LLM searches the KB itself."""
    temporal = detect_temporal_intent(question)
    today = _dt.date.today()
    prompt = _build_tool_prompt(question, temporal, today)

    tools = ["mcp__radar__search_news", "mcp__radar__get_digest"]
    if web_fallback:
        tools.append("WebSearch")

    return run_claude_cli(
        prompt, model,
        timeout=_TOOL_ANSWER_TIMEOUT_S,
        allowed_tools=tools,
        mcp_config=_MCP_CONFIG,
    )


# ---------------------------------------------------------------------------
# Classic prompt-stuffing path (fallback)
# ---------------------------------------------------------------------------

def _filter_by_date(items: list[Item], intent: TemporalIntent) -> list[Item]:
    if not intent.date_from:
        return items
    from_str = intent.date_from.strftime("%Y-%m-%d")
    to_str = intent.date_to.strftime("%Y-%m-%d") if intent.date_to else None
    filtered = []
    for item in items:
        if not item.created:
            continue
        normed = normalize_datetime(item.created)
        item_date = normed[:10]
        if item_date < from_str:
            continue
        if to_str and item_date > to_str:
            continue
        filtered.append(item)
    return filtered


def _fetch_url(url: str, timeout: int = 4) -> str | None:
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            if getattr(resp, "status", 200) == 200:
                return resp.read().decode("utf-8")
    except Exception:  # noqa: BLE001
        return None
    return None


def recent_digests(digests_dir: Path, n: int = 2, *, raw_base: str | None = None,
                   today: _dt.date | None = None) -> str:
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


_TERM_RE = re.compile(r"[a-z0-9]{2,}|[一-鿿㐀-䶿]{1,2}", re.UNICODE)


def _terms(question: str) -> list[str]:
    return [w for w in _TERM_RE.findall(question.lower())
            if w not in _STOPWORDS]


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


def build_chat_prompt(question: str, items: list[Item], digest_text: str,
                      web_fallback: bool = False,
                      today: _dt.date | None = None) -> str:
    """Classic prompt-stuffing path (used when CHAT_MODE=classic)."""
    today = today or _dt.date.today()
    ctx = "\n\n".join(
        f"[{i.source} · {i.created or 'n/a'}] {i.title}\n{i.url}\n{i.text}"
        for i in items
    )
    gap_policy = (
        "Prefer the retrieved context. If it lacks specifics the question "
        "demands, use the WebSearch tool to fill the gap. Every claim must "
        "come from context or a web result you opened — cite its URL."
        if web_fallback else
        "If the context genuinely doesn't cover it, say so rather than guessing."
    )
    digest_section = f"\n\n=== DIGEST ===\n{digest_text[:2500]}" if digest_text else ""
    return (
        f"Today is {today.isoformat()} (UTC). "
        "You are an AI-news assistant. Answer from the retrieved context below. "
        "Be concrete, cite sources with URLs inline. "
        f"{gap_policy}\n"
        "ALWAYS reply in Traditional Chinese (繁體中文,台灣用語). "
        "Keep technical terms in their original form.\n\n"
        f"=== RETRIEVED CONTEXT ===\n{ctx}"
        f"{digest_section}\n\n"
        f"=== QUESTION ===\n{question}"
    )


def _answer_classic(question: str, model: str, web_fallback: bool,
                     store_dir: Path, digests_dir: Path, k: int) -> str:
    """Classic single-shot RAG path."""
    temporal = detect_temporal_intent(question)
    if rag.configured():
        chosen = rag.search(question, limit=k, temporal_intent=temporal)
    else:
        chosen = kb.search(kb.get_index(store_dir), question, limit=k)
        if temporal.tier == TemporalTier.EXPLICIT:
            chosen = _filter_by_date(chosen, temporal)

    # No digest for EXPLICIT temporal queries — it contains stale repeats
    digest_text = "" if temporal.tier == TemporalTier.EXPLICIT else recent_digests(digests_dir)

    prompt = build_chat_prompt(question, chosen, digest_text, web_fallback=web_fallback)
    tools = ["WebSearch"] if web_fallback else None
    timeout = _TOOL_ANSWER_TIMEOUT_S if web_fallback else _ANSWER_TIMEOUT_S
    return run_claude_cli(prompt, model, timeout=timeout, allowed_tools=tools)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _chat_mode() -> str:
    return os.environ.get("CHAT_MODE", "mcp").strip().lower()


def answer(question: str, *, store_dir: Path | None = None,
           digests_dir: Path | None = None, model: str | None = None,
           k: int = 12, web_fallback: bool | None = None) -> str:
    store_dir = store_dir or config.STORE_DIR
    digests_dir = digests_dir or config.DIGESTS_DIR
    model = model or config.synth_model()
    web_fallback = config.web_fallback_enabled() if web_fallback is None else web_fallback

    if _chat_mode() == "mcp" and rag.configured():
        return _answer_mcp(question, model, web_fallback)
    return _answer_classic(question, model, web_fallback, store_dir, digests_dir, k)

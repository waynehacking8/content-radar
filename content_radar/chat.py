"""Conversational layer over the radar (RAG-over-radar).

Enhanced single-shot RAG: retrieval with temporal filtering, first_seen dedup,
and reranking. Research shows this matches agentic RAG at 3.6x lower cost.

Digest is suppressed for EXPLICIT temporal queries ("today", "yesterday") to
prevent stale story pollution.
"""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from . import config, kb, rag
from .models import Item, normalize_datetime
from .synthesize import run_claude_cli
from .temporal import TemporalIntent, TemporalTier, detect_temporal_intent

_ANSWER_TIMEOUT_S = 300
_TOOL_ANSWER_TIMEOUT_S = 420

_URL_RE = re.compile(r'https?://[^\s\)>]+')
_URL_SKIP = {'substack.com', 'email-', 'smol.ai', 'latent.space/action'}
_URL_SEEN_PATH = Path(__file__).resolve().parent.parent / "store" / "url_seen.json"
_url_seen_cache: dict[str, str] | None = None


def _load_url_seen() -> dict[str, str]:
    """Load URL→earliest_first_seen registry (cached in-process)."""
    global _url_seen_cache
    if _url_seen_cache is None:
        try:
            import json as _json
            _url_seen_cache = _json.loads(_URL_SEEN_PATH.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            _url_seen_cache = {}
    return _url_seen_cache


def _extract_urls(text: str) -> set[str]:
    return {
        u.split("?")[0].rstrip("/")
        for u in _URL_RE.findall(text)
        if not any(s in u for s in _URL_SKIP)
    }


def _dedup_by_story(items: list[Item], target_date: str) -> list[Item]:
    """Remove chunks whose story URLs all appeared before target_date."""
    url_seen = _load_url_seen()
    if not url_seen:
        return items
    result = []
    for item in items:
        urls = _extract_urls(item.text)
        if not urls:
            result.append(item)
            continue
        has_new = any(url_seen.get(u, target_date) >= target_date for u in urls)
        if has_new:
            result.append(item)
    return result


# ---------------------------------------------------------------------------
# Enhanced RAG path — research-backed best practice
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


def build_chat_prompt(question: str, items: list[Item], digest_text: str,
                      web_fallback: bool = False,
                      today: _dt.date | None = None,
                      temporal_intent: TemporalIntent | None = None) -> str:
    today = today or _dt.date.today()
    ctx = "\n\n".join(
        f"[{i.source} · {i.created or 'n/a'} · first_seen:{i.first_seen or 'n/a'}] "
        f"{i.title}\n{i.url}\n{i.text}"
        for i in items
    )
    gap_policy = (
        "Prefer the retrieved context. If it lacks specifics the question "
        "demands, use the WebSearch tool to fill the gap. Every claim must "
        "come from context or a web result you opened — cite its URL."
        if web_fallback else
        "If the context genuinely doesn't cover it, say so rather than guessing."
    )
    temporal_rule = ""
    if temporal_intent and temporal_intent.tier == TemporalTier.EXPLICIT:
        date_label = temporal_intent.date_from.strftime("%Y-%m-%d") if temporal_intent.date_from else today.isoformat()
        if not items:
            temporal_rule = (
                f"\n\nCRITICAL: The user asks about {date_label}. No items were "
                "found for that date. Tell the user explicitly — do not fabricate."
            )
        else:
            temporal_rule = (
                f"\n\nDATE: The user asks about {date_label}. Only discuss items "
                "with first_seen matching that date. Ignore anything older."
            )
    digest_section = ""
    if digest_text and not (temporal_intent and temporal_intent.tier == TemporalTier.EXPLICIT):
        digest_section = f"\n\n=== DIGEST ===\n{digest_text[:2500]}"
    return (
        f"Today is {today.isoformat()} (UTC). "
        "You are an AI-news assistant. Answer from the retrieved context below. "
        "Be concrete, cite sources with URLs inline. "
        f"{gap_policy}\n"
        "ALWAYS reply in Traditional Chinese (繁體中文,台灣用語). "
        "Keep technical terms in their original form."
        f"{temporal_rule}\n\n"
        f"=== RETRIEVED CONTEXT ===\n{ctx}"
        f"{digest_section}\n\n"
        f"=== QUESTION ===\n{question}"
    )


def _answer_enhanced(question: str, model: str, web_fallback: bool,
                     store_dir: Path, digests_dir: Path, k: int) -> str:
    """Enhanced single-shot RAG with temporal filtering + reranking + story dedup."""
    temporal = detect_temporal_intent(question)

    if rag.configured():
        fetch_k = k * 3 if temporal.tier == TemporalTier.EXPLICIT else k
        chosen = rag.search(question, limit=fetch_k, prefetch=80,
                            per_parent=15, temporal_intent=temporal)
    else:
        chosen = kb.search(kb.get_index(store_dir), question, limit=k)
        if temporal.tier == TemporalTier.EXPLICIT:
            chosen = _filter_by_date(chosen, temporal)

    if temporal.tier == TemporalTier.EXPLICIT and temporal.date_from:
        target = temporal.date_from.strftime("%Y-%m-%d")
        chosen = _dedup_by_story(chosen, target)

    digest_text = "" if temporal.tier == TemporalTier.EXPLICIT else recent_digests(digests_dir)

    prompt = build_chat_prompt(question, chosen, digest_text,
                               web_fallback=web_fallback, temporal_intent=temporal)
    tools = ["WebSearch"] if web_fallback else None
    timeout = _TOOL_ANSWER_TIMEOUT_S if web_fallback else _ANSWER_TIMEOUT_S
    return run_claude_cli(prompt, model, timeout=timeout, allowed_tools=tools)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def answer(question: str, *, store_dir: Path | None = None,
           digests_dir: Path | None = None, model: str | None = None,
           k: int = 20, web_fallback: bool | None = None) -> str:
    store_dir = store_dir or config.STORE_DIR
    digests_dir = digests_dir or config.DIGESTS_DIR
    model = model or config.synth_model()
    web_fallback = config.web_fallback_enabled() if web_fallback is None else web_fallback

    return _answer_enhanced(question, model, web_fallback, store_dir, digests_dir, k)

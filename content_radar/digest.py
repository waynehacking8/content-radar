"""Phase 2 — AINews-style thematic digest.

Two-stage synthesis, the move that separates a digest from a list:

  1. cluster the day's signal into a handful of themes;
  2. write a short narrative per theme that synthesises the items and attributes
     each claim with an inline link;
  3. surface the top items by engagement.

Runs on the local `claude` CLI (your subscription) via `synthesize.run_claude_cli`.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from pathlib import Path
from typing import Iterable

from .models import Item
from .synthesize import run_claude_cli

DIGEST_INSTRUCTIONS = """\
You are the editor of a daily AI/dev intelligence digest (think AINews by smol.ai).
From the raw signal below, produce a tight, high-signal digest. Cluster the items
into {max_themes} or fewer THEMES that actually matter today; ignore noise. For
each theme write a 2-4 sentence narrative that synthesises what happened and why
it matters, weaving in the specific items. Be concrete and non-hyped.

Return ONLY a JSON object (no prose around it):
{
  "headline": "one sentence on what mattered most today",
  "themes": [
    {
      "title": "short theme title",
      "narrative": "2-4 sentences synthesising the theme",
      "sources": ["https://...", "https://..."]
    }
  ],
  "top_by_engagement": [
    {"title": "...", "url": "https://...", "source": "hackernews", "score": 2410}
  ]
}
Pick top_by_engagement from the highest-scored items (max 8)."""


def _items_block(items: Iterable[Item], limit: int) -> str:
    lines = []
    for i, it in enumerate(list(items)[:limit], 1):
        snippet = (it.text or "").replace("\n", " ")[:240]
        lines.append(
            f"{i}. [{it.source} · score {it.score}] {it.title}\n"
            f"   {it.url}\n   {snippet}"
        )
    return "\n".join(lines)


def build_digest_prompt(items: Iterable[Item], max_themes: int, item_limit: int) -> str:
    instructions = DIGEST_INSTRUCTIONS.replace("{max_themes}", str(max_themes))
    return f"{instructions}\n\n=== RAW SIGNAL ===\n{_items_block(items, item_limit)}"


def extract_json_object(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON object in model output: {text[:200]}")
    return json.loads(text[start : end + 1])


def synthesize_digest(items, *, model, max_themes=5, item_limit=60) -> dict:
    prompt = build_digest_prompt(items, max_themes, item_limit)
    return extract_json_object(run_claude_cli(prompt, model))


JUDGE_INSTRUCTIONS = """\
You are the editor of a daily AI/dev digest. Below are several candidate digests
as JSON. Pick the single best one: most signal, sharpest and least-overlapping
themes, best source attribution, least hype, most useful to a practitioner.
Return ONLY a JSON object: {"best": <zero-based index>, "why": "one short line"}."""


def pick_best_digest(candidates: list[dict], *, model) -> dict:
    if len(candidates) == 1:
        return candidates[0]
    listing = "\n\n".join(
        f"=== CANDIDATE {i} ===\n{json.dumps(c, ensure_ascii=False)[:3000]}"
        for i, c in enumerate(candidates)
    )
    out = run_claude_cli(f"{JUDGE_INSTRUCTIONS}\n\n{listing}", model)
    try:
        idx = int(extract_json_object(out).get("best", 0))
    except (ValueError, TypeError):
        idx = 0
    return candidates[max(0, min(idx, len(candidates) - 1))]


def synthesize_digest_best_of(items, *, model, max_themes=5, item_limit=60, n=1) -> dict:
    """Generate `n` candidate digests and have the model pick the best (AINews-style)."""
    candidates = [
        synthesize_digest(items, model=model, max_themes=max_themes, item_limit=item_limit)
        for _ in range(max(1, n))
    ]
    return pick_best_digest(candidates, model=model)


def render_digest_markdown(data: dict, day: _dt.date, counts: dict[str, int]) -> str:
    total = sum(counts.values())
    checked = ", ".join(f"{k}({v})" for k, v in sorted(counts.items())) or "no sources"
    out: list[str] = [
        f"# AI Radar — {day.isoformat()}",
        "",
        f"> {data.get('headline', '').strip()}",
        "",
        f"*Checked {checked} — {total} items.*",
        "",
        "## Themes",
        "",
    ]
    for theme in data.get("themes", []):
        out.append(f"### {theme.get('title', 'Untitled').strip()}")
        out.append("")
        out.append(theme.get("narrative", "").strip())
        sources = theme.get("sources") or []
        if sources:
            out.append("")
            out.append("Sources: " + " · ".join(f"<{u}>" for u in sources))
        out.append("")

    top = data.get("top_by_engagement") or []
    if top:
        out.append("## Top by engagement")
        out.append("")
        for t in top:
            score = t.get("score")
            tail = f" — {t.get('source', '')} · {score}" if score is not None else ""
            out.append(f"- [{t.get('title', '').strip()}]({t.get('url', '')}){tail}")
        out.append("")
    return "\n".join(out)


def write_digest(markdown: str, out_dir, day: _dt.date) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"digest-{day.isoformat()}.md"
    path.write_text(markdown, encoding="utf-8")
    return path


ZH_TRANSLATE_INSTRUCTIONS = """\
你是專業科技新聞譯者。把下面這**一段** AINews 英文電子報**完整忠實**翻成
**繁體中文(台灣用語)**,讀者是工程師。鐵則:
- 逐段翻譯,**不可省略、不可摘要、不可濃縮** —— 保留這段的每一個章節與條目;
  原文多長,譯文就多長。
- 模型名稱、公司名、帳號(@handle)、技術術語(RAG、MoE、Flash Attention 等)、
  數字、與所有連結 **原樣保留**,不要翻譯也不要刪除。
- 用 Markdown 呈現:章節標題用 ## / ###,條目分段清楚易讀。
- 這只是整封信的一個片段,直接從這段開頭翻起,**不要**自行補開場白或結語。
只輸出翻譯後的 Markdown,前後不要加任何說明或註解。"""

# A single giant `claude -p` call on a 30k+ char newsletter is fragile: long
# streaming generations hit socket drops (local) and timeouts (CI) — both
# observed 2026-06-09. Translate in section-aware chunks instead: each call is
# short and fast, and a transient failure only costs one chunk (retried).
TRANSLATE_CHUNK_CHARS = 6000
TRANSLATE_RETRIES = 3


def _hard_split(block: str, max_chars: int) -> list[str]:
    """Break a single oversized block (no blank lines) into <=max_chars pieces,
    preferring line boundaries, falling back to a raw char window for a single
    very long line."""
    if len(block) <= max_chars:
        return [block]
    pieces: list[str] = []
    cur = ""
    for line in block.split("\n"):
        while len(line) > max_chars:  # a single line longer than the budget
            if cur:
                pieces.append(cur); cur = ""
            pieces.append(line[:max_chars]); line = line[max_chars:]
        if cur and len(cur) + len(line) + 1 > max_chars:
            pieces.append(cur); cur = line
        else:
            cur = f"{cur}\n{line}" if cur else line
    if cur:
        pieces.append(cur)
    return pieces


def _split_for_translation(text: str, max_chars: int = TRANSLATE_CHUNK_CHARS) -> list[str]:
    """Split a newsletter into <=max_chars chunks, breaking on blank lines /
    markdown headings so a section is never cut mid-sentence. A single block
    that is itself larger than max_chars is hard-split further so no chunk ever
    exceeds the budget (a giant chunk would defeat the point — see _hard_split)."""
    blocks = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    cur = ""
    for block in blocks:
        block = block.strip("\n")
        if not block:
            continue
        for piece in _hard_split(block, max_chars):
            if cur and len(cur) + len(piece) + 2 > max_chars:
                chunks.append(cur)
                cur = piece
            else:
                cur = f"{cur}\n\n{piece}" if cur else piece
    if cur:
        chunks.append(cur)
    return chunks or [text]


def _translate_chunk(chunk: str, model: str, timeout: int) -> str:
    prompt = f"{ZH_TRANSLATE_INSTRUCTIONS}\n\n=== AINEWS 原文片段 ===\n{chunk}"
    last_exc: Exception | None = None
    for attempt in range(1, TRANSLATE_RETRIES + 1):
        try:
            return run_claude_cli(prompt, model, timeout=timeout).strip()
        except Exception as exc:  # noqa: BLE001 — retry transient CLI/socket errors
            last_exc = exc
            print(f"  translate chunk attempt {attempt}/{TRANSLATE_RETRIES} failed: "
                  f"{str(exc)[:160]}")
    raise RuntimeError(f"chunk translation failed after {TRANSLATE_RETRIES} attempts: {last_exc}")


def chinese_newsletter_markdown(english_text: str, model: str, timeout: int = 1800) -> str:
    """Faithfully translate a full AINews newsletter into Traditional Chinese.

    Translated in section-aware chunks (see TRANSLATE_CHUNK_CHARS), each with a
    bounded retry, so one dropped connection no longer loses the whole issue.
    `timeout` is the per-chunk subprocess cap.
    """
    chunks = _split_for_translation(english_text)
    print(f"  translating in {len(chunks)} chunk(s) "
          f"(~{TRANSLATE_CHUNK_CHARS} chars each) ...")
    out: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        out.append(_translate_chunk(chunk, model, timeout))
        print(f"  chunk {i}/{len(chunks)} done")
    return "\n\n".join(out).strip()


EMAIL_SUMMARY_INSTRUCTIONS = """\
你是科技電子報的編輯。下面是今天整封 AINews 電子報的英文全文。
用**繁體中文（台灣用語）**寫一段「本期摘要」，讓讀者 30 秒內掌握整封信重點：
先用一句話總結今天最重要的事，接著 3–6 個條列（每條一句），點出最值得注意的
主題、工具或事件。只輸出摘要本身的 Markdown，不要前言、不要大標題、不要結語。"""


def summarize_for_email(english_text: str, model: str, timeout: int = 600) -> str:
    """A Traditional-Chinese TL;DR of the whole newsletter, to prepend to the email
    so the reader gets the gist before the full translation. Best-effort: returns ''
    on any failure so it never blocks delivery. Summarises the lede + top sections
    (where AINews puts the most important items), capped for speed."""
    prompt = f"{EMAIL_SUMMARY_INSTRUCTIONS}\n\n=== AINEWS 全文 ===\n{english_text[:12000]}"
    try:
        body = run_claude_cli(prompt, model, timeout=timeout).strip()
    except Exception as exc:  # noqa: BLE001
        print(f"  summary generation failed ({str(exc)[:120]}) — sending without it")
        return ""
    return f"## 📌 本期摘要\n\n{body}" if body else ""

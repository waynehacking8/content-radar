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
你是專業科技新聞譯者。把下面這封 AINews 英文電子報**完整忠實**翻成
**繁體中文(台灣用語)**,讀者是工程師。鐵則:
- 逐段翻譯,**不可省略、不可摘要、不可濃縮** —— 保留原文每一個章節
  (如 AI Twitter Recap 的各子主題、AI Reddit Recap、研究論文、Top tweets)
  與其中每一條目;原文多長,譯文就多長。
- 模型名稱、公司名、帳號(@handle)、技術術語(RAG、MoE、Flash Attention 等)、
  數字、與所有連結 **原樣保留**,不要翻譯也不要刪除。
- 用 Markdown 呈現:章節標題用 ## / ###,條目分段清楚易讀。
- 若原文開頭有一句話 TLDR,保留並翻譯它放在最前面。
只輸出翻譯後的 Markdown,前後不要加任何說明或註解。"""


def chinese_newsletter_markdown(english_text: str, model: str, timeout: int = 1800) -> str:
    """Faithfully translate a full AINews newsletter into Traditional Chinese.

    Unlike a digest, this preserves every section and item — the output length
    tracks the source. A long newsletter (30k+ chars) can take >10 min, so the
    timeout is 30 min — the old 600s cap killed the translation of a 32k-char
    issue on 2026-06-09.
    """
    prompt = f"{ZH_TRANSLATE_INSTRUCTIONS}\n\n=== AINEWS 原文 ===\n{english_text}"
    return run_claude_cli(prompt, model, timeout=timeout).strip()

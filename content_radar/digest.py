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


ZH_INSTRUCTIONS = """\
你是一份每日 AI/開發者情報日報的中文編輯。把下面這份英文 digest 改寫成一封
**繁體中文(台灣用語)** 的電子報,讀者是工程師。要求:
- 全文繁體中文,但模型名稱、公司名、技術術語(如 RAG、Transformer)保留原文。
- 保留每個連結(Markdown 連結或 <url> 角括號連結原樣保留,不要刪)。
- 保持原本的主題結構與重點,語氣精煉、不浮誇、有資訊密度。
- 開頭用一句話點出今天最重要的事。
只輸出改寫後的 Markdown,不要加任何說明文字。"""


def chinese_email_markdown(english_markdown: str, model: str) -> str:
    """Localize a built English digest into a Traditional Chinese email edition."""
    prompt = f"{ZH_INSTRUCTIONS}\n\n=== ENGLISH DIGEST ===\n{english_markdown}"
    return run_claude_cli(prompt, model).strip()

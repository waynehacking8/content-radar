"""Turn collected signal into review-ready post drafts with Claude.

Feeds the top-scored items to Claude, asks for accessible, knowledge-sharing
post drafts (a hook + body + tags, each tied to its sources), and writes them as
Markdown files with YAML front matter — the same shape a review-gated posting
queue consumes. Nothing is published here; drafts are for a human to approve.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from .models import Item

VOICE = """\
You write LinkedIn posts for an AI systems engineer pivoting to Solutions
Architect / Forward-Deployed roles. Voice: accessible knowledge-sharing, not
academic. Lead with a concrete hook or an opinion, explain one idea a general
developer audience can engage with, stay honest and non-hyped. Think "here's a
useful insight + why it matters", not a benchmark dump. 120-200 words. End with
3-5 lowercase-friendly hashtags. No emojis-as-bullets; use plain prose."""

SCHEMA_HINT = """\
Return ONLY a JSON array (no prose around it). Each element:
{
  "title": "short internal title",
  "angle": "building-in-public | accessible-lesson | opinionated-take | tool-spotlight",
  "body": "the full post text, ready to paste",
  "tags": ["LLM", "AI", ...],
  "source_urls": ["https://..."]
}
Produce {n} drafts, each grounded in one or more of the items below. Prefer
items that are genuinely interesting to a practitioner; skip noise."""


def _items_digest(items: Iterable[Item], limit: int) -> str:
    lines = []
    for i, it in enumerate(list(items)[:limit], 1):
        snippet = (it.text or "").replace("\n", " ")[:280]
        lines.append(
            f"{i}. [{it.source} · score {it.score}] {it.title}\n"
            f"   {it.url}\n   {snippet}"
        )
    return "\n".join(lines)


def build_prompt(items: Iterable[Item], n_drafts: int, item_limit: int) -> str:
    return (
        f"{VOICE}\n\n{SCHEMA_HINT.replace('{n}', str(n_drafts))}\n\n"
        f"=== TRENDING ITEMS ===\n{_items_digest(items, item_limit)}"
    )


def _extract_json(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON array in model output: {text[:200]}")
    return json.loads(text[start : end + 1])


def claude_cli_available() -> bool:
    return shutil.which("claude") is not None


def _result_text(stdout: str) -> str:
    """Pull the model's text out of `claude --output-format json` (or pass through)."""
    out = stdout.strip()
    try:
        obj = json.loads(out)
    except json.JSONDecodeError:
        return out
    if isinstance(obj, dict) and "result" in obj:
        return obj["result"]
    return out


def run_claude_cli(prompt: str, model: str, timeout: int = 300) -> str:
    """Run a one-shot Claude Code query using the local subscription auth.

    Uses `claude -p` (headless). No API key required: auth comes from the
    logged-in subscription locally, or from CLAUDE_CODE_OAUTH_TOKEN in CI
    (generate one with `claude setup-token`).
    """
    cmd = ["claude", "-p", "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        detail = (proc.stderr.strip() or proc.stdout.strip() or "no output")[:600]
        raise RuntimeError(f"claude CLI failed ({proc.returncode}): {detail}")
    return _result_text(proc.stdout)


def _run_via_api(prompt: str, model: str, api_key: str | None) -> str:
    if not api_key:
        raise ValueError("backend='api' requires an Anthropic API key")
    import anthropic  # imported lazily; only needed for the API backend

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")


def synthesize(items, *, model, n_drafts=5, item_limit=40,
               backend="cli", api_key=None) -> list[dict]:
    """Draft posts from collected items; returns a list of draft dicts.

    backend="cli"  -> local `claude` CLI on your subscription (default, no API key)
    backend="api"  -> Anthropic API with api_key (pay-per-token)
    """
    prompt = build_prompt(items, n_drafts, item_limit)
    if backend == "api":
        text = _run_via_api(prompt, model, api_key)
    else:
        text = run_claude_cli(prompt, model)
    return _extract_json(text)


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s or "draft")[:48]


def write_drafts(drafts: list[dict], out_dir: Path, start_date: _dt.date,
                 spacing_days: int = 2, platform: str = "linkedin") -> list[Path]:
    """Write each draft as a queue Markdown file (status: draft)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for idx, d in enumerate(drafts):
        day = start_date + _dt.timedelta(days=idx * spacing_days)
        slug = _slug(d.get("title", f"draft-{idx}"))
        tags = d.get("tags") or []
        sources = d.get("source_urls") or []
        front = [
            "---",
            f"id: {slug}",
            f"platform: {platform}",
            "status: draft",
            f"publish_date: {day.isoformat()}",
            f"title: {json.dumps(d.get('title', slug), ensure_ascii=False)}",
            f"angle: {d.get('angle', '')}",
            "tags:",
            *[f"  - {t}" for t in tags],
            "sources:",
            *[f"  - {u}" for u in sources],
            "---",
            "",
            d.get("body", "").strip(),
            "",
        ]
        path = out_dir / f"{day.isoformat()}-{slug}.md"
        path.write_text("\n".join(front), encoding="utf-8")
        written.append(path)
    return written

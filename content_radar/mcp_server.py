"""MCP tool server — exposes the radar knowledge base to the Claude CLI.

Run via mcp_config.json (the claude CLI launches it as a subprocess):
  {"mcpServers": {"radar": {"command": "python3", "args": ["-m", "content_radar.mcp_server"]}}}

Tools:
  search_news   — hybrid vector+keyword search with date/first_seen filtering
  get_digest    — fetch a specific day's digest markdown
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

from . import config, rag
from .models import normalize_datetime
from .temporal import TemporalIntent, TemporalTier


def _search_news(
    query: str,
    first_seen_from: str = "",
    first_seen_to: str = "",
    limit: int = 15,
    source: str = "",
) -> list[dict]:
    """Search the knowledge base. Use first_seen_from/to to find genuinely new stories."""
    intent = None
    if first_seen_from:
        dt_from = _dt.datetime.fromisoformat(first_seen_from).replace(tzinfo=_dt.timezone.utc)
        dt_to = (
            _dt.datetime.fromisoformat(first_seen_to).replace(tzinfo=_dt.timezone.utc)
            if first_seen_to
            else _dt.datetime.now(_dt.timezone.utc)
        )
        intent = TemporalIntent(tier=TemporalTier.EXPLICIT, date_from=dt_from, date_to=dt_to)

    items = rag.search(query, limit=limit, prefetch=60, per_parent=8,
                       temporal_intent=intent)

    if first_seen_from and intent:
        from .chat import _dedup_by_story
        items = _dedup_by_story(items, first_seen_from)

    if source:
        items = [i for i in items if i.source == source]

    return [
        {
            "title": it.title,
            "url": it.url,
            "source": it.source,
            "created": it.created,
            "first_seen": getattr(it, "first_seen", ""),
            "score": it.score,
            "text": it.text[:800],
        }
        for it in items[:limit]
    ]


def _get_digest(date: str = "") -> str:
    """Fetch a day's digest. Defaults to today."""
    day = _dt.date.fromisoformat(date) if date else _dt.date.today()
    path = config.DIGESTS_DIR / f"digest-{day.isoformat()}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"No digest found for {day.isoformat()}."


TOOLS = {
    "search_news": {
        "fn": _search_news,
        "schema": {
            "name": "search_news",
            "description": (
                "Search the AI news knowledge base. Returns items ranked by relevance. "
                "Use first_seen_from/first_seen_to to find stories first collected on a "
                "specific date — this filters out multi-day trending repeats. "
                "For 'today's news', set first_seen_from to today's date."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords, topic, or question)",
                    },
                    "first_seen_from": {
                        "type": "string",
                        "description": "ISO date (YYYY-MM-DD). Only return items first collected on or after this date.",
                    },
                    "first_seen_to": {
                        "type": "string",
                        "description": "ISO date (YYYY-MM-DD). Only return items first collected on or before this date.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results to return (default 15)",
                        "default": 15,
                    },
                    "source": {
                        "type": "string",
                        "description": "Filter by source: hackernews, gmail, reddit, github, arxiv, x",
                    },
                },
                "required": ["query"],
            },
        },
    },
    "get_digest": {
        "fn": _get_digest,
        "schema": {
            "name": "get_digest",
            "description": "Get the AI news digest for a specific date.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "ISO date (YYYY-MM-DD). Defaults to today.",
                    },
                },
            },
        },
    },
}


def _handle_request(req: dict) -> dict:
    """Handle a JSON-RPC request."""
    method = req.get("method", "")
    rid = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "content-radar", "version": "1.0.0"},
            },
        }

    if method == "notifications/initialized":
        return None  # no response for notifications

    if method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {"tools": [t["schema"] for t in TOOLS.values()]},
        }

    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})
        tool = TOOLS.get(name)
        if not tool:
            return {
                "jsonrpc": "2.0", "id": rid,
                "result": {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True},
            }
        try:
            result = tool["fn"](**args)
            text = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, (list, dict)) else str(result)
            return {
                "jsonrpc": "2.0", "id": rid,
                "result": {"content": [{"type": "text", "text": text}]},
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0", "id": rid,
                "result": {"content": [{"type": "text", "text": f"Error: {exc}"}], "isError": True},
            }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}

    return {
        "jsonrpc": "2.0", "id": rid,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main() -> None:
    """Stdio JSON-RPC loop for the MCP protocol."""
    config.load_env()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = _handle_request(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

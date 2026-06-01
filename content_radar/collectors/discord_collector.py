"""Discord collector via the official Bot REST API (ToS-compliant).

Self-bots (automating a user account) are forbidden and get accounts banned, so
this uses a proper Bot token reading channels the bot has been added to. Disabled
unless DISCORD_BOT_TOKEN is set and `discord_channels` lists channel IDs.

Setup: create a bot at https://discord.com/developers, enable the MESSAGE CONTENT
intent, invite it to servers you're in, and collect the channel IDs to watch.
"""
from __future__ import annotations

import requests

from ..config import Interests, discord_bot_token
from ..models import Item
from .base import warn

API = "https://discord.com/api/v10"
SOURCE = "discord"
TIMEOUT = 20


def _channel_messages(channel_id: str, token: str, limit: int = 50) -> list[dict]:
    resp = requests.get(
        f"{API}/channels/{channel_id}/messages",
        params={"limit": limit},
        headers={"Authorization": f"Bot {token}", "User-Agent": "content-radar/0.1"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def _to_item(msg: dict, channel_id: str) -> Item | None:
    mid = str(msg.get("id") or "")
    content = (msg.get("content") or "").strip()
    if not mid or not content:
        return None
    reactions = sum(r.get("count", 0) for r in msg.get("reactions", []) or [])
    author = (msg.get("author") or {}).get("username", "")
    return Item(
        source=SOURCE,
        id=mid,
        title=content[:120],
        url=f"https://discord.com/channels/@me/{channel_id}/{mid}",
        text=content[:1200],
        score=reactions,
        author=author,
        created=msg.get("timestamp", ""),
        extra={"channel_id": channel_id},
    )


def collect(interests: Interests) -> list[Item]:
    token = discord_bot_token()
    if not token or not interests.discord_channels:
        return []  # disabled until a bot token + channel IDs are configured
    floor = interests.min_score.get(SOURCE, 0)
    out: list[Item] = []
    for channel_id in interests.discord_channels:
        try:
            for msg in _channel_messages(channel_id, token):
                item = _to_item(msg, channel_id)
                if item and item.score >= floor:
                    out.append(item)
        except requests.RequestException as exc:
            warn(SOURCE, exc)
    return out

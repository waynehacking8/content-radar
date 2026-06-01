"""Telegram front-end for the radar chat — DM it questions, get grounded answers.

Long-polling (works behind NAT/firewall; no public webhook needed). Run on any
always-on machine — e.g. your GB10 server:

    TELEGRAM_BOT_TOKEN=... python -m content_radar.telegram_bot

Security: set TELEGRAM_ALLOWED_CHAT_IDS=123,456 so it only answers you. With it
unset the bot replies to anyone who finds it (it always reports the chat id so
you can lock it down). Answers run on your Claude subscription (no API key).
"""
from __future__ import annotations

import os
import time

import requests

from . import config
from .chat import answer

API = "https://api.telegram.org/bot{token}/{method}"
TG_LIMIT = 4000  # Telegram hard limit is 4096


def _call(token: str, method: str, *, poll: int = 0, **params):
    if poll:
        params["timeout"] = poll
    resp = requests.get(API.format(token=token, method=method), params=params,
                        timeout=poll + 10 if poll else 30)
    resp.raise_for_status()
    return resp.json()


def _allowed(chat_id) -> bool:
    ids = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").strip()
    return not ids or str(chat_id) in {x.strip() for x in ids.split(",")}


def _handle(token: str, msg: dict) -> None:
    chat_id = (msg.get("chat") or {}).get("id")
    text = (msg.get("text") or "").strip()
    if not chat_id or not text:
        return
    if not _allowed(chat_id):
        _call(token, "sendMessage", chat_id=chat_id,
              text=f"Not authorized. Your chat id is {chat_id} — add it to "
                   f"TELEGRAM_ALLOWED_CHAT_IDS to enable.")
        return
    if text.startswith("/start") or text.startswith("/help"):
        _call(token, "sendMessage", chat_id=chat_id,
              text=f"Ask me anything about your AI-news radar — e.g. "
                   f"\"what's new with NVIDIA?\" or \"summarize agent safety\".\n"
                   f"(your chat id: {chat_id})")
        return
    _call(token, "sendChatAction", chat_id=chat_id, action="typing")
    try:
        reply = answer(text)
    except Exception as exc:  # noqa: BLE001
        reply = f"Sorry, something went wrong: {exc}"
    _call(token, "sendMessage", chat_id=chat_id, text=reply[:TG_LIMIT])


def _token() -> str:
    config.load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("set TELEGRAM_BOT_TOKEN (create a bot via @BotFather).")
    return token


def poll_once() -> int:
    """Drain and answer all pending messages, then exit. Stateless: Telegram
    holds unconfirmed updates for ~24h, so a cron can call this on a schedule
    without persisting an offset. Returns how many updates were handled.
    """
    token = _token()
    updates = _call(token, "getUpdates", poll=0).get("result", [])
    last = None
    for update in updates:
        last = update["update_id"]
        message = update.get("message") or update.get("edited_message")
        if message:
            try:
                _handle(token, message)
            except Exception as exc:  # noqa: BLE001
                print("handle error:", exc)
    if last is not None:
        _call(token, "getUpdates", offset=last + 1)  # acknowledge the batch
    print(f"handled {len(updates)} update(s)")
    return len(updates)


def run() -> None:
    """Continuous long-polling loop (for an always-on host)."""
    token = _token()
    print("radar telegram bot polling... (Ctrl-C to stop)")
    offset = None
    while True:
        try:
            resp = _call(token, "getUpdates", poll=60, offset=offset)
        except Exception as exc:  # noqa: BLE001
            print("poll error:", exc)
            time.sleep(5)
            continue
        for update in resp.get("result", []):
            offset = update["update_id"] + 1
            message = update.get("message") or update.get("edited_message")
            if message:
                try:
                    _handle(token, message)
                except Exception as exc:  # noqa: BLE001
                    print("handle error:", exc)


if __name__ == "__main__":
    import sys

    if "--once" in sys.argv:
        poll_once()
    else:
        run()

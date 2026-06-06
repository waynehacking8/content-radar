#!/bin/bash
cd /home/richard/content-radar
exec python3 -u << 'PYEOF'
import os, time, traceback, requests
from dotenv import load_dotenv; load_dotenv('.env')

token = os.environ['TELEGRAM_BOT_TOKEN']
API = f"https://api.telegram.org/bot{token}"
allowed = os.environ.get('TELEGRAM_ALLOWED_CHAT_IDS', '').strip()
allowed_set = {x.strip() for x in allowed.split(',')} if allowed else set()

def tg(method, **params):
    r = requests.get(f"{API}/{method}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def tg_post(method, **data):
    requests.post(f"{API}/{method}", data=data, timeout=10)

def kick_ghost():
    """Set then delete webhook to disconnect ghost polling instances."""
    try:
        requests.post(f"{API}/setWebhook", data={"url": "https://example.com:443/x"}, timeout=10)
        time.sleep(2)
        requests.post(f"{API}/deleteWebhook", timeout=10)
        time.sleep(0.5)
    except Exception:
        pass

def handle_message(msg):
    chat_id = (msg.get("chat") or {}).get("id")
    text = (msg.get("text") or "").strip()
    if not chat_id or not text:
        return
    if allowed_set and str(chat_id) not in allowed_set:
        tg("sendMessage", chat_id=chat_id, text=f"Not authorized. chat id: {chat_id}")
        return
    if text.startswith("/start") or text.startswith("/help"):
        tg("sendMessage", chat_id=chat_id, text=f"Ask me about AI news.\n(chat id: {chat_id})")
        return
    tg("sendMessage", chat_id=chat_id, text="⏳ 正在搜尋並整理中...")
    try:
        from content_radar.chat import answer
        reply = answer(text)
    except Exception as exc:
        reply = f"Error: {exc}"
    tg("sendMessage", chat_id=chat_id, text=reply[:4000])

print("radar bot starting (anti-ghost polling)...")
kick_ghost()
consecutive_409 = 0

while True:
    try:
        resp = tg("getUpdates", timeout=5)
        consecutive_409 = 0
        updates = resp.get("result", [])
        last = None
        for update in updates:
            last = update["update_id"]
            msg = update.get("message") or update.get("edited_message")
            if msg:
                try:
                    handle_message(msg)
                except Exception as exc:
                    print(f"handle error: {exc}")
        if last is not None:
            tg("getUpdates", offset=last + 1, timeout=0)
            print(f"handled {len(updates)} update(s)")
    except requests.exceptions.HTTPError as e:
        if "409" in str(e):
            consecutive_409 += 1
            print(f"409 conflict (#{consecutive_409}), kicking ghost...")
            kick_ghost()
            if consecutive_409 > 3:
                time.sleep(5)
        else:
            print(f"HTTP error: {e}")
            time.sleep(5)
    except Exception as exc:
        print(f"poll error: {exc}")
        time.sleep(5)
PYEOF

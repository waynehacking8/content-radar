"""Telegram webhook server — receives updates via HTTP POST instead of polling.

Avoids 409 Conflict from competing polling instances. Telegram pushes updates
to this server; setting a webhook automatically disables getUpdates for all
other instances.

    python -m content_radar.telegram_webhook [--port 8443]
"""
from __future__ import annotations

import json
import os
import ssl
import subprocess
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from . import config
from .chat import answer

TG_API = "https://api.telegram.org/bot{token}/{method}"
TG_LIMIT = 4000


def _call(token: str, method: str, **params):
    import requests
    resp = requests.post(TG_API.format(token=token, method=method), json=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _allowed(chat_id) -> bool:
    ids = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").strip()
    return not ids or str(chat_id) in {x.strip() for x in ids.split(",")}


class WebhookHandler(BaseHTTPRequestHandler):
    token: str = ""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

        try:
            update = json.loads(body)
            msg = update.get("message") or update.get("edited_message")
            if msg:
                self._handle(msg)
        except Exception as exc:
            print(f"handle error: {exc}")

    def _handle(self, msg: dict):
        chat_id = (msg.get("chat") or {}).get("id")
        text = (msg.get("text") or "").strip()
        if not chat_id or not text:
            return
        if not _allowed(chat_id):
            _call(self.token, "sendMessage", chat_id=chat_id,
                  text=f"Not authorized. Your chat id is {chat_id}")
            return
        if text.startswith("/start") or text.startswith("/help"):
            _call(self.token, "sendMessage", chat_id=chat_id,
                  text=f"Ask me anything about AI news.\n(chat id: {chat_id})")
            return
        _call(self.token, "sendChatAction", chat_id=chat_id, action="typing")
        try:
            reply = answer(text)
        except Exception as exc:
            reply = f"Sorry, something went wrong: {exc}"
        _call(self.token, "sendMessage", chat_id=chat_id, text=reply[:TG_LIMIT])

    def log_message(self, format, *args):
        print(f"[webhook] {args[0]}" if args else "")


def _generate_self_signed_cert(cert_path: Path, key_path: Path):
    """Generate a self-signed certificate for Telegram webhook."""
    subprocess.run([
        "openssl", "req", "-newkey", "rsa:2048", "-sha256", "-nodes",
        "-keyout", str(key_path), "-x509", "-days", "365",
        "-out", str(cert_path),
        "-subj", f"/CN={os.environ.get('WEBHOOK_HOST', '0.0.0.0')}",
    ], check=True, capture_output=True)


def run(port: int = 8443):
    config.load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("set TELEGRAM_BOT_TOKEN")

    host = os.environ.get("WEBHOOK_HOST", "")
    if not host:
        import requests as _req
        host = _req.get("https://ifconfig.me", timeout=5).text.strip()
        print(f"Auto-detected public IP: {host}")

    cert_dir = Path(__file__).parent.parent / ".certs"
    cert_dir.mkdir(exist_ok=True)
    cert_path = cert_dir / "webhook.pem"
    key_path = cert_dir / "webhook.key"

    if not cert_path.exists():
        print("Generating self-signed certificate...")
        _generate_self_signed_cert(cert_path, key_path)

    webhook_url = f"https://{host}:{port}/webhook"

    # Set webhook with certificate
    import requests as _req
    with open(cert_path, "rb") as cert_file:
        resp = _req.post(
            TG_API.format(token=token, method="setWebhook"),
            data={"url": webhook_url},
            files={"certificate": cert_file},
            timeout=30,
        )
    result = resp.json()
    if not result.get("ok"):
        raise SystemExit(f"Failed to set webhook: {result}")
    print(f"Webhook set: {webhook_url}")

    WebhookHandler.token = token

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(str(cert_path), str(key_path))

    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    server.socket = ctx.wrap_socket(server.socket, server_side=True)

    print(f"Webhook server listening on 0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up webhook on exit
        _req.post(TG_API.format(token=token, method="deleteWebhook"), timeout=10)
        print("Webhook deleted, server stopped.")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8443
    run(port)

#!/bin/bash
# Run the Telegram chat bot on an always-on host (e.g. the GB10 server).
# All logic lives in the module now (anti-ghost polling + 409 handling there),
# so this is just a launcher. Needs TELEGRAM_BOT_TOKEN in .env.
cd /home/richard/content-radar
exec python3 -u -m content_radar.telegram_bot

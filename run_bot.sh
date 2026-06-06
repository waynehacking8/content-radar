#!/bin/bash
# Non-blocking poll loop — avoids 409 Conflict by not holding a persistent connection.
# Each iteration does a quick getUpdates, processes messages, then sleeps.
cd /home/richard/content-radar
while true; do
    python3 -u -c "
from dotenv import load_dotenv; load_dotenv('.env')
from content_radar.telegram_bot import poll_once
poll_once()
" 2>&1
    sleep 5
done

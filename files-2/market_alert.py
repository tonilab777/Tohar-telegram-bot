"""
Wall Street / Nasdaq trading-hours Telegram notifier.
Runs on a schedule (via GitHub Actions). Each run checks the current time
in New York and, if it matches one of the configured market events
(within TOLERANCE_MINUTES) and hasn't already been sent today, sends a
Telegram message via the official Bot API.

State (which alerts were already sent today) is kept in state.json so the
bot doesn't spam the same alert every time the job runs.
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, date
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")

# Full-closure NYSE/Nasdaq holidays.
# UPDATE THIS LIST EVERY YEAR -> https://www.nyse.com/markets/hours-calendars
MARKET_HOLIDAYS = {
    2026: [
        date(2026, 1, 1),    # New Year's Day
        date(2026, 1, 19),   # MLK Day
        date(2026, 2, 16),   # Presidents Day
        date(2026, 4, 3),    # Good Friday
        date(2026, 5, 25),   # Memorial Day
        date(2026, 6, 19),   # Juneteenth
        date(2026, 7, 3),    # Independence Day (observed)
        date(2026, 9, 7),    # Labor Day
        date(2026, 11, 26),  # Thanksgiving
        date(2026, 12, 25),  # Christmas
    ],
}

# Event times are in America/New_York local time -> DST is handled
# automatically by zoneinfo, no need to touch this when clocks change.
EVENTS = [
    {"key": "premarket_open",   "hour": 4,  "minute": 0,  "label": "🌅 המסחר המוקדם נפתח (Wall Street / Nasdaq)"},
    {"key": "market_open",      "hour": 9,  "minute": 30, "label": "🔔 המסחר הרגיל נפתח (Wall Street / Nasdaq)"},
    {"key": "market_close",     "hour": 16, "minute": 0,  "label": "🔒 המסחר הרגיל נסגר (Wall Street / Nasdaq)"},
    {"key": "afterhours_close", "hour": 20, "minute": 0,  "label": "🌙 המסחר המאוחר נסגר (Wall Street / Nasdaq)"},
]

# Must be >= the cron interval (in minutes) so no event window is missed.
TOLERANCE_MINUTES = 10


def is_trading_day(d: date) -> bool:
    if d.weekday() >= 5:  # Saturday / Sunday
        return False
    return d not in MARKET_HOLIDAYS.get(d.year, [])


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def send_telegram(message: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Telegram response:", resp.status, resp.read().decode(errors="ignore"))


def main() -> None:
    now = datetime.now(ET)
    today_str = now.date().isoformat()
    print(f"Checking at {now.isoformat()}")

    if not is_trading_day(now.date()):
        print("Not a trading day (weekend/holiday) - skipping.")
        return

    state = load_state()
    now_minutes = now.hour * 60 + now.minute

    for ev in EVENTS:
        target_minutes = ev["hour"] * 60 + ev["minute"]
        diff = now_minutes - target_minutes
        already_sent = state.get(ev["key"]) == today_str

        if 0 <= diff <= TOLERANCE_MINUTES and not already_sent:
            print(f"Triggering event: {ev['key']}")
            send_telegram(ev["label"])
            state[ev["key"]] = today_str

    save_state(state)


if __name__ == "__main__":
    main()

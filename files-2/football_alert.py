"""
Beitar Jerusalem match-day Telegram alert.
Runs once a day (via GitHub Actions, scheduled around 08:00 Israel time).
Checks TheSportsDB free API for the team's next scheduled match; if it's
today, sends a Telegram alert with the opponent and kickoff time
(converted to Israel local time, DST-safe).
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

IL = ZoneInfo("Asia/Jerusalem")
UTC = timezone.utc
STATE_FILE = os.path.join(os.path.dirname(__file__), "football_state.json")

TEAM_ID = "135992"     # Beitar Jerusalem on TheSportsDB
TEAM_NAME = "ביתר ירושלים"
API_BASE = "https://www.thesportsdb.com/api/v1/json/123"  # free public test key

# We want one check around 08:00 Israel time. The workflow runs every 30
# min during a UTC window that covers 08:00 in both IST and IDT, so we
# just need a generous tolerance here.
TARGET_HOUR = 8
TARGET_MINUTE = 0
TOLERANCE_MINUTES = 40


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_next_events() -> list:
    url = f"{API_BASE}/eventsnext.php?id={TEAM_ID}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    return data.get("events") or []


def send_telegram(message: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Telegram response:", resp.status, resp.read().decode(errors="ignore"))


def format_kickoff(date_event: str, time_utc_str: str | None) -> str:
    if not time_utc_str:
        return "שעה לא ידועה"
    try:
        h, m, _s = map(int, time_utc_str.split(":"))
        y, mo, d = map(int, date_event.split("-"))
        dt_utc = datetime(y, mo, d, h, m, tzinfo=UTC)
        return dt_utc.astimezone(IL).strftime("%H:%M")
    except Exception as e:
        print("Time parse error:", e)
        return "שעה לא ידועה"


def main() -> None:
    now = datetime.now(IL)
    today_str = now.date().isoformat()
    now_minutes = now.hour * 60 + now.minute
    target_minutes = TARGET_HOUR * 60 + TARGET_MINUTE
    diff = now_minutes - target_minutes

    print(f"Checking at {now.isoformat()}")

    if not (0 <= diff <= TOLERANCE_MINUTES):
        print("Outside today's check window - skipping.")
        return

    state = load_state()
    if state.get("last_checked_date") == today_str:
        print("Already checked today.")
        return

    events = get_next_events()
    todays_match = next((ev for ev in events if ev.get("dateEvent") == today_str), None)

    state["last_checked_date"] = today_str

    if not todays_match:
        print("No Beitar Jerusalem match today.")
        save_state(state)
        return

    home = todays_match.get("strHomeTeam", "?")
    away = todays_match.get("strAwayTeam", "?")
    league = todays_match.get("strLeague", "")
    kickoff = format_kickoff(todays_match.get("dateEvent", today_str), todays_match.get("strTime"))

    message = f"⚽ היום משחק! {home} נגד {away} ({league}) בשעה {kickoff}. בהצלחה {TEAM_NAME}!"
    send_telegram(message)
    save_state(state)


if __name__ == "__main__":
    main()

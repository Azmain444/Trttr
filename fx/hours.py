from __future__ import annotations
from datetime import datetime, timezone, timedelta

# Forex: opens Sunday ~22:00 UTC, closes Friday ~22:00 UTC.
# Closed all Saturday, and Sunday before open.

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def is_market_open(when: datetime | None = None) -> bool:
    dt = when or now_utc()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    wd = dt.weekday()  # Mon=0 … Sun=6
    h = dt.hour + dt.minute / 60.0

    # Saturday — fully closed
    if wd == 5:
        return False
    # Sunday — closed until 22:00 UTC
    if wd == 6:
        return h >= 22.0
    # Friday — closed after 22:00 UTC
    if wd == 4:
        return h < 22.0
    # Mon–Thu — open
    return True

def next_open_utc(when: datetime | None = None) -> datetime:
    dt = when or now_utc()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    # Walk forward hour by hour until open (max 3 days)
    cur = dt.replace(minute=0, second=0, microsecond=0)
    for _ in range(80):
        cur = cur + timedelta(hours=1)
        if is_market_open(cur):
            return cur
    # fallback: next Sunday 22:00
    days = (6 - dt.weekday()) % 7
    if days == 0 and dt.hour >= 22:
        days = 7
    return (dt + timedelta(days=days)).replace(hour=22, minute=0, second=0, microsecond=0)

def market_status() -> dict:
    """Professional status block for UI."""
    dt = now_utc()
    open_now = is_market_open(dt)
    bd = timezone(timedelta(hours=6))  # Bangladesh for owner display
    local = dt.astimezone(bd)

    if open_now:
        # next close = upcoming Friday 22:00 UTC
        days_to_fri = (4 - dt.weekday()) % 7
        close_at = (dt + timedelta(days=days_to_fri)).replace(
            hour=22, minute=0, second=0, microsecond=0
        )
        if dt.weekday() == 4 and dt.hour >= 22:
            close_at = close_at + timedelta(days=7)
        return {
            "open": True,
            "utc": dt.strftime("%a %d %b  %H:%M UTC"),
            "local": local.strftime("%a %d %b  %H:%M BD"),
            "next_event": "Closes",
            "next_time": close_at.strftime("%a %d %b  %H:%M UTC"),
            "next_local": close_at.astimezone(bd).strftime("%a %d %b  %H:%M BD"),
        }

    nxt = next_open_utc(dt)
    return {
        "open": False,
        "utc": dt.strftime("%a %d %b  %H:%M UTC"),
        "local": local.strftime("%a %d %b  %H:%M BD"),
        "next_event": "Opens",
        "next_time": nxt.strftime("%a %d %b  %H:%M UTC"),
        "next_local": nxt.astimezone(bd).strftime("%a %d %b  %H:%M BD"),
    }


def is_market_open_for(symbol: str | None = None) -> bool:
    """Forex/metals follow FX session; crypto is effectively 24/7 (Exness CFDs)."""
    from .constants import is_crypto
    if symbol and is_crypto(symbol):
        return True
    return is_market_open()

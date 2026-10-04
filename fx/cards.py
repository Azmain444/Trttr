from __future__ import annotations
from datetime import datetime, timezone, timedelta
from .fonts import mono, b, code
from .constants import OWNER_USERNAME

BD = timezone(timedelta(hours=6))
W = "═" * 28


def _ts(ts: int) -> str:
    return datetime.fromtimestamp(ts, BD).strftime("%d %b  %H:%M BD")


def _p(v) -> str:
    x = float(v)
    if x >= 1000:
        return f"{x:,.2f}"
    if x >= 10:
        return f"{x:.3f}"
    return f"{x:.5f}"


def _pip_num(v) -> str:
    try:
        n = float(v)
    except (TypeError, ValueError):
        return str(v)
    if n == int(n):
        return str(int(n))
    return f"{n:.1f}"


def signal_card(d: dict) -> str:
    sig = d["signal"]
    up = sig == "BUY"
    badge = "🟢 LIVE BUY" if up else "🔴 LIVE SELL"
    slp = _pip_num(d.get("sl_pips", 0))
    tpp = _pip_num(d.get("tp_pips", 0))
    reason = d.get("reason") or "structure setup"
    structure = d.get("structure") or ""
    rr = d.get("rr", "1:2.2")
    score = d.get("score", "")
    tags = d.get("tags") or []
    tag_line = " · ".join(tags) if tags else ""

    score_line = f"Score  <b>{score}</b>\n" if score != "" else ""
    tags_line = f"<code>{tag_line}</code>\n" if tag_line else ""
    struct_line = f"<i>{structure}</i>\n" if structure else ""

    return (
        f"<b>TRADER</b>  ·  MULTI-SYSTEM 5M\n"
        f"<code>{W}</code>\n"
        f"<b>{d['label']}</b>   ·   5M   ·   {d.get('trend', '—')}\n"
        f"<code>{_ts(d['last_ts'])}</code>\n"
        f"{score_line}"
        f"{tags_line}"
        f"{struct_line}"
        f"<i>{reason}</i>\n"
        f"<code>{W}</code>\n\n"
        f"<b>{badge}</b>\n\n"
        f"🎯  <b>ENTRY</b>\n"
        f"    <code>{_p(d['entry'])}</code>\n\n"
        f"🛑  <b>STOP LOSS</b>\n"
        f"    <code>{_p(d['sl'])}</code>\n"
        f"    <b>−{slp} PIPS</b>\n\n"
        f"💰  <b>TAKE PROFIT</b>\n"
        f"    <code>{_p(d['tp'])}</code>\n"
        f"    <b>+{tpp} PIPS</b>\n\n"
        f"<code>{W}</code>\n"
        f"⚖️  <b>R:R</b>   <code>{rr}</code>\n"
        f"🛡  S  <code>{d.get('support', '—')}</code>\n"
        f"🚧  R  <code>{d.get('resistance', '—')}</code>\n"
        f"<code>{W}</code>\n"
        f"<b>TP or SL — no mid</b>\n"
        f"{OWNER_USERNAME}  ·  Exness"
    )


def tp_card(d: dict) -> str:
    tpp = _pip_num(d.get("tp_pips", 0))
    side = "BUY" if d["signal"] == "BUY" else "SELL"
    return (
        f"<b>💰 TP HIT</b>\n"
        f"<code>{W}</code>\n"
        f"<b>{d['label']}</b>  ·  {side}\n\n"
        f"Entry   <code>{_p(d['entry'])}</code>\n"
        f"TP      <code>{_p(d['tp'])}</code>\n"
        f"<b>+{tpp} PIPS  SECURED</b>\n\n"
        f"✅  <b>Close it. Bank it.</b>\n"
        f"{OWNER_USERNAME}"
    )


def sl_card(d: dict) -> str:
    slp = _pip_num(d.get("sl_pips", 0))
    side = "BUY" if d["signal"] == "BUY" else "SELL"
    return (
        f"<b>🛑 SL HIT</b>\n"
        f"<code>{W}</code>\n"
        f"<b>{d['label']}</b>  ·  {side}\n\n"
        f"Entry   <code>{_p(d['entry'])}</code>\n"
        f"SL      <code>{_p(d['sl'])}</code>\n"
        f"<b>−{slp} PIPS</b>\n\n"
        f"Next setup when structure resets.\n"
        f"{OWNER_USERNAME}"
    )


def hold_card(d: dict) -> str:
    reason = d.get("reason") or "no clean structure"
    structure = d.get("structure") or ""
    return (
        f"<b>TRADER</b>  ·  HOLD\n"
        f"<code>{W}</code>\n"
        f"<b>{d['label']}</b>   ·   5M   ·   {d.get('trend', '—')}\n"
        f"<code>{_ts(d['last_ts'])}</code>\n\n"
        f"<i>{structure}</i>\n"
        f"<i>{reason}</i>\n\n"
        f"No entry. Waiting for BOS + rejection.\n"
        f"<code>{W}</code>\n"
        f"{OWNER_USERNAME}"
    )


def no_signal_card() -> str:
    return (
        f"<b>TRADER</b>  ·  SCAN COMPLETE\n"
        f"<code>{W}</code>\n\n"
        f"No clean BOS + rejection setup\n"
        f"across the scanned pairs.\n\n"
        f"Structure is quiet or mixed.\n"
        f"Try again later or switch to Manual.\n"
        f"<code>{W}</code>\n"
        f"{OWNER_USERNAME}"
    )


def market_closed_card() -> str:
    return (
        f"<b>TRADER</b>  ·  MARKET CLOSED\n"
        f"<code>{W}</code>\n\n"
        f"Forex is offline.\n"
        f"Crypto still available under Manual.\n"
        f"<code>{W}</code>\n"
        f"{OWNER_USERNAME}"
    )

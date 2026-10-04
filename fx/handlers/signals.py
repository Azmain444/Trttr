from __future__ import annotations
import asyncio, logging
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from ..market  import fetch_signal, scan_all
from ..chart   import generate_chart
from ..cards   import (
    signal_card, tp_card, sl_card, hold_card, no_signal_card, market_closed_card,
)
from ..keyboards import (
    auto_menu, manual_cat, majors_grid, crosses_grid, metals_grid, crypto_grid,
    home_btn, back_home, strategy_menu,
)
from ..utils   import reply
from ..constants import ALL_SYM, MAJOR_SYM, CROSS_SYM, METAL_SYM, CRYPTO_SYM, LABEL_MAP
from ..hours   import is_market_open, is_market_open_for, market_status

log = logging.getLogger("TRADER")


def _mode_label(mode: str) -> str:
    return "🕯 STRUCTURE (BOS · CHOCH)"


def strategy_pick_text(which: str) -> str:
    from ..fonts import mono, b
    title = "AUTO SIGNAL" if which == "auto" else "MANUAL SIGNAL"
    st = market_status()
    status_line = (
        f"  Market   :  {b('🟢 OPEN')}"
        if st["open"]
        else f"  Market   :  {b('🌙 CLOSED')}"
    )
    return (
        f"┏{'━'*28}┓\n"
        f"  🕯  {mono('MARKET STRUCTURE')}\n"
        f"┗{'━'*28}┛\n\n"
        f"  Mode     ➤  {b(title)}\n"
        f"{status_line}\n\n"
        f"  HH/HL + BOS → uptrend\n"
        f"  LH/LL + BOS → downtrend\n"
        f"  CHOCH → first sign of weakness\n"
        f"  Pullback + rejection = entry\n\n"
        f"  SL beyond structure · TP 2R+\n\n"
        f"  Tap START 👇"
    )


def auto_mode_text(mode: str = "normal") -> str:
    from ..fonts import mono, b
    st = market_status()
    mkt = "🟢 OPEN" if st["open"] else "🌙 CLOSED"
    return (
        f"┏{'━'*28}┓\n"
        f"  🤖  {mono('AUTO SIGNAL MODE')}\n"
        f"┗{'━'*28}┛\n\n"
        f"  Strategy  :  {b(_mode_label(mode))}\n"
        f"  Timeframe :  {b('5M')}\n"
        f"  Market    :  {b(mkt)}\n"
        f"  Output    :  {b('Text signal + tracker')}\n\n"
        f"  Bot scans selected pairs and returns\n"
        f"  the first confirmed BUY or SELL."
    )


def manual_mode_text(mode: str = "normal") -> str:
    from ..fonts import mono, b
    st = market_status()
    mkt = "🟢 OPEN" if st["open"] else "🌙 CLOSED"
    return (
        f"┏{'━'*28}┓\n"
        f"  ✍️   {mono('MANUAL SIGNAL MODE')}\n"
        f"┗{'━'*28}┛\n\n"
        f"  Strategy  :  {b(_mode_label(mode))}\n"
        f"  Timeframe :  {b('5M')}\n"
        f"  Market    :  {b(mkt)}\n"
        f"  Output    :  {b('Text signal + tracker')}\n\n"
        f"  Choose a category then pick your pair."
    )


def _get_mode(ctx) -> str:
    return ctx.user_data.get("strategy_mode", "normal")


async def _reject_if_closed(u, c, symbol: str | None = None, crypto_ok: bool = False) -> bool:
    if crypto_ok or (symbol and is_market_open_for(symbol)):
        return False
    if is_market_open():
        return False
    await u.callback_query.answer("🌙 Forex market is closed", show_alert=True)
    await reply(u, c, market_closed_card(), home_btn())
    return True


async def _send_signal(update, ctx, data):
    caption = signal_card(data)
    chart = generate_chart(data)
    msg = update.callback_query.message
    if chart:
        sent = await msg.reply_photo(
            photo=chart, caption=caption, parse_mode="HTML", reply_markup=home_btn()
        )
    else:
        sent = await msg.reply_text(
            caption, parse_mode="HTML", reply_markup=home_btn()
        )
    asyncio.create_task(_track(ctx, data, sent.chat_id))


async def _track(ctx, data, chat_id):
    from ..market import fetch_signal as fs
    sym = data["symbol"]
    engine = data["engine"]
    mode = data.get("mode", "normal")
    for _ in range(72):
        await asyncio.sleep(300)
        if not is_market_open():
            continue
        try:
            fresh = await fs(sym, mode=mode)
            last = fresh["candles"][-1] if fresh["candles"] else None
            if not last:
                continue
            result = engine.update(last["high"], last["low"])
            if result == "WIN":
                await ctx.bot.send_message(chat_id, tp_card(data), parse_mode="HTML")
                return
            elif result == "LOSS":
                await ctx.bot.send_message(chat_id, sl_card(data), parse_mode="HTML")
                return
        except Exception:
            continue


# ── strategy pick ─────────────────────────────────────────────────────────────
async def cb_auto(u, c):
    await u.callback_query.answer()
    await reply(u, c, strategy_pick_text("auto"), strategy_menu("auto"))


async def cb_manual(u, c):
    await u.callback_query.answer()
    await reply(u, c, strategy_pick_text("manual"), strategy_menu("manual"))


async def cb_mode(u, c):
    await u.callback_query.answer()
    data = u.callback_query.data
    parts = data.split("_")
    mode = parts[2]
    which = parts[3]
    c.user_data["strategy_mode"] = mode
    if which == "auto":
        await reply(u, c, auto_mode_text(mode), auto_menu())
    else:
        await reply(u, c, manual_mode_text(mode), manual_cat())


# ── AUTO scan ─────────────────────────────────────────────────────────────────
async def _auto_scan(u, c, syms, crypto_ok: bool = False):
    if await _reject_if_closed(u, c, crypto_ok=crypto_ok):
        return
    await u.callback_query.answer()
    mode = _get_mode(c)
    loading = await u.callback_query.message.reply_text(
        f"⚡ <b>TRADER — SCANNING…</b>\n"
        f"Strategy: <b>{_mode_label(mode)}</b>\n"
        f"Pairs: <b>{len(syms)}</b>\n\n"
        f"Preparing…",
        parse_mode="HTML",
    )

    async def progress(i, total, sym):
        label = LABEL_MAP.get(sym, sym)
        try:
            await loading.edit_text(
                f"⚡ <b>TRADER — SCANNING…</b>\n"
                f"Strategy: <b>{_mode_label(mode)}</b>\n\n"
                f"Checking <b>{i}/{total}</b>\n"
                f"Pair ➤ <code>{label}</code>\n\n"
                f"Please wait…",
                parse_mode="HTML",
            )
        except Exception:
            pass

    try:
        data = await scan_all(syms, on_progress=progress, mode=mode)
        try:
            await loading.delete()
        except Exception:
            pass
        if data:
            data["mode"] = mode
            await _send_signal(u, c, data)
        else:
            await u.callback_query.message.reply_text(
                no_signal_card(), parse_mode="HTML", reply_markup=home_btn()
            )
    except Exception as e:
        log.exception("Auto scan error")
        try:
            await loading.edit_text(f"❌ Scan failed: <code>{e}</code>", parse_mode="HTML")
        except Exception:
            pass


async def cb_auto_all(u, c):   await _auto_scan(u, c, ALL_SYM)
async def cb_auto_maj(u, c):   await _auto_scan(u, c, MAJOR_SYM)
async def cb_auto_cross(u, c): await _auto_scan(u, c, CROSS_SYM)
async def cb_auto_metal(u, c): await _auto_scan(u, c, METAL_SYM)
async def cb_auto_crypto(u, c): await _auto_scan(u, c, CRYPTO_SYM, crypto_ok=True)


# ── MANUAL ────────────────────────────────────────────────────────────────────
async def cb_cat_maj(u, c):
    await u.callback_query.answer()
    await reply(u, c, "💼 <b>Select a major pair:</b>", majors_grid())


async def cb_cat_cross(u, c):
    await u.callback_query.answer()
    await reply(u, c, "🔀 <b>Select a cross pair:</b>", crosses_grid())


async def cb_cat_metal(u, c):
    await u.callback_query.answer()
    await reply(u, c, "🥇 <b>Select a metal:</b>", metals_grid())


async def cb_cat_crypto(u, c):
    await u.callback_query.answer()
    await reply(u, c, "₿ <b>Select a crypto pair:</b>", crypto_grid())


async def cb_pair(u, c):
    await u.callback_query.answer()
    mode = _get_mode(c)
    raw = u.callback_query.data[len("fx_p_"):]
    symbol = raw.replace("_", "/", 1)
    if await _reject_if_closed(u, c, symbol=symbol):
        return
    label = LABEL_MAP.get(symbol, symbol)
    loading = await u.callback_query.message.reply_text(
        f"⚡ <b>Scanning {label}…</b>\n"
        f"Strategy: <b>{_mode_label(mode)}</b>\n\n"
        f"Fetching 5M · Running structure engine…",
        parse_mode="HTML",
    )
    try:
        data = await fetch_signal(symbol, mode=mode)
        data["mode"] = mode
        try:
            await loading.delete()
        except Exception:
            pass
        if data["signal"] in ("BUY", "SELL"):
            await _send_signal(u, c, data)
        else:
            await u.callback_query.message.reply_text(
                hold_card(data),
                parse_mode="HTML",
                reply_markup=back_home("fx_manual"),
            )
    except Exception as e:
        log.exception("Manual scan error for %s", symbol)
        try:
            await loading.edit_text(f"❌ Failed: <code>{e}</code>", parse_mode="HTML")
        except Exception:
            pass


handlers = [
    CallbackQueryHandler(cb_auto,        pattern="^fx_auto$"),
    CallbackQueryHandler(cb_manual,      pattern="^fx_manual$"),
    CallbackQueryHandler(cb_mode,        pattern="^fx_mode_(strict|normal)_(auto|manual)$"),
    CallbackQueryHandler(cb_auto_all,    pattern="^fx_auto_all$"),
    CallbackQueryHandler(cb_auto_maj,    pattern="^fx_auto_majors$"),
    CallbackQueryHandler(cb_auto_cross,  pattern="^fx_auto_crosses$"),
    CallbackQueryHandler(cb_auto_metal,  pattern="^fx_auto_metals$"),
    CallbackQueryHandler(cb_auto_crypto, pattern="^fx_auto_crypto$"),
    CallbackQueryHandler(cb_cat_maj,     pattern="^fx_cat_maj$"),
    CallbackQueryHandler(cb_cat_cross,   pattern="^fx_cat_cross$"),
    CallbackQueryHandler(cb_cat_metal,   pattern="^fx_cat_metal$"),
    CallbackQueryHandler(cb_cat_crypto,  pattern="^fx_cat_crypto$"),
    CallbackQueryHandler(cb_pair,        pattern="^fx_p_"),
]

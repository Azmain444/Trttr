from __future__ import annotations
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from ..db import is_admin, is_authorized, is_banned, get_user
from ..text import profile
from ..keyboards import back_home
from ..utils import reply

async def cb_profile(u, c):
    await u.callback_query.answer()
    user   = u.effective_user
    uid    = str(user.id)
    uname  = f"@{user.username}" if user.username else user.first_name or "—"
    record = get_user(uid) or {}
    since  = record.get("member_since","—")
    try: since = datetime.fromisoformat(since).strftime("%Y-%m-%d") if since != "—" else "—"
    except: pass
    if is_admin(uid):
        status, plan, expires = "🟢 OWNER", "Lifetime", "Never"
    elif is_banned(uid):
        status, plan, expires = "🚫 BANNED", "—", "—"
    elif is_authorized(uid):
        exp = record.get("expires_at")
        try: expires = datetime.fromisoformat(exp).strftime("%Y-%m-%d %H:%M UTC") if exp else "Lifetime"
        except: expires = exp or "Lifetime"
        plan = record.get("source","key").upper(); status = "✅ ACTIVE"
    else:
        status, plan, expires = "🔒 NO LICENSE", "—", "—"
    await reply(u, c, profile(uid, uname, since, status, plan, expires), back_home("fx_home"))

handlers = [CallbackQueryHandler(cb_profile, pattern="^fx_profile$")]

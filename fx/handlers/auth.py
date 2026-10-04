from __future__ import annotations
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from ..db import (
    is_admin, is_authorized, is_banned,
    authorize, unauthorize, ban_user, unban_user,
    generate_key, delete_key, redeem_key,
    get_user, get_all_users, get_all_keys, get_stats, parse_duration
)
from ..constants import OWNER_USERNAME, ADMIN_ID
from ..fonts import b, bi, code, mono
from ..text import welcome, buy_msg, help_msg, admin_panel
from ..keyboards import main_menu, buy_menu, home_btn

def _uid(s): return s.lstrip("@").strip()

async def cmd_start(u: Update, c):
    name = u.effective_user.first_name or u.effective_user.username or "Trader"
    uid = u.effective_user.id
    ok = is_admin(uid) or is_authorized(uid)
    await u.message.reply_text(
        welcome(name, licensed=ok), parse_mode="HTML", reply_markup=main_menu(licensed=ok)
    )

async def cmd_buy(u: Update, c):
    await u.message.reply_text(buy_msg(), parse_mode="HTML", reply_markup=buy_menu())

async def cmd_help(u: Update, c):
    owner = is_admin(u.effective_user.id)
    await u.message.reply_text(
        help_msg(is_owner=owner), parse_mode="HTML", reply_markup=home_btn()
    )

async def cmd_license(u: Update, c):
    uid = str(u.effective_user.id)
    if is_admin(uid):
        txt = f"┏{'━'*26}┓\n  👑  {mono('OWNER LICENSE')}\n┗{'━'*26}┛\n\n  Status  ➤  🟢 OWNER UNLIMITED\n  Expires ➤  Never\n"
    else:
        r = get_user(uid) or {}
        if is_authorized(uid):
            exp = r.get("expires_at") or "Lifetime"
            try: exp = datetime.fromisoformat(exp).strftime("%Y-%m-%d %H:%M UTC")
            except: pass
            txt = f"┏{'━'*26}┓\n  ✅  {mono('LICENSE ACTIVE')}\n┗{'━'*26}┛\n\n  Status  ➤  🟢 ACTIVE\n  Expires ➤  {exp}\n  Plan    ➤  {r.get('source','key').upper()}\n"
        elif is_banned(uid):
            txt = f"🚫 {b('YOU ARE BANNED')}\n\nContact {OWNER_USERNAME} to appeal."
        else:
            txt = f"┏{'━'*26}┓\n  🔒  {mono('NO LICENSE')}\n┗{'━'*26}┛\n\n  Get a key from {OWNER_USERNAME}\n  Then: {code('/redeem YOUR_KEY')}"
    await u.message.reply_text(txt, parse_mode="HTML")

async def cmd_redeem(u: Update, c):
    if len(c.args) != 1:
        await u.message.reply_text(
            f"🔐 {b('Redeem License')}\n\nUsage: {code('/redeem YOUR_KEY')}\n\nNo key? {OWNER_USERNAME}",
            parse_mode="HTML"); return
    uid = str(u.effective_user.id)
    uname = f"@{u.effective_user.username}" if u.effective_user.username else ""
    ok, msg = redeem_key(c.args[0], uid, uname)
    if ok:
        text = (f"┏{'━'*26}┓\n  ✅  {mono('LICENSE ACTIVATED')}\n┗{'━'*26}┛\n\n"
                f"  Key     ➤  {code(c.args[0].upper())}\n"
                f"  Expires ➤  {msg}\n\n  👑 Support : {OWNER_USERNAME}")
    else:
        text = msg
    await u.message.reply_text(text, parse_mode="HTML")

# ── ADMIN ──────────────────────────────────────────────────────────────────
async def cmd_admin(u: Update, c):
    if not is_admin(u.effective_user.id): await u.message.reply_text("❌ Admin only."); return
    await u.message.reply_text(admin_panel(get_stats()), parse_mode="HTML")

async def cmd_auth(u: Update, c):
    if not is_admin(u.effective_user.id): await u.message.reply_text("❌ Admin only."); return
    if not c.args: await u.message.reply_text("Usage: /auth USER_ID [30d]"); return
    uid = _uid(c.args[0])
    exp = parse_duration(c.args[1]) if len(c.args) > 1 else None
    if len(c.args) > 1 and exp is None: await u.message.reply_text("❌ Bad duration. Try: 1d 7d 30d 1month"); return
    authorize(uid, c.args[0], exp, "admin")
    dur = f" · expires {c.args[1]}" if len(c.args) > 1 else " · permanent"
    await u.message.reply_text(f"✅ Authorized {code(uid)}{dur}", parse_mode="HTML")

async def cmd_unauth(u: Update, c):
    if not is_admin(u.effective_user.id): await u.message.reply_text("❌ Admin only."); return
    if len(c.args) != 1: await u.message.reply_text("Usage: /unauth USER_ID"); return
    uid = _uid(c.args[0])
    ok = unauthorize(uid)
    await u.message.reply_text(("🚫 Revoked " if ok else "⚠️ Not found ") + code(uid), parse_mode="HTML")

async def cmd_ban(u: Update, c):
    if not is_admin(u.effective_user.id): await u.message.reply_text("❌ Admin only."); return
    if len(c.args) < 1: await u.message.reply_text("Usage: /ban USER_ID"); return
    uid = _uid(c.args[0])
    if str(uid) == str(ADMIN_ID): await u.message.reply_text("❌ Cannot ban yourself."); return
    ban_user(uid)
    await u.message.reply_text(f"🚫 {b('BANNED')} — {code(uid)}\n\nBlocked from all bot features.", parse_mode="HTML")

async def cmd_unban(u: Update, c):
    if not is_admin(u.effective_user.id): await u.message.reply_text("❌ Admin only."); return
    if len(c.args) != 1: await u.message.reply_text("Usage: /unban USER_ID"); return
    uid = _uid(c.args[0])
    ok = unban_user(uid)
    await u.message.reply_text((f"✅ {b('UNBANNED')} — {code(uid)}" if ok else f"⚠️ User not found: {code(uid)}"), parse_mode="HTML")

async def cmd_userlist(u: Update, c):
    if not is_admin(u.effective_user.id): await u.message.reply_text("❌ Admin only."); return
    users = get_all_users()
    if not users: await u.message.reply_text("👥 No users yet."); return
    lines = [f"┏{'━'*26}┓\n  👥  {b('USER LIST')}\n┗{'━'*26}┛\n"]
    for uid, v in users.items():
        uname = v.get("username") or "—"
        banned = v.get("banned", False)
        exp = v.get("expires_at","")
        try: exp_str = datetime.fromisoformat(exp).strftime("%Y-%m-%d") if exp else "lifetime"
        except: exp_str = "—"
        if banned: st = "🚫 BANNED"
        elif is_authorized(uid): st = f"✅ ACTIVE · {exp_str}"
        else: st = "🔒 NO LICENSE"
        lines.append(f"▸ {code(uid)}  {uname}\n  └ {st}")
    chunk = ""; chunks = []
    for ln in lines:
        if len(chunk)+len(ln)+1 > 3800: chunks.append(chunk); chunk = ""
        chunk += ln + "\n"
    if chunk: chunks.append(chunk)
    for p in chunks: await u.message.reply_text(p, parse_mode="HTML")

async def cmd_genkey(u: Update, c):
    if not is_admin(u.effective_user.id): await u.message.reply_text("❌ Admin only."); return
    if len(c.args) == 1: duration, name = c.args[0], None
    elif len(c.args) == 2: name, duration = c.args[0], c.args[1]
    else: await u.message.reply_text(f"Usage:\n{code('/genkey 30d')}\n{code('/genkey MYKEY 30d')}", parse_mode="HTML"); return
    res = generate_key(duration, name)
    if res is None: await u.message.reply_text("❌ Invalid duration or key exists. Try: 1d 7d 30d 1month 1year"); return
    key, _ = res
    await u.message.reply_text(
        f"┏{'━'*26}┓\n  🔑  {b('KEY CREATED')}\n┗{'━'*26}┛\n\n"
        f"  Key    ➤  {code(key)}\n  Plan   ➤  {b(duration)}\n  Status ➤  🟢 UNUSED\n\n"
        f"  ⚡ Timer starts on redeem.\n  👑 Sell via : {OWNER_USERNAME}",
        parse_mode="HTML")

async def cmd_delkey(u: Update, c):
    if not is_admin(u.effective_user.id): await u.message.reply_text("❌ Admin only."); return
    if len(c.args) != 1:
        await u.message.reply_text(f"Usage: {code('/delkey KEY')}\n\nOnly destroys {b('unredeemed')} keys.", parse_mode="HTML"); return
    key = c.args[0].strip().upper()
    ok, reason = delete_key(key)
    if ok:
        await u.message.reply_text(f"🗑 {b('KEY DESTROYED')}\n\n{code(key)}\n\nPermanently deleted.", parse_mode="HTML")
    elif reason == "already_redeemed":
        await u.message.reply_text(
            f"❌ {b('Cannot delete redeemed key.')}\n\n{code(key)} is in use.\n"
            f"Use {code('/unauth USER_ID')} to revoke their access instead.", parse_mode="HTML")
    else:
        await u.message.reply_text(f"❌ Key not found: {code(key)}", parse_mode="HTML")

async def cmd_keylist(u: Update, c):
    if not is_admin(u.effective_user.id): await u.message.reply_text("❌ Admin only."); return
    keys = get_all_keys()
    if not keys: await u.message.reply_text("🔑 No keys yet."); return
    lines = [f"┏{'━'*26}┓\n  🔑  {b('KEY LIST')}\n┗{'━'*26}┛\n"]
    for key, v in keys.items():
        plan = v.get("duration","?")
        red  = v.get("redeemed_by")
        if red:
            uname = v.get("redeemed_username") or red
            exp   = v.get("expires_at","")
            try: exp_str = datetime.fromisoformat(exp).strftime("%Y-%m-%d") if exp else "—"
            except: exp_str = "—"
            st = f"♻️  USED · {uname} · exp {exp_str}"
        else:
            st = "🟢 UNUSED"
        lines.append(f"▸ {code(key)}\n  └ {plan}  ·  {st}")
    chunk = ""; chunks = []
    for ln in lines:
        if len(chunk)+len(ln)+1 > 3800: chunks.append(chunk); chunk = ""
        chunk += ln + "\n"
    if chunk: chunks.append(chunk)
    for p in chunks: await u.message.reply_text(p, parse_mode="HTML")

handlers = [
    CommandHandler("start",    cmd_start),
    CommandHandler("buy",      cmd_buy),
    CommandHandler("help",     cmd_help),
    CommandHandler("license",  cmd_license),
    CommandHandler("redeem",   cmd_redeem),
    CommandHandler("admin",    cmd_admin),
    CommandHandler("auth",     cmd_auth),
    CommandHandler("unauth",   cmd_unauth),
    CommandHandler("ban",      cmd_ban),
    CommandHandler("unban",    cmd_unban),
    CommandHandler("userlist", cmd_userlist),
    CommandHandler("genkey",   cmd_genkey),
    CommandHandler("delkey",   cmd_delkey),
    CommandHandler("keylist",  cmd_keylist),
]

from __future__ import annotations
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from ..text import welcome, about, help_msg, buy_msg
from ..keyboards import main_menu, home_btn, buy_menu
from ..utils import reply
from ..db import is_admin, is_authorized

async def cb_home(u, c):
    await u.callback_query.answer()
    uid = u.effective_user.id
    name = u.effective_user.first_name or "Trader"
    ok = is_admin(uid) or is_authorized(uid)
    await reply(u, c, welcome(name, licensed=ok), main_menu(licensed=ok))

async def cb_about(u, c):
    await u.callback_query.answer()
    await reply(u, c, about(), home_btn())

async def cb_help(u, c):
    await u.callback_query.answer()
    owner = is_admin(u.effective_user.id)
    await reply(u, c, help_msg(is_owner=owner), home_btn())

async def cb_buy(u, c):
    await u.callback_query.answer()
    await reply(u, c, buy_msg(), buy_menu())

handlers = [
    CallbackQueryHandler(cb_home,  pattern="^fx_home$"),
    CallbackQueryHandler(cb_about, pattern="^fx_about$"),
    CallbackQueryHandler(cb_help,  pattern="^fx_help$"),
    CallbackQueryHandler(cb_buy,   pattern="^fx_buy$"),
]

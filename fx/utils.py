from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes

async def reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE,
                text: str, markup=None, parse_mode="HTML") -> None:
    q = update.callback_query
    if q:
        try:
            await q.edit_message_text(text, parse_mode=parse_mode, reply_markup=markup)
            return
        except Exception:
            pass
        try:
            await q.message.reply_text(text, parse_mode=parse_mode, reply_markup=markup)
        except Exception:
            pass
    elif update.message:
        await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=markup)

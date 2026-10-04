from __future__ import annotations
import logging, os, warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

from telegram.ext import Application, CallbackQueryHandler, ApplicationHandlerStop
from telegram.error import NetworkError

from fx.handlers import auth_handlers, menu_handlers, profile_handlers, signal_handlers
from fx import is_authorized, is_banned

_PUBLIC = ("fx_home", "fx_about", "fx_help", "fx_buy", "fx_profile")


async def _gate(update, context):
    q = update.callback_query
    if not q:
        return
    data = q.data or ""
    if any(data.startswith(p) for p in _PUBLIC):
        return
    uid = update.effective_user.id
    if is_banned(uid):
        await q.answer("🚫 You are banned. Contact the owner.", show_alert=True)
        raise ApplicationHandlerStop
    if not is_authorized(uid):
        await q.answer("🔒 License required. Buy a key or /redeem KEY — signals are not free.", show_alert=True)
        raise ApplicationHandlerStop


async def _on_error(update, context):
    if isinstance(context.error, NetworkError):
        return
    logging.getLogger(__name__).error("Error", exc_info=context.error)


def main():
    logging.basicConfig(
        format="%(asctime)s  %(name)-18s  %(levelname)s  %(message)s",
        level=logging.INFO,
    )
    for ns in ("httpx", "httpcore", "telegram.ext._utils.networkloop",
               "telegram.ext._application"):
        logging.getLogger(ns).setLevel(logging.WARNING)

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("❌  BOT_TOKEN missing in .env")

    app = (
        Application.builder().token(token)
        .get_updates_read_timeout(30)
        .get_updates_write_timeout(30)
        .get_updates_connect_timeout(30)
        .build()
    )

    for h in auth_handlers:
        app.add_handler(h)
    app.add_handler(CallbackQueryHandler(_gate, block=True), group=-100)
    for h in menu_handlers:
        app.add_handler(h)
    for h in profile_handlers:
        app.add_handler(h)
    for h in signal_handlers:
        app.add_handler(h)
    app.add_error_handler(_on_error)

    print(
        "\n"
        "  ⚡  TRADER  ·  STRUCTURE ENGINE  V3.0\n"
        "  ──────────────────────────────────\n"
        "  Strategy  :  BOS + CHOCH + Market Structure\n"
        "  Data      :  Twelve Data  (5M)\n"
        "  Output    :  Text signals + auto tracker\n"
        "  Auth      :  Key system + ban\n"
        "  ──────────────────────────────────\n"
        "  Running. Ctrl+C to stop.\n"
    )

    app.run_polling(
        allowed_updates=["callback_query", "message"],
        drop_pending_updates=True,
        bootstrap_retries=-1,
    )


if __name__ == "__main__":
    main()

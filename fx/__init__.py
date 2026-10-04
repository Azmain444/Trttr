"""
fx — TRADER Structure Engine package.
Exposes every public symbol so handlers only need:
    from .. import is_authorized, signal_card, ...
"""
# ── database / auth ──────────────────────────────────────────────────────────
from .db import (
    is_admin, is_authorized, is_banned,
    authorize, unauthorize, ban_user, unban_user,
    generate_key, delete_key, redeem_key,
    get_user, get_all_users, get_all_keys, get_stats,
    parse_duration, ADMIN_ID,
)

# ── constants ────────────────────────────────────────────────────────────────
from .constants import (
    OWNER_USERNAME, OWNER_URL,
    ALL_SYM, MAJOR_SYM, CROSS_SYM, METAL_SYM, CRYPTO_SYM,
    PIP_MAP, LABEL_MAP,
)

# ── font / html helpers ──────────────────────────────────────────────────────
from .fonts import mono, b, i, bi, code

# ── strategy ─────────────────────────────────────────────────────────────────
from .strategy import TraderStructure

# ── market data ──────────────────────────────────────────────────────────────
from .market import fetch_signal, scan_all

# ── chart generator ──────────────────────────────────────────────────────────
from .chart import generate_chart

# ── message cards ────────────────────────────────────────────────────────────
from .cards import (
    signal_card, tp_card, sl_card, hold_card, no_signal_card, market_closed_card,
)

# ── message text ─────────────────────────────────────────────────────────────
from .text import (
    welcome, about, help_msg, buy_msg, profile, admin_panel,
)

# ── keyboards ────────────────────────────────────────────────────────────────
from .keyboards import (
    main_menu, home_btn, back_home, buy_menu, locked_menu,
    auto_menu, manual_cat, strategy_menu,
    majors_grid, crosses_grid, metals_grid, crypto_grid,
)

# ── utils ────────────────────────────────────────────────────────────────────
from .utils import reply

__all__ = [
    # auth
    "is_admin","is_authorized","is_banned",
    "authorize","unauthorize","ban_user","unban_user",
    "generate_key","delete_key","redeem_key",
    "get_user","get_all_users","get_all_keys","get_stats",
    "parse_duration","ADMIN_ID",
    # constants
    "OWNER_USERNAME","OWNER_URL",
    "ALL_SYM","MAJOR_SYM","CROSS_SYM","METAL_SYM","CRYPTO_SYM",
    "PIP_MAP","LABEL_MAP",
    # fonts
    "mono","b","i","bi","code",
    # core
    "TraderStructure","fetch_signal","scan_all",
    "generate_chart",
    # cards
    "signal_card","tp_card","sl_card","hold_card","no_signal_card","market_closed_card",
    # text
    "welcome","about","help_msg","buy_msg","profile","admin_panel",
    # keyboards
    "main_menu","home_btn","back_home","buy_menu","locked_menu",
    "auto_menu","manual_cat","strategy_menu",
    "majors_grid","crosses_grid","metals_grid","crypto_grid",
    # utils
    "reply",
]

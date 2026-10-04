from __future__ import annotations
from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as K
from .constants import OWNER_URL, MAJOR_SYM, CROSS_SYM, METAL_SYM, CRYPTO_SYM


def _k(*rows):
    return K(list(rows))


def _b(txt, cb=None, url=None):
    return B(txt, callback_data=cb) if cb else B(txt, url=url)


def main_menu(licensed: bool = True):
    if licensed:
        return _k(
            [_b("⚡  AUTO SIGNAL", "fx_auto"), _b("🎯  MANUAL", "fx_manual")],
            [_b("👤  PROFILE", "fx_profile"), _b("✦  ABOUT", "fx_about")],
            [_b("🛡  HELP", "fx_help"), _b("💎  GET KEY", "fx_buy")],
        )
    return _k(
        [_b("💎  GET KEY", "fx_buy"), _b("🔐  /redeem KEY", "fx_home")],
        [_b("👤  PROFILE", "fx_profile"), _b("✦  ABOUT", "fx_about")],
        [_b("🛡  HELP", "fx_help")],
    )


def home_btn():
    return _k([_b("⌂  HOME", "fx_home")])


def back_home(cb: str):
    return _k([_b("◀  BACK", cb), _b("⌂  HOME", "fx_home")])


def buy_menu():
    return _k(
        [_b("💬  Message Owner", url=OWNER_URL)],
        [_b("⌂  HOME", "fx_home")],
    )


def locked_menu():
    return _k(
        [_b("💎  Buy Key", url=OWNER_URL)],
        [_b("🔐  /redeem KEY", "fx_home")],
    )


def strategy_menu(next_action: str):
    return _k(
        [_b("🕯  STRUCTURE  ·  START", f"fx_mode_normal_{next_action}")],
        [_b("⌂  HOME", "fx_home")],
    )


def auto_menu():
    return _k(
        [_b("🌐  ALL EXNESS", "fx_auto_all")],
        [_b("💵  MAJORS", "fx_auto_majors"), _b("🔀  CROSSES", "fx_auto_crosses")],
        [_b("🥇  METALS", "fx_auto_metals"), _b("₿  CRYPTO", "fx_auto_crypto")],
        [_b("◀  Strategy", "fx_auto"), _b("⌂  HOME", "fx_home")],
    )


def manual_cat():
    return _k(
        [_b("💵  Forex Majors", "fx_cat_maj")],
        [_b("🔀  Forex Crosses", "fx_cat_cross")],
        [_b("🥇  Metals (XAU XAG…)", "fx_cat_metal")],
        [_b("₿  Crypto (BTC ETH…)", "fx_cat_crypto")],
        [_b("◀  Strategy", "fx_manual"), _b("⌂  HOME", "fx_home")],
    )


def _grid(syms, prefix):
    rows = []
    for i in range(0, len(syms), 2):
        row = [_b(syms[i], f"{prefix}{syms[i].replace('/', '_')}")]
        if i + 1 < len(syms):
            row.append(_b(syms[i + 1], f"{prefix}{syms[i + 1].replace('/', '_')}"))
        rows.append(row)
    rows.append([_b("◀  BACK", "fx_manual"), _b("⌂  HOME", "fx_home")])
    return K(rows)


def majors_grid():
    return _grid(MAJOR_SYM, "fx_p_")


def crosses_grid():
    return _grid(CROSS_SYM, "fx_p_")


def metals_grid():
    return _grid(METAL_SYM, "fx_p_")


def crypto_grid():
    return _grid(CRYPTO_SYM, "fx_p_")

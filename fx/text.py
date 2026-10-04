from __future__ import annotations
from datetime import datetime
from .fonts import b, i, bi, code, mono
from .constants import OWNER_USERNAME, OWNER_URL, ADMIN_ID


def welcome(name: str, licensed: bool = False) -> str:
    body = (
        f"{bi('TRADER  ·  STRUCTURE ENGINE')}\n\n"
        f"Welcome, {b(name)}.\n\n"
        f"5M signals built on pure market structure:\n"
        f"{b('BOS')} · {b('CHOCH')} · Higher Highs / Lower Lows\n\n"
        f"Exness markets · Forex · Metals · Crypto\n\n"
        f"{b('ENTRY')} · {b('SL')} · {b('TP')}\n\n"
    )
    if licensed:
        body += "Choose AUTO or MANUAL — clean structure only."
    else:
        body += (
            f"🔒 {b('License required')} — signals are not free.\n"
            f"Get a key → {code('/redeem YOUR_KEY')}\n\n"
            f"Owner: {OWNER_USERNAME}"
        )
    return body


def about() -> str:
    return (
        f"┏{'━'*28}┓\n"
        f"  {mono('TRADER  ·  V3.0')}\n"
        f"┗{'━'*28}┛\n\n"
        f"  {b('Strategy')}   :  Market Structure\n"
        f"  {b('Core')}       :  BOS + CHOCH + HH/HL\n"
        f"  {b('Timeframe')}  :  5M\n"
        f"  {b('Data')}       :  Twelve Data\n"
        f"  {b('Output')}     :  Text signals + tracker\n"
        f"  {b('Tracker')}    :  Auto TP / SL alerts\n\n"
        f"{'┄'*30}\n\n"
        f"  Detects confirmed Break of Structure\n"
        f"  and Change of Character.\n"
        f"  Pullback + rejection = entry.\n\n"
        f"{'┄'*30}\n\n"
        f"  {b('Owner')}  :  {OWNER_USERNAME}\n"
        f"┗{'━'*28}┛"
    )


def help_msg(is_owner: bool = False) -> str:
    user = (
        f"┏{'━'*28}┓\n"
        f"  {mono('TRADER  ·  HELP')}\n"
        f"┗{'━'*28}┛\n\n"
        f"  {b('For members')}\n"
        f"  {b('Auto Signal')}   — scan markets, first clean hit\n"
        f"  {b('Manual Signal')} — pick pair, full analysis\n"
        f"  {b('My Profile')}    — license status\n\n"
        f"{'┄'*30}\n\n"
        f"  {b('License')}\n"
        f"  {code('/redeem KEY')}   activate key\n"
        f"  {code('/buy')}          get a key\n"
        f"  {code('/license')}      check status\n\n"
        f"  🔒 Signals need an active license.\n"
        f"  Support: {OWNER_USERNAME}\n"
        f"┗{'━'*28}┛"
    )
    if not is_owner:
        return user
    owner = (
        f"\n\n"
        f"┏{'━'*28}┓\n"
        f"  {mono('OWNER CONTROL')}\n"
        f"┗{'━'*28}┛\n\n"
        f"  Only you can see this section.\n\n"
        f"  {b('Keys')}\n"
        f"  {code('/genkey 30d')}\n"
        f"      generate key (1d 7d 30d 90d 1y)\n"
        f"  {code('/genkey VIP 30d')}\n"
        f"      custom key name + duration\n"
        f"  {code('/delkey KEY')}\n"
        f"      delete unused key\n"
        f"  {code('/keylist')}\n"
        f"      list all keys\n\n"
        f"  {b('Users')}\n"
        f"  {code('/auth USER_ID 30d')}\n"
        f"      grant access (optional duration)\n"
        f"  {code('/unauth USER_ID')}\n"
        f"      revoke access\n"
        f"  {code('/ban USER_ID')}\n"
        f"      ban user\n"
        f"  {code('/unban USER_ID')}\n"
        f"      unban user\n"
        f"  {code('/userlist')}\n"
        f"      list all users\n\n"
        f"  {b('Panel')}\n"
        f"  {code('/admin')}\n"
        f"      stats + command summary\n\n"
        f"  Members without a key cannot\n"
        f"  open Auto or Manual signals.\n"
        f"┗{'━'*28}┛"
    )
    return user + owner


def buy_msg() -> str:
    return (
        f"┏{'━'*28}┓\n"
        f"  {mono('TRADER  ·  LICENSE')}\n"
        f"┗{'━'*28}┛\n\n"
        f"  Access is license-gated.\n"
        f"  Message the owner for a key.\n\n"
        f"  {b('Owner')}  :  {OWNER_USERNAME}\n"
        f"  After payment → {code('/redeem KEY')}\n\n"
        f"┗{'━'*28}┛"
    )


def profile_msg(name: str, uid: int, licensed: bool, expires: str | None = None) -> str:
    status = f"{b('ACTIVE')}" if licensed else f"{b('LOCKED')}"
    exp = f"\n  Expires  :  {expires}" if expires else ""
    return (
        f"┏{'━'*28}┓\n"
        f"  {mono('PROFILE')}\n"
        f"┗{'━'*28}┛\n\n"
        f"  Name     :  {name}\n"
        f"  ID       :  {code(str(uid))}\n"
        f"  License  :  {status}{exp}\n\n"
        f"┗{'━'*28}┛"
    )


def profile(uid, uname, since, status, plan, expires) -> str:
    return (
        f"┏{'━'*28}┓\n"
        f"  👤  {mono('YOUR PROFILE')}\n"
        f"┗{'━'*28}┛\n\n"
        f"  {mono('ID')}           ➤  {code(uid)}\n"
        f"  {mono('Username')}     ➤  {mono(uname)}\n"
        f"  {mono('Member Since')} ➤  {mono(since)}\n\n"
        f"{'┄'*30}\n\n"
        f"  {mono('License')}      ➤  {status}\n"
        f"  {mono('Plan')}         ➤  {mono(plan)}\n"
        f"  {mono('Valid Until')}  ➤  {mono(expires)}\n\n"
        f"{'┄'*30}\n\n"
        f"  {b('Buy / Renew')} :  {OWNER_USERNAME}\n"
        f"┗{'━'*28}┛"
    )


def admin_panel(s: dict) -> str:
    return (
        f"┏{'━'*28}┓\n"
        f"  👑  {mono('TRADER ADMIN PANEL')}\n"
        f"┗{'━'*28}┛\n\n"
        f"  Owner       :  {OWNER_USERNAME}\n"
        f"  Admin ID    :  {code(str(ADMIN_ID))}\n\n"
        f"{'┄'*30}\n\n"
        f"  👥 Users      :  {b(str(s['users']))}\n"
        f"  ✅ Active      :  {b(str(s['active']))}\n"
        f"  🚫 Banned      :  {b(str(s['banned']))}\n\n"
        f"  🔑 Keys total  :  {b(str(s['keys']))}\n"
        f"  🟢 Unused      :  {b(str(s['unused']))}\n"
        f"  ♻️  Redeemed    :  {b(str(s['redeemed']))}\n\n"
        f"{'┄'*30}\n\n"
        f"  {b('Commands')}\n"
        f"  {code('/genkey 30d')}         generate key\n"
        f"  {code('/genkey NAME 30d')}    custom key name\n"
        f"  {code('/delkey KEY')}         destroy unused key\n"
        f"  {code('/keylist')}            all keys\n"
        f"  {code('/auth ID 30d')}        manual authorize\n"
        f"  {code('/unauth ID')}          revoke access\n"
        f"  {code('/ban ID')}             ban user\n"
        f"  {code('/unban ID')}           unban user\n"
        f"  {code('/userlist')}           all users\n"
        f"┗{'━'*28}┛"
    )

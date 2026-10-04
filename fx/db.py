from __future__ import annotations
import json, re, secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from .constants import ADMIN_ID, DB_PATH

def _now(): return datetime.now(timezone.utc)

def _load() -> dict:
    if not DB_PATH.exists():
        return {"users": {}, "keys": {}}
    try:
        d = json.loads(DB_PATH.read_text("utf-8"))
        d.setdefault("users", {}); d.setdefault("keys", {})
        return d
    except Exception:
        return {"users": {}, "keys": {}}

def _save(d: dict):
    tmp = DB_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=2, ensure_ascii=False), "utf-8")
    tmp.replace(DB_PATH)

def _parse_dur(s: str) -> timedelta | None:
    s = s.strip().lower()
    alias = {"m":"m","min":"m","mins":"m","minute":"m","minutes":"m",
              "h":"h","hr":"h","hour":"h","hours":"h",
              "d":"d","day":"d","days":"d",
              "month":"mo","months":"mo","mo":"mo",
              "y":"y","year":"y","years":"y"}
    m = re.fullmatch(r"(\d+)\s*([a-zA-Z]+)", s)
    if not m: return None
    n, u = int(m.group(1)), alias.get(m.group(2))
    if n <= 0 or u is None: return None
    return {"m":timedelta(minutes=n),"h":timedelta(hours=n),
            "d":timedelta(days=n),"mo":timedelta(days=30*n),
            "y":timedelta(days=365*n)}[u]

def parse_duration(s: str) -> datetime | None:
    d = _parse_dur(s)
    return None if d is None else _now() + d

def is_admin(uid) -> bool:
    return str(uid) == str(ADMIN_ID)

def is_authorized(uid) -> bool:
    if is_admin(uid): return True
    d = _load(); u = d["users"].get(str(uid))
    if not u or not u.get("authorized") or u.get("banned"): return False
    exp = u.get("expires_at")
    if not exp: return True
    try:
        if _now() >= datetime.fromisoformat(exp):
            u["authorized"] = False; _save(d); return False
    except: return False
    return True

def is_banned(uid) -> bool:
    if is_admin(uid): return False
    d = _load(); u = d["users"].get(str(uid), {})
    return bool(u.get("banned", False))

def authorize(uid: str, uname: str = "", expires: datetime | None = None, source: str = "admin"):
    d = _load(); old = d["users"].get(str(uid), {})
    d["users"][str(uid)] = {
        "authorized": True, "banned": False,
        "username": uname or old.get("username",""),
        "expires_at": expires.isoformat() if expires else None,
        "source": source,
        "member_since": old.get("member_since", _now().isoformat()),
        "updated_at": _now().isoformat(),
    }; _save(d)

def unauthorize(uid: str) -> bool:
    d = _load()
    if str(uid) not in d["users"]: return False
    d["users"][str(uid)]["authorized"] = False
    d["users"][str(uid)]["updated_at"] = _now().isoformat()
    _save(d); return True

def ban_user(uid: str):
    d = _load(); old = d["users"].get(str(uid), {})
    d["users"][str(uid)] = {**old, "banned": True, "authorized": False,
                             "username": old.get("username",""),
                             "member_since": old.get("member_since", _now().isoformat()),
                             "updated_at": _now().isoformat()}
    _save(d)

def unban_user(uid: str) -> bool:
    d = _load()
    if str(uid) not in d["users"]: return False
    d["users"][str(uid)]["banned"] = False
    d["users"][str(uid)]["updated_at"] = _now().isoformat()
    _save(d); return True

def generate_key(duration: str, custom: str | None = None) -> tuple[str, datetime] | None:
    td = _parse_dur(duration)
    if td is None: return None
    key = (custom or ("TRADER-" + secrets.token_urlsafe(10).upper()[:12])).strip().upper()
    d = _load()
    if key in d["keys"]: return None
    d["keys"][key] = {"duration": duration, "redeemed_by": None,
                      "redeemed_username": None, "expires_at": None,
                      "created_at": _now().isoformat()}
    _save(d); return key, _now() + td

def delete_key(key: str) -> tuple[bool, str]:
    key = key.strip().upper(); d = _load()
    if key not in d["keys"]: return False, "not_found"
    if d["keys"][key].get("redeemed_by"): return False, "already_redeemed"
    del d["keys"][key]; _save(d); return True, "deleted"

def redeem_key(key: str, uid: str, uname: str = "") -> tuple[bool, str]:
    key = key.strip().upper(); d = _load()
    item = d["keys"].get(key)
    if not item: return False, "❌ Invalid key."
    if item.get("redeemed_by"): return False, "❌ Key already used."
    td = _parse_dur(str(item["duration"]))
    if td is None: return False, "❌ Corrupt key data."
    exp = _now() + td
    item["redeemed_by"] = str(uid); item["redeemed_username"] = uname
    item["redeemed_at"] = _now().isoformat(); item["expires_at"] = exp.isoformat()
    old = d["users"].get(str(uid), {})
    d["users"][str(uid)] = {
        "authorized": True, "banned": False,
        "username": uname or old.get("username",""),
        "expires_at": exp.isoformat(), "source": "redeem",
        "member_since": old.get("member_since", _now().isoformat()),
        "updated_at": _now().isoformat(),
    }; _save(d)
    return True, exp.strftime("%Y-%m-%d %H:%M UTC")

def get_user(uid: str): return _load()["users"].get(str(uid))
def get_all_users(): return _load()["users"]
def get_all_keys(): return _load()["keys"]

def get_stats() -> dict:
    d = _load(); users = d["users"]; keys = d["keys"]
    active   = sum(1 for u,v in users.items() if is_authorized(u))
    banned   = sum(1 for v in users.values() if v.get("banned"))
    redeemed = sum(1 for v in keys.values() if v.get("redeemed_by"))
    unused   = sum(1 for v in keys.values() if not v.get("redeemed_by"))
    return {"users": len(users), "active": active, "banned": banned,
            "keys": len(keys), "redeemed": redeemed, "unused": unused}

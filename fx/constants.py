from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

ADMIN_ID       = int(os.getenv("ADMIN_ID", "7472288880"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "@gajarbottle")
OWNER_URL      = f"https://t.me/{OWNER_USERNAME.lstrip('@')}"
DB_PATH        = ROOT / "users.json"

# ══════════════════════════════════════════════════════════════
# EXNESS instruments — majors / minors / metals / core crypto
# ══════════════════════════════════════════════════════════════

PAIRS = [
    # Majors
    ("EUR/USD", "EURUSD", 0.0001),
    ("GBP/USD", "GBPUSD", 0.0001),
    ("USD/JPY", "USDJPY", 0.01),
    ("USD/CHF", "USDCHF", 0.0001),
    ("AUD/USD", "AUDUSD", 0.0001),
    ("USD/CAD", "USDCAD", 0.0001),
    ("NZD/USD", "NZDUSD", 0.0001),
    # Crosses
    ("EUR/GBP", "EURGBP", 0.0001),
    ("EUR/JPY", "EURJPY", 0.01),
    ("EUR/CHF", "EURCHF", 0.0001),
    ("EUR/AUD", "EURAUD", 0.0001),
    ("EUR/CAD", "EURCAD", 0.0001),
    ("EUR/NZD", "EURNZD", 0.0001),
    ("GBP/JPY", "GBPJPY", 0.01),
    ("GBP/CHF", "GBPCHF", 0.0001),
    ("GBP/AUD", "GBPAUD", 0.0001),
    ("GBP/CAD", "GBPCAD", 0.0001),
    ("GBP/NZD", "GBPNZD", 0.0001),
    ("AUD/JPY", "AUDJPY", 0.01),
    ("AUD/CAD", "AUDCAD", 0.0001),
    ("AUD/CHF", "AUDCHF", 0.0001),
    ("AUD/NZD", "AUDNZD", 0.0001),
    ("CAD/JPY", "CADJPY", 0.01),
    ("CAD/CHF", "CADCHF", 0.0001),
    ("CHF/JPY", "CHFJPY", 0.01),
    ("NZD/JPY", "NZDJPY", 0.01),
    ("NZD/CAD", "NZDCAD", 0.0001),
    ("NZD/CHF", "NZDCHF", 0.0001),
    # Metals
    ("XAU/USD", "XAUUSD · GOLD", 0.1),
    ("XAG/USD", "XAGUSD · SILVER", 0.01),
    ("XPT/USD", "XPTUSD · PLATINUM", 0.1),
    ("XPD/USD", "XPDUSD · PALLADIUM", 0.1),
    ("XAU/EUR", "XAUEUR", 0.1),
    # Crypto
    ("BTC/USD", "BTCUSD", 1.0),
    ("ETH/USD", "ETHUSD", 0.01),
    ("XRP/USD", "XRPUSD", 0.0001),
    ("LTC/USD", "LTCUSD", 0.01),
    ("SOL/USD", "SOLUSD", 0.01),
]

_MAJOR = {
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
    "AUD/USD", "USD/CAD", "NZD/USD",
}
_METAL = {"XAU/USD", "XAG/USD", "XPT/USD", "XPD/USD", "XAU/EUR"}
_CRYPTO = {"BTC/USD", "ETH/USD", "XRP/USD", "LTC/USD", "SOL/USD"}

MAJORS  = [p for p in PAIRS if p[0] in _MAJOR]
CROSSES = [p for p in PAIRS if p[0] not in _MAJOR and p[0] not in _METAL and p[0] not in _CRYPTO]
METALS  = [p for p in PAIRS if p[0] in _METAL]
CRYPTOS = [p for p in PAIRS if p[0] in _CRYPTO]

PIP_MAP   = {p[0]: p[2] for p in PAIRS}
LABEL_MAP = {p[0]: p[1] for p in PAIRS}

def sym_list(group):
    return [p[0] for p in group]

ALL_SYM    = sym_list(PAIRS)
MAJOR_SYM  = sym_list(MAJORS)
CROSS_SYM  = sym_list(CROSSES)
METAL_SYM  = sym_list(METALS)
CRYPTO_SYM = sym_list(CRYPTOS)

def is_crypto(symbol: str) -> bool:
    return symbol in _CRYPTO

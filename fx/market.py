from __future__ import annotations
import asyncio, logging, time
import requests
import os
from .constants import PIP_MAP, LABEL_MAP
from .strategy import TraderStructure

log = logging.getLogger("TRADER.market")
_BASE = "https://api.twelvedata.com"
_LOCK = asyncio.Lock()
_LAST_CALL = 0.0
_MIN_INTERVAL = 5.0


def _key():
    k = os.getenv("TWELVE_DATA_KEY", "").strip()
    if not k:
        raise RuntimeError("TWELVE_DATA_KEY missing in .env")
    return k


def _fetch(symbol: str, count: int = 120) -> list[dict]:
    global _LAST_CALL
    now = time.time()
    wait = _MIN_INTERVAL - (now - _LAST_CALL)
    if wait > 0:
        time.sleep(wait)

    last_err = None
    for attempt in range(3):
        try:
            r = requests.get(
                f"{_BASE}/time_series",
                timeout=20,
                params={
                    "symbol": symbol,
                    "interval": "5min",
                    "outputsize": count,
                    "apikey": _key(),
                    "format": "JSON",
                },
            )
            _LAST_CALL = time.time()
            if r.status_code == 429:
                sleep_s = 20 * (attempt + 1)
                log.warning("429 for %s — waiting %ss (attempt %s)", symbol, sleep_s, attempt + 1)
                time.sleep(sleep_s)
                last_err = requests.HTTPError("429 Too Many Requests")
                continue
            r.raise_for_status()
            d = r.json()
            if d.get("status") == "error":
                raise RuntimeError(d.get("message", str(d)))
            out = []
            for v in reversed(d.get("values", [])):
                try:
                    out.append({
                        "time":  int(time.mktime(time.strptime(v["datetime"], "%Y-%m-%d %H:%M:%S"))),
                        "open":  float(v["open"]),
                        "high":  float(v["high"]),
                        "low":   float(v["low"]),
                        "close": float(v["close"]),
                    })
                except Exception:
                    continue
            return out
        except requests.HTTPError as e:
            last_err = e
            if "429" in str(e):
                time.sleep(20 * (attempt + 1))
                continue
            raise
        except Exception as e:
            last_err = e
            raise
    raise last_err or RuntimeError(f"Failed to fetch {symbol}")


async def fetch_signal(symbol: str, mode: str = "normal") -> dict:
    async with _LOCK:
        loop = asyncio.get_event_loop()
        # 5m needs more bars for clean structure (≈12–16h of data)
        candles = await loop.run_in_executor(None, _fetch, symbol, 200)
    if len(candles) < 80:
        raise RuntimeError(f"Only {len(candles)} candles for {symbol}")

    o = [c["open"]  for c in candles]
    h = [c["high"]  for c in candles]
    l = [c["low"]   for c in candles]
    c = [c["close"] for c in candles]
    t = [c["time"]  for c in candles]

    pip = PIP_MAP.get(symbol, 0.0001)
    # buffer in pips — ATR does the real sizing
    if pip >= 1.0:          # BTC
        buf = 5
    elif pip >= 0.1:        # Gold
        buf = 6
    elif pip >= 0.01:       # JPY / Silver
        buf = 5
    else:                   # standard FX
        buf = 5

    eng = TraderStructure(pip=pip, rr=2.2, sl_buf=buf, mode=mode)
    res = eng.snipe(o, h, l, c, t, volumes=None)

    recent = candles[-20:]
    sup  = min(x["low"]  for x in recent)
    res_ = max(x["high"] for x in recent)

    trend = res.get("trend", "NEUTRAL")
    if trend == "BULLISH":
        trend_disp = "BULLISH 📈"
    elif trend == "BEARISH":
        trend_disp = "BEARISH 📉"
    else:
        trend_disp = "NEUTRAL ➡️"

    return {
        "symbol":     symbol,
        "label":      LABEL_MAP.get(symbol, symbol),
        "signal":     res.get("signal", "HOLD"),
        "entry":      res.get("entry", float(c[-1])),
        "sl":         res.get("sl"),
        "tp":         res.get("tp"),
        "sl_pips":    res.get("sl_pips"),
        "tp_pips":    res.get("tp_pips"),
        "rr":         res.get("rr", "1:2.2"),
        "trend":      trend_disp,
        "support":    f"{sup:.5f}",
        "resistance": f"{res_:.5f}",
        "last_ts":    int(t[-1]),
        "candles":    candles,
        "engine":     eng,
        "reason":     res.get("reason", ""),
        "structure":  res.get("structure", ""),
        "bos":        res.get("bos"),
        "choch":      res.get("choch"),
        "mode":       mode,
        "score":      res.get("score", 0),
        "tags":       res.get("tags", []),
    }


async def scan_all(symbols: list[str], on_progress=None, mode: str = "normal") -> dict | None:
    total = len(symbols)
    for i, sym in enumerate(symbols, 1):
        if on_progress:
            try:
                await on_progress(i, total, sym)
            except Exception:
                pass
        try:
            d = await fetch_signal(sym, mode=mode)
            if d["signal"] in ("BUY", "SELL"):
                return d
        except Exception as e:
            log.warning("skip %s: %s", sym, e)
    return None

from __future__ import annotations

"""
TRADER  ·  Multi-System 5M Engine

Primary (exact video):
  HH/HL + BOS · LH/LL + BOS · CHOCH

Confluence stack (all run on the same 5M bars):
  1. Market Structure (BOS / CHOCH)          — required
  2. EMA trend (9 / 21)                     — direction filter
  3. Pullback into EMA / last swing zone
  4. Liquidity sweep (wick beyond swing then close back)
  5. Fair Value Gap / imbalance (simple 3-candle)
  6. Volume spike (relative to 20-bar avg)
  7. RSI zone + optional divergence
  8. ATR expansion (volatility alive)
  9. Session bias (London / NY hours)

Score >= threshold → tradable signal.
SL beyond structure · TP 2–2.5R.
"""

from datetime import datetime, timezone


def _atr(h, l, c, n=14):
    if len(c) < n + 1:
        return None
    trs = [max(h[i] - l[i], abs(h[i] - c[i-1]), abs(l[i] - c[i-1])) for i in range(1, len(c))]
    atr = sum(trs[:n]) / n
    for i in range(n, len(trs)):
        atr = (atr * (n - 1) + trs[i]) / n
    return atr


def _ema(series, n):
    if len(series) < n:
        return None
    k = 2 / (n + 1)
    e = sum(series[:n]) / n
    for v in series[n:]:
        e = v * k + e * (1 - k)
    return e


def _rsi(closes, n=14):
    if len(closes) < n + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    avg_g = sum(gains[:n]) / n
    avg_l = sum(losses[:n]) / n
    for i in range(n, len(gains)):
        avg_g = (avg_g * (n - 1) + gains[i]) / n
        avg_l = (avg_l * (n - 1) + losses[i]) / n
    if avg_l == 0:
        return 100.0
    rs = avg_g / avg_l
    return 100 - (100 / (1 + rs))


def _swings(h, l, lb=3):
    sh, sl_ = [], []
    n = len(h)
    for i in range(lb, n - lb):
        if all(h[i] >= h[j] for j in range(i - lb, i + lb + 1) if j != i):
            sh.append((i, float(h[i])))
        if all(l[i] <= l[j] for j in range(i - lb, i + lb + 1) if j != i):
            sl_.append((i, float(l[i])))
    return sh, sl_


def _detect_structure(sh, sl_, closes):
    if len(sh) < 2 or len(sl_) < 2:
        return "FLAT", None, None, None, None, "need more swings"

    prev_h, last_h = sh[-2], sh[-1]
    prev_l, last_l = sl_[-2], sl_[-1]

    hh = last_h[1] > prev_h[1]
    hl = last_l[1] > prev_l[1]
    lh = last_h[1] < prev_h[1]
    ll = last_l[1] < prev_l[1]

    c1 = float(closes[-1])
    c2 = float(closes[-2]) if len(closes) > 1 else c1

    if hh and hl:
        secondary_high = prev_h[1]
        last_hl = last_l[1]
        bos = c1 > secondary_high or c2 > secondary_high
        if bos:
            if c1 < last_hl or c2 < last_hl:
                return "BEAR", last_h[1], last_l[1], secondary_high, last_hl, \
                       "CHOCH · broke last higher low"
            return "BULL", last_h[1], last_l[1], secondary_high, last_hl, \
                   "BULL · HH+HL · BOS confirmed"
        return "BULL", last_h[1], last_l[1], secondary_high, last_hl, \
               "BULL forming · waiting BOS"

    if lh and ll:
        secondary_low = prev_l[1]
        last_lh = last_h[1]
        bos = c1 < secondary_low or c2 < secondary_low
        if bos:
            if c1 > last_lh or c2 > last_lh:
                return "BULL", last_h[1], last_l[1], secondary_low, last_lh, \
                       "CHOCH · broke last lower high"
            return "BEAR", last_h[1], last_l[1], secondary_low, last_lh, \
                   "BEAR · LH+LL · BOS confirmed"
        return "BEAR", last_h[1], last_l[1], secondary_low, last_lh, \
               "BEAR forming · waiting BOS"

    if hh and not hl:
        level = prev_l[1]
        if c1 < level or c2 < level:
            return "BEAR", last_h[1], last_l[1], None, level, "CHOCH · prior HL broken"
    if ll and not lh:
        level = prev_h[1]
        if c1 > level or c2 > level:
            return "BULL", last_h[1], last_l[1], None, level, "CHOCH · prior LH broken"

    return "FLAT", last_h[1], last_l[1], None, None, "no clear structure"


def _fvg(highs, lows, side):
    if len(highs) < 3:
        return False
    if side == "BUY":
        return highs[-3] < lows[-1]
    return lows[-3] > highs[-1]


def _liquidity_sweep(highs, lows, closes, sh, sl_, side, atr):
    if not sh or not sl_ or atr is None:
        return False
    price = closes[-1]
    if side == "BUY":
        recent_low = min(s[1] for s in sl_[-3:])
        return lows[-1] < recent_low and price > recent_low and (recent_low - lows[-1]) > atr * 0.15
    recent_high = max(s[1] for s in sh[-3:])
    return highs[-1] > recent_high and price < recent_high and (highs[-1] - recent_high) > atr * 0.15


def _volume_spike(volumes, mult=1.6):
    if not volumes or len(volumes) < 21:
        return False
    avg = sum(volumes[-21:-1]) / 20
    return volumes[-1] > avg * mult if avg > 0 else False


def _session_bias(ts):
    try:
        hour = datetime.fromtimestamp(ts, tz=timezone.utc).hour
    except Exception:
        return "ANY"
    if 12 <= hour < 16:
        return "OVERLAP"
    if 7 <= hour < 16:
        return "LONDON"
    if 12 <= hour < 21:
        return "NY"
    return "ASIA"


class TraderStructure:
    MIN_SCORE = 4

    def __init__(self, pip=0.0001, rr=2.2, sl_buf=5, mode="normal"):
        self.pip = float(pip)
        self.rr = max(float(rr), 2.0)
        self.sl_buf = max(3, min(int(sl_buf), 10))
        self.mode = mode
        self.fired = 0
        self.hits = 0
        self.trade = None
        self.history = []

    def _pips(self, d):
        if self.pip <= 0:
            return 0.0
        return round(abs(d) / self.pip, 1)

    def _levels(self, side, price, anchor, atr, next_swing=None):
        buf = self.pip * self.sl_buf
        if side == "BUY":
            raw = price - (min(anchor, price) - buf)
        else:
            raw = (max(anchor, price) + buf) - price

        if atr and atr > 0:
            risk = max(atr * 0.7, min(raw, atr * 1.5))
        else:
            risk = raw

        if self.pip >= 1.0:
            lo, hi = 60.0, 250.0
        elif self.pip >= 0.1:
            lo, hi = 2.5, 10.0
        elif self.pip >= 0.01:
            lo, hi = 0.20, 0.60
        else:
            lo, hi = 0.0015, 0.0050

        risk = max(lo, min(risk, hi))
        reward = risk * self.rr

        if next_swing is not None:
            if side == "BUY" and next_swing > price:
                room = next_swing - price
                if room > reward:
                    reward = min(room * 0.85, risk * 2.8)
            elif side == "SELL" and next_swing < price:
                room = price - next_swing
                if room > reward:
                    reward = min(room * 0.85, risk * 2.8)

        if side == "BUY":
            sl = round(price - risk, 5)
            tp = round(price + reward, 5)
        else:
            sl = round(price + risk, 5)
            tp = round(price - reward, 5)
        return sl, tp, self._pips(risk), self._pips(reward), self.rr

    def snipe(self, o, h, l, c, t, volumes=None):
        n = len(c)
        if n < 80:
            return {"signal": "HOLD", "reason": "warming up — building multi-system structure"}

        opens  = [float(x) for x in o]
        highs  = [float(x) for x in h]
        lows   = [float(x) for x in l]
        closes = [float(x) for x in c]
        vols   = [float(x) for x in (volumes or [0] * n)]
        price  = closes[-1]
        ts     = t[-1] if t else 0

        atr = _atr(highs, lows, closes, 14)
        ema9  = _ema(closes, 9)
        ema21 = _ema(closes, 21)
        rsi   = _rsi(closes, 14)
        sh, sl_ = _swings(highs, lows, lb=3)

        bias, last_sh, last_sl, bos, choch, struct_note = _detect_structure(
            sh, sl_, closes
        )

        if atr is None or atr < self.pip * 3:
            return {"signal": "HOLD", "reason": "volatility dead"}

        score = 0
        tags = []

        bos_ok = "BOS confirmed" in struct_note
        if bias in ("BULL", "BEAR") and bos_ok:
            score += 2
            tags.append("STRUCTURE")
        elif bias in ("BULL", "BEAR"):
            score += 1
            tags.append("STRUCT-FORMING")
        else:
            return {
                "signal": "HOLD",
                "reason": struct_note,
                "trend": "NEUTRAL",
                "structure": struct_note,
                "score": 0,
                "tags": [],
            }

        side = "BUY" if bias == "BULL" else "SELL"

        if ema9 is not None and ema21 is not None:
            if side == "BUY" and ema9 > ema21 and price > ema9:
                score += 1
                tags.append("EMA-BULL")
            elif side == "SELL" and ema9 < ema21 and price < ema9:
                score += 1
                tags.append("EMA-BEAR")

        near_ema = ema9 is not None and abs(price - ema9) <= atr * 0.9
        near_swing = False
        if side == "BUY" and (choch or last_sl):
            lvl = choch or last_sl
            near_swing = price <= lvl + atr * 0.9
        if side == "SELL" and (choch or last_sh):
            lvl = choch or last_sh
            near_swing = price >= lvl - atr * 0.9
        if near_ema or near_swing:
            score += 1
            tags.append("PULLBACK")

        if _liquidity_sweep(highs, lows, closes, sh, sl_, side, atr):
            score += 1
            tags.append("SWEEP")

        if _fvg(highs, lows, side):
            score += 1
            tags.append("FVG")

        if _volume_spike(vols):
            score += 1
            tags.append("VOL")

        if rsi is not None:
            if side == "BUY" and 30 <= rsi <= 55:
                score += 1
                tags.append("RSI-OK")
            elif side == "SELL" and 45 <= rsi <= 70:
                score += 1
                tags.append("RSI-OK")

        if atr and len(highs) > 5:
            recent_range = max(highs[-5:]) - min(lows[-5:])
            if recent_range > atr * 0.8:
                score += 1
                tags.append("ATR-ALIVE")

        sess = _session_bias(ts)
        if sess in ("LONDON", "NY", "OVERLAP"):
            score += 1
            tags.append(sess)

        if score < self.MIN_SCORE or not bos_ok:
            return {
                "signal": "HOLD",
                "reason": f"{struct_note} · score {score}/{self.MIN_SCORE} · {', '.join(tags) or 'none'}",
                "trend": "BULLISH" if bias == "BULL" else "BEARISH" if bias == "BEAR" else "NEUTRAL",
                "structure": struct_note,
                "score": score,
                "tags": tags,
            }

        next_high = max((s[1] for s in sh[-3:]), default=None) if sh else None
        next_low  = min((s[1] for s in sl_[-3:]), default=None) if sl_ else None

        if side == "BUY":
            anchor = min(lows[-1], lows[-2], last_sl or price)
            if choch:
                anchor = min(anchor, choch)
            sl, tp, sp, tp_p, rr = self._levels("BUY", price, anchor, atr, next_high)
        else:
            anchor = max(highs[-1], highs[-2], last_sh or price)
            if choch:
                anchor = max(anchor, choch)
            sl, tp, sp, tp_p, rr = self._levels("SELL", price, anchor, atr, next_low)

        self.fired += 1
        self.trade = {"side": side, "entry": price, "sl": sl, "tp": tp}

        tag_str = " · ".join(tags)
        return {
            "signal": side,
            "entry": price,
            "sl": sl,
            "tp": tp,
            "sl_pips": round(sp, 1),
            "tp_pips": round(tp_p, 1),
            "rr": f"1:{rr:.1f}",
            "reason": f"score {score} · {tag_str} · {struct_note}",
            "trend": "BULLISH" if side == "BUY" else "BEARISH",
            "structure": struct_note,
            "bos": bos,
            "choch": choch,
            "score": score,
            "tags": tags,
        }

    def update(self, high, low):
        if not self.trade:
            return None
        tr = self.trade
        if tr["side"] == "BUY":
            if low <= tr["sl"]:
                self._close("LOSS"); return "LOSS"
            if high >= tr["tp"]:
                self._close("WIN"); return "WIN"
        else:
            if high >= tr["sl"]:
                self._close("LOSS"); return "LOSS"
            if low <= tr["tp"]:
                self._close("WIN"); return "WIN"
        return None

    def _close(self, result):
        if result == "WIN":
            self.hits += 1
        self.history.append({**self.trade, "result": result})
        self.trade = None

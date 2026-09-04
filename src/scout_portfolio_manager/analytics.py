"""Pure technical-analysis math. No I/O, no wall-clock reads, no randomness.

Every function here returns the same answer for the same input, every time,
and returns None (never raises, never fabricates a number) when the input
list is shorter than the required window. ``closes`` is always assumed
oldest-first.
"""

from typing import Optional, Sequence


def sma(closes: Sequence[float], window: int) -> Optional[float]:
    """Simple moving average over the last ``window`` closes."""
    if window <= 0 or len(closes) < window:
        return None
    return sum(closes[-window:]) / window


def ema(closes: Sequence[float], window: int) -> Optional[float]:
    """Exponential moving average, seeded with the SMA of the first window."""
    if window <= 0 or len(closes) < window:
        return None
    multiplier = 2 / (window + 1)
    value = sum(closes[:window]) / window
    for close in closes[window:]:
        value = (close - value) * multiplier + value
    return value


def rsi(closes: Sequence[float], window: int = 14) -> Optional[float]:
    """Wilder's RSI. Needs at least ``window`` + 1 closes (window deltas)."""
    if window <= 0 or len(closes) < window + 1:
        return None
    gains = []
    losses = []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))
    avg_gain = sum(gains[:window]) / window
    avg_loss = sum(losses[:window]) / window
    for i in range(window, len(gains)):
        avg_gain = (avg_gain * (window - 1) + gains[i]) / window
        avg_loss = (avg_loss * (window - 1) + losses[i]) / window
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def range_30d(closes: Sequence[float]) -> Optional[dict]:
    """{"low", "high"} over the last 30 closes, or None with fewer than 30."""
    window = 30
    if len(closes) < window:
        return None
    recent = closes[-window:]
    return {"low": min(recent), "high": max(recent)}


def distance_from_range_pct(current: float, low: float, high: float) -> dict:
    """{"from_low_pct", "from_high_pct"}: current's percent distance from each bound."""
    from_low_pct = ((current - low) / low * 100) if low else 0.0
    from_high_pct = ((current - high) / high * 100) if high else 0.0
    return {"from_low_pct": from_low_pct, "from_high_pct": from_high_pct}


def drawdown_from_cost_basis_pct(current_value_usd: float, basis_usd: float) -> float:
    """(current - basis) / basis * 100. Caller guarantees basis_usd > 0."""
    return (current_value_usd - basis_usd) / basis_usd * 100

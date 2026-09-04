"""Pure-function tests for analytics.py. No I/O; the real fixture is read once
here purely as a realistic data source for the "enough history" assertions.
"""

import json
from pathlib import Path

from scout_portfolio_manager.analytics import (
    distance_from_range_pct,
    drawdown_from_cost_basis_pct,
    ema,
    range_30d,
    rsi,
    sma,
)

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "price_history.json"


def _real_eth_closes() -> list[float]:
    raw = json.loads(FIXTURE.read_text())
    return [p["close_usd"] for p in raw["ETH"]["daily_close"]]


def test_sma_averages_the_trailing_window():
    assert sma([1.0, 2.0, 3.0, 4.0], 2) == 3.5


def test_sma_none_when_insufficient_data():
    assert sma([1.0, 2.0], 5) is None


def test_sma_none_for_non_positive_window():
    assert sma([1.0, 2.0, 3.0], 0) is None


def test_ema_matches_sma_seed_when_series_equals_window():
    assert ema([1.0, 2.0, 3.0], 3) == 2.0


def test_ema_none_when_insufficient_data():
    assert ema([1.0], 3) is None


def test_rsi_is_100_for_an_uninterrupted_uptrend():
    closes = [float(i) for i in range(1, 20)]
    assert rsi(closes, 14) == 100.0


def test_rsi_is_0_for_an_uninterrupted_downtrend():
    closes = [float(i) for i in range(20, 1, -1)]
    result = rsi(closes, 14)
    assert result == 0.0


def test_rsi_none_when_insufficient_data():
    assert rsi([1.0, 2.0, 3.0], 14) is None


def test_rsi_is_100_for_a_flat_price_series():
    # avg_gain == 0 and avg_loss == 0 both hold here; the avg_loss == 0
    # branch must resolve to 100.0 rather than raising or dividing by zero.
    closes = [100.0] * 20
    assert rsi(closes, 14) == 100.0


def test_range_30d_reports_low_and_high_over_last_30():
    closes = [float(i) for i in range(1, 40)]  # 1..39, ascending
    result = range_30d(closes)
    assert result == {"low": 10.0, "high": 39.0}


def test_range_30d_none_with_fewer_than_30_points():
    assert range_30d([1.0] * 29) is None


def test_distance_from_range_pct_at_the_low():
    result = distance_from_range_pct(100.0, low=100.0, high=200.0)
    assert result == {"from_low_pct": 0.0, "from_high_pct": -50.0}


def test_distance_from_range_pct_at_the_high():
    result = distance_from_range_pct(200.0, low=100.0, high=200.0)
    assert result == {"from_low_pct": 100.0, "from_high_pct": 0.0}


def test_drawdown_from_cost_basis_pct_negative_when_underwater():
    assert drawdown_from_cost_basis_pct(1900.0, 2000.0) == -5.0


def test_drawdown_from_cost_basis_pct_positive_when_above_basis():
    assert drawdown_from_cost_basis_pct(2200.0, 2000.0) == 10.0


def test_indicators_all_resolve_on_the_real_fixture_series():
    closes = _real_eth_closes()
    assert len(closes) >= 40
    assert sma(closes, 20) is not None
    assert ema(closes, 12) is not None
    assert rsi(closes, 14) is not None
    rng = range_30d(closes)
    assert rng is not None
    dist = distance_from_range_pct(closes[-1], rng["low"], rng["high"])
    assert -100.0 <= dist["from_low_pct"] <= 200.0
    assert -100.0 <= dist["from_high_pct"] <= 100.0

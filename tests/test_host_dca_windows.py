from pathlib import Path

import pytest

from scout_portfolio_manager.host import ReadOnlyHost

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "portfolio.json"


@pytest.fixture
def host() -> ReadOnlyHost:
    return ReadOnlyHost(FIXTURE)


def test_dca_windows_end_to_end_against_real_fixtures(host: ReadOnlyHost):
    result = host.dca_windows("ETH", risk_profile="balanced", amount_usd=300.0)
    assert result["status"] == "ok"
    assert result["boundary"] == "propose"
    assert result["asset"] == "ETH"
    assert result["window"] == "current"
    assert result["label"] in {"favorable", "neutral", "unfavorable"}
    assert result["risk_profile"] == "balanced"
    assert result["sizing_fraction"] == 0.5
    assert result["suggested_amount_usd"] == 150.0
    assert result["confidence"] == "low"
    assert (
        result["disclosure"]
        == "Heuristic indicators, not backtested; treat as descriptive, not predictive."
    )
    assert result["not_financial_advice"] == "This is analysis, not financial advice."


def test_dca_windows_defaults_to_balanced_risk_profile(host: ReadOnlyHost):
    result = host.dca_windows("ETH")
    assert result["risk_profile"] == "balanced"
    assert result["sizing_fraction"] == 0.5
    assert "suggested_amount_usd" not in result


def test_dca_windows_favorable_on_the_real_fixture_series(host: ReadOnlyHost):
    # The synthetic price fixture ends on a sustained decline to the 30-day
    # low, which is a real (not forced) favorable read for ETH.
    result = host.dca_windows("ETH")
    assert result["label"] == "favorable"


def test_dca_windows_invalid_risk_profile_raises(host: ReadOnlyHost):
    with pytest.raises(ValueError):
        host.dca_windows("ETH", risk_profile="yolo")


def test_dca_windows_conservative_and_aggressive_sizing(host: ReadOnlyHost):
    conservative = host.dca_windows("ETH", risk_profile="conservative", amount_usd=100.0)
    aggressive = host.dca_windows("ETH", risk_profile="aggressive", amount_usd=100.0)
    assert conservative["suggested_amount_usd"] == 25.0
    assert aggressive["suggested_amount_usd"] == 100.0

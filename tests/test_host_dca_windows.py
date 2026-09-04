import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scout_portfolio_manager.contracts import (
    Holding,
    PortfolioSnapshot,
    SourceMetadata,
    Transaction,
)
from scout_portfolio_manager.host import ReadOnlyHost

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "portfolio.json"
PRICE_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "price_history.json"


def _snapshot(*, observed_at) -> PortfolioSnapshot:
    return PortfolioSnapshot(
        wallet_address="0xabc123",
        chain="ethereum",
        observed_at=observed_at,
        source=SourceMetadata(
            kind="fixture", locator="test", retrieved_at=datetime(2026, 9, 3, tzinfo=timezone.utc)
        ),
        holdings=[Holding(asset="ETH", quantity=1, value_usd=2250)],
        transactions=[
            Transaction(
                id="buy-1",
                kind="buy",
                asset="ETH",
                quantity=1,
                value_usd=2000,
                occurred_at=datetime(2026, 8, 3, tzinfo=timezone.utc),
                wallet_address="0xabc123",
            )
        ],
    )


class _FakeReader:
    def __init__(self, snapshot: PortfolioSnapshot):
        self._snapshot = snapshot

    def snapshot(self) -> PortfolioSnapshot:
        return self._snapshot


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


def test_dca_windows_propagates_freshness_from_real_fixtures(host: ReadOnlyHost):
    result = host.dca_windows("ETH")
    assert result["freshness"] == {
        "stale": False,
        "max_age_days": 2,
        "last_price_date": "2026-09-03",
    }


def test_dca_windows_flags_stale_price_data_never_silently_dropped(tmp_path):
    # A price series well past the freshness gate must still produce a
    # favorable/unfavorable classification, but that classification must
    # carry a visible stale=True flag rather than looking indistinguishable
    # from a fresh one.
    stale_fixture = tmp_path / "price_history.json"
    raw = json.loads(PRICE_FIXTURE.read_text())
    stale_fixture.write_text(json.dumps(raw))
    snapshot = _snapshot(observed_at=datetime(2026, 9, 20, 12, tzinfo=timezone.utc))
    fake_host = ReadOnlyHost(_FakeReader(snapshot), price_history_path=stale_fixture)

    result = fake_host.dca_windows("ETH")

    assert result["status"] == "ok"
    assert result["label"] in {"favorable", "neutral", "unfavorable"}
    assert result["freshness"]["stale"] is True
    assert result["freshness"]["last_price_date"] == "2026-09-03"

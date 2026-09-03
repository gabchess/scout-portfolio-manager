from pathlib import Path

from zerion_portfolio_manager.portfolio import FixturePortfolioReader

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "portfolio.json"


def test_reader_observes_fixture_snapshot_without_execution_surface():
    reader = FixturePortfolioReader(FIXTURE)
    snapshot = reader.snapshot()
    assert snapshot.wallet_address == "0xabc123"
    assert snapshot.holdings[0].value_usd == 2250.0
    assert snapshot.source.kind == "fixture"

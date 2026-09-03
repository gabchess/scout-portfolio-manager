import json
from pathlib import Path

from zerion_portfolio_manager.portfolio import FixturePortfolioReader


def test_reader_observes_fixture_snapshot_without_execution_surface():
    reader = FixturePortfolioReader(Path("fixtures/portfolio.json"))
    snapshot = reader.snapshot()
    assert snapshot.wallet_address == "0xabc123"
    assert snapshot.holdings[0].value_usd == 2250.0
    assert snapshot.source.kind == "fixture"

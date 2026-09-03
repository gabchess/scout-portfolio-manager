from pathlib import Path

from zerion_portfolio_manager.portfolio import FixturePortfolioReader
from zerion_portfolio_manager.reporting import format_pnl_report


def test_report_separates_observed_calculated_assumed_and_unknown():
    snapshot = FixturePortfolioReader(Path("fixtures/portfolio.json")).snapshot()
    report = format_pnl_report(snapshot)
    assert report["observed"]
    assert report["calculated"] == ["+$250 (12.5%)"]
    assert report["assumed"] == ["fees are zero because fixture fee is zero"]
    assert report["unknown"] == []

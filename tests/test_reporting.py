from pathlib import Path

from scout_portfolio_manager.portfolio import FixturePortfolioReader
from scout_portfolio_manager.reporting import format_pnl_report

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "portfolio.json"


def test_report_separates_observed_calculated_assumed_and_unknown():
    snapshot = FixturePortfolioReader(FIXTURE).snapshot()
    report = format_pnl_report(snapshot)
    assert report["observed"]
    assert report["calculated"] == ["+$250 (12.5%)"]
    assert report["assumed"] == ["fees are zero because fixture fee is zero"]
    assert report["unknown"] == []

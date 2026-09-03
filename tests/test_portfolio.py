from pathlib import Path

from zerion_portfolio_manager.portfolio import FixturePortfolioReader

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "portfolio.json"


def test_reader_observes_fixture_snapshot_without_execution_surface():
    reader = FixturePortfolioReader(FIXTURE)
    snapshot = reader.snapshot()
    assert snapshot.wallet_address == "0xabc123"
    assert snapshot.holdings[0].value_usd == 2250.0
    assert snapshot.source.kind == "fixture"


def test_reader_reports_actual_resolved_fixture_path_as_locator(tmp_path):
    # The fixture file's own JSON bakes in a locator string ("fixtures/portfolio.json").
    # A reader pointed at a different path (e.g. the packaged wheel's data file) must
    # report where the data actually came from, not the fixture's stale self-description.
    copied = tmp_path / "elsewhere.json"
    copied.write_text(FIXTURE.read_text())
    reader = FixturePortfolioReader(copied)
    snapshot = reader.snapshot()
    assert snapshot.source.locator == str(copied)

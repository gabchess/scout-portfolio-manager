from pathlib import Path

from scout_portfolio_manager.contracts import AssetPriceHistory
from scout_portfolio_manager.price_history import FixturePriceHistoryReader

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "price_history.json"


def test_series_returns_validated_history_for_a_known_asset():
    reader = FixturePriceHistoryReader(FIXTURE)
    history = reader.series("ETH")
    assert isinstance(history, AssetPriceHistory)
    assert history.asset == "ETH"
    assert len(history.points) >= 40
    dates = [p.date for p in history.points]
    assert dates == sorted(dates)  # ascending, no gaps checked by construction
    assert history.source.kind == "fixture"


def test_series_is_case_insensitive_on_asset_symbol():
    reader = FixturePriceHistoryReader(FIXTURE)
    assert reader.series("eth") is not None


def test_series_returns_none_for_unknown_asset_not_an_exception():
    reader = FixturePriceHistoryReader(FIXTURE)
    assert reader.series("NOSUCHASSET") is None


def test_series_returns_none_when_fixture_file_is_missing(tmp_path):
    reader = FixturePriceHistoryReader(tmp_path / "does-not-exist.json")
    assert reader.series("ETH") is None

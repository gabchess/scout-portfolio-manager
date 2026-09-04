from pathlib import Path

from scout_portfolio_manager.intents import read_intent
from scout_portfolio_manager.portfolio import FixturePortfolioReader

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "portfolio.json"


def test_read_intents_return_source_grounded_answers():
    snapshot = FixturePortfolioReader(FIXTURE).snapshot()
    result = read_intent("what is my pnl?", snapshot)
    assert result.intent == "pnl"
    assert result.observed[0].startswith("ETH")
    assert result.calculated[0].startswith("+$250")
    assert result.unknown == []

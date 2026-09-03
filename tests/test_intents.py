from pathlib import Path
from zerion_portfolio_manager.intents import read_intent
from zerion_portfolio_manager.portfolio import FixturePortfolioReader


def test_read_intents_return_source_grounded_answers():
    snapshot = FixturePortfolioReader(Path("fixtures/portfolio.json")).snapshot()
    result = read_intent("what is my pnl?", snapshot)
    assert result.intent == "pnl"
    assert result.observed[0].startswith("ETH")
    assert result.calculated[0].startswith("+$250")
    assert result.unknown == []

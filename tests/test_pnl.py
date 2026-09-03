from datetime import datetime, timezone

from zerion_portfolio_manager.contracts import Holding
from zerion_portfolio_manager.pnl import calculate_pnl


def test_pnl_explains_unrealized_gain_with_formula_and_confidence():
    result = calculate_pnl(
        holding=Holding(asset="ETH", quantity=1, value_usd=2250),
        basis_usd=2000,
        valuation_at=datetime(2026, 9, 3, 12, tzinfo=timezone.utc),
        fee_usd=0,
    )
    assert result.unrealized_usd == 250
    assert result.return_pct == 12.5
    assert result.formula == "current_value_usd - basis_usd - fees_usd"
    assert result.confidence == "high"
    assert result.warnings == []

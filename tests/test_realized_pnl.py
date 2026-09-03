from datetime import datetime, timezone

from zerion_portfolio_manager.contracts import Holding, Transaction
from zerion_portfolio_manager.pnl import calculate_pnl


def test_pnl_reports_realized_profit_from_a_sell():
    result = calculate_pnl(
        holding=Holding(asset="ETH", quantity=0.5, value_usd=1250),
        basis_usd=2000,
        valuation_at=datetime(2026, 9, 3, tzinfo=timezone.utc),
        transactions=[
            Transaction(id="buy", kind="buy", asset="ETH", quantity=1, value_usd=2000,
                        occurred_at=datetime(2026, 8, 1, tzinfo=timezone.utc), wallet_address="0xabc"),
            Transaction(id="sell", kind="sell", asset="ETH", quantity=0.5, value_usd=1100,
                        occurred_at=datetime(2026, 8, 20, tzinfo=timezone.utc), wallet_address="0xabc"),
        ],
    )
    assert result.realized_usd == 100
    assert result.unrealized_usd == 250
    assert result.total_usd == 350
    assert "sell proceeds" in result.formula

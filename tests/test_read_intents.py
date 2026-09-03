from datetime import datetime, timezone

from zerion_portfolio_manager.contracts import (
    Holding,
    PortfolioSnapshot,
    SourceMetadata,
    Transaction,
)
from zerion_portfolio_manager.intents import read_intent


def snapshot():
    return PortfolioSnapshot(
        wallet_address="0xabc123",
        chain="ethereum",
        observed_at=datetime(2026, 9, 3, tzinfo=timezone.utc),
        source=SourceMetadata(
            kind="fixture", locator="test", retrieved_at=datetime(2026, 9, 3, tzinfo=timezone.utc)
        ),
        holdings=[Holding(asset="ETH", quantity=1, value_usd=2250)],
        transactions=[
            Transaction(
                id="buy-1",
                kind="buy",
                asset="ETH",
                quantity=1,
                value_usd=2000,
                occurred_at=datetime(2026, 8, 3, tzinfo=timezone.utc),
                wallet_address="0xabc123",
            )
        ],
    )


def test_last_purchase_intent_reports_observed_transaction():
    result = read_intent("what did I buy last month?", snapshot())
    assert result.intent == "last_purchase"
    assert result.observed == ["ETH: $2000.00 on 2026-08-03"]


def test_change_since_date_is_explicit_when_no_calculation_is_available():
    result = read_intent("show change since 2026-08-01", snapshot())
    assert result.intent == "change_since_date"
    assert result.unknown == ["historical valuation series is not available in this fixture"]


def test_missing_basis_is_not_presented_as_exact_pnl():
    data = snapshot()
    data.transactions = []
    result = read_intent("what is my pnl?", data)
    assert result.calculated == []
    assert result.unknown == ["missing acquisition basis for ETH"]

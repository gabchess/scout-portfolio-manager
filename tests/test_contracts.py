import json
from pathlib import Path

import pytest

from zerion_portfolio_manager.contracts import Holding, PortfolioSnapshot, Transaction

FIXTURE = Path(__file__).parents[1] / "fixtures" / "portfolio.json"


def test_fixture_loads_into_typed_portfolio_contracts():
    data = json.loads(FIXTURE.read_text())
    snapshot = PortfolioSnapshot.model_validate(data)
    assert snapshot.wallet_address == "0xabc123"
    assert snapshot.chain == "ethereum"
    assert snapshot.holdings == [Holding(asset="ETH", quantity=1.0, value_usd=2250.0)]
    assert snapshot.observed_at.isoformat() == "2026-09-03T12:00:00+00:00"
    assert snapshot.source.kind == "fixture"


def test_transaction_contract_rejects_secret_bearing_fields():
    with pytest.raises(ValueError):
        Transaction.model_validate(
            {
                "id": "tx-1",
                "kind": "buy",
                "asset": "ETH",
                "quantity": 1,
                "value_usd": 2000,
                "occurred_at": "2026-08-03T12:00:00Z",
                "wallet_address": "0xabc123",
                "private_key": "never",
            }
        )

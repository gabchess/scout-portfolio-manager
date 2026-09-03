import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from zerion_portfolio_manager.contracts import Holding, PortfolioSnapshot, Transaction
from zerion_portfolio_manager.pnl import PnlResult

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


@pytest.mark.parametrize("bad_value", [math.inf, -math.inf, math.nan])
def test_holding_rejects_inf_and_nan_quantity(bad_value):
    with pytest.raises(ValidationError):
        Holding(asset="ETH", quantity=bad_value, value_usd=1.0)


@pytest.mark.parametrize("bad_value", [math.inf, -math.inf, math.nan])
def test_holding_rejects_inf_and_nan_value_usd(bad_value):
    with pytest.raises(ValidationError):
        Holding(asset="ETH", quantity=1.0, value_usd=bad_value)


def test_holding_rejects_coerced_bool_quantity():
    with pytest.raises(ValidationError):
        Holding(asset="ETH", quantity=True, value_usd=1.0)


def test_holding_rejects_coerced_str_quantity():
    with pytest.raises(ValidationError):
        Holding(asset="ETH", quantity="1.0", value_usd=1.0)


def test_transaction_rejects_inf_value_usd():
    with pytest.raises(ValidationError):
        Transaction(
            id="tx-1",
            kind="buy",
            asset="ETH",
            quantity=1,
            value_usd=math.inf,
            occurred_at=datetime(2026, 8, 3, tzinfo=timezone.utc),
            wallet_address="0xabc123",
        )


def test_transaction_rejects_coerced_bool_fee_usd():
    with pytest.raises(ValidationError):
        Transaction(
            id="tx-1",
            kind="buy",
            asset="ETH",
            quantity=1,
            value_usd=2000,
            fee_usd=False,
            occurred_at=datetime(2026, 8, 3, tzinfo=timezone.utc),
            wallet_address="0xabc123",
        )


def test_transaction_rejects_coerced_str_value_usd():
    with pytest.raises(ValidationError):
        Transaction(
            id="tx-1",
            kind="buy",
            asset="ETH",
            quantity=1,
            value_usd="2000",
            occurred_at=datetime(2026, 8, 3, tzinfo=timezone.utc),
            wallet_address="0xabc123",
        )


@pytest.mark.parametrize("bad_value", [math.inf, -math.inf, math.nan])
def test_pnl_result_rejects_inf_and_nan(bad_value):
    with pytest.raises(ValidationError):
        PnlResult(
            asset="ETH",
            realized_usd=0,
            unrealized_usd=bad_value,
            total_usd=0,
            return_pct=0,
            valuation_at=datetime(2026, 8, 3, tzinfo=timezone.utc),
            fees_usd=0,
            formula="test",
            confidence="low",
            warnings=[],
        )

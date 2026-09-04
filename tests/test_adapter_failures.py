from datetime import datetime, timedelta, timezone

import pytest

from scout_portfolio_manager.adapters import ExecutionError, FakeExecutionAdapter
from scout_portfolio_manager.dca import DcaIntent
from scout_portfolio_manager.safety import build_preview


def make_preview(destination="wallet:0xdef456"):
    return build_preview(
        intent=DcaIntent(
            asset="ETH",
            amount_usd=300,
            chain="ethereum",
            schedule="one_time",
            source="wallet:0xabc123",
            destination=destination,
        ),
        expected_output=0.13,
        fees_usd=3,
        slippage_pct=0.5,
        quote_expiry=datetime.now(timezone.utc) + timedelta(minutes=5),
        max_fee_usd=5,
    )


def test_fake_adapter_rejects_insufficient_balance_and_wrong_destination():
    with pytest.raises(ExecutionError, match="insufficient balance"):
        FakeExecutionAdapter(balance_usd=100).execute(
            make_preview(), approval=True, idempotency_key="funds"
        )
    with pytest.raises(ExecutionError, match="wrong destination"):
        FakeExecutionAdapter(allowed_destinations={"wallet:other"}).execute(
            make_preview(), approval=True, idempotency_key="destination"
        )


def test_fake_adapter_can_expose_timeout_without_claiming_success():
    with pytest.raises(ExecutionError, match="timeout"):
        FakeExecutionAdapter(failure="timeout").execute(
            make_preview(), approval=True, idempotency_key="timeout"
        )


def test_fake_adapter_rejects_unsupported_chain():
    with pytest.raises(ExecutionError, match="unsupported chain"):
        FakeExecutionAdapter(supported_chains={"base"}).execute(
            make_preview(), approval=True, idempotency_key="chain"
        )


def test_stale_quote_is_rejected():
    stale = build_preview(
        intent=DcaIntent(
            asset="ETH",
            amount_usd=300,
            chain="ethereum",
            schedule="one_time",
            source="wallet:0xabc123",
            destination="wallet:0xdef456",
        ),
        expected_output=0.13,
        fees_usd=3,
        slippage_pct=0.5,
        quote_expiry=datetime.now(timezone.utc) - timedelta(seconds=1),
        max_fee_usd=5,
    )
    with pytest.raises(ExecutionError, match="stale"):
        FakeExecutionAdapter().execute(stale, approval=True, idempotency_key="stale")


def test_duplicate_idempotency_key_is_rejected():
    adapter = FakeExecutionAdapter()
    adapter.execute(make_preview(), approval=True, idempotency_key="same")
    with pytest.raises(ExecutionError, match="duplicate"):
        adapter.execute(make_preview(), approval=True, idempotency_key="same")


def test_rejected_authorization_is_not_execution():
    with pytest.raises(ExecutionError, match="approval"):
        FakeExecutionAdapter().execute(make_preview(), approval=False, idempotency_key="rejected")

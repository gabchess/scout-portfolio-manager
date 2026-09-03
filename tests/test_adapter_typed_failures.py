from datetime import datetime, timedelta, timezone

import pytest

from zerion_portfolio_manager.adapters import ExecutionError, FakeExecutionAdapter
from zerion_portfolio_manager.dca import DcaIntent
from zerion_portfolio_manager.safety import build_preview


def preview():
    return build_preview(
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
        quote_expiry=datetime.now(timezone.utc) + timedelta(minutes=5),
        max_fee_usd=5,
    )


def test_fake_adapter_models_typed_provider_rejection_and_settlement_mismatch():
    with pytest.raises(ExecutionError, match="authorization_rejected"):
        FakeExecutionAdapter(failure="authorization_rejected").execute(
            preview(), approval=True, idempotency_key="auth"
        )
    with pytest.raises(ExecutionError, match="settlement_mismatch"):
        FakeExecutionAdapter(failure="settlement_mismatch").execute(
            preview(), approval=True, idempotency_key="settlement"
        )


def test_fake_adapter_rejects_unknown_failure_code():
    with pytest.raises(ValueError, match="unsupported failure"):
        FakeExecutionAdapter(failure="invented_failure")

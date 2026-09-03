from datetime import datetime, timedelta, timezone

import pytest

from zerion_portfolio_manager.adapters import FakeExecutionAdapter, ExecutionError
from zerion_portfolio_manager.dca import DcaIntent
from zerion_portfolio_manager.safety import build_preview


def preview():
    return build_preview(
        intent=DcaIntent(asset="ETH", amount_usd=300, chain="ethereum", schedule="one_time",
                         source="wallet:0xabc123", destination="wallet:0xdef456"),
        expected_output=0.13, fees_usd=3, slippage_pct=0.5,
        quote_expiry=datetime.now(timezone.utc) + timedelta(minutes=5), max_fee_usd=5)


def test_fake_adapter_requires_explicit_approval_and_can_execute_once():
    adapter = FakeExecutionAdapter()
    with pytest.raises(ExecutionError, match="approval"):
        adapter.execute(preview(), approval=False, idempotency_key="k1")
    result = adapter.execute(preview(), approval=True, idempotency_key="k1")
    assert result.status == "submitted"


def test_fake_adapter_rejects_stale_quote_and_duplicate_request():
    adapter = FakeExecutionAdapter()
    stale = build_preview(intent=DcaIntent(asset="ETH", amount_usd=300, chain="ethereum", schedule="one_time",
        source="wallet:0xabc123", destination="wallet:0xdef456"), expected_output=0.13, fees_usd=3,
        slippage_pct=0.5, quote_expiry=datetime.now(timezone.utc)-timedelta(seconds=1), max_fee_usd=5)
    with pytest.raises(ExecutionError, match="stale"):
        adapter.execute(stale, approval=True, idempotency_key="stale")
    adapter.execute(preview(), approval=True, idempotency_key="dup")
    with pytest.raises(ExecutionError, match="duplicate"):
        adapter.execute(preview(), approval=True, idempotency_key="dup")

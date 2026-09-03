from datetime import datetime, timezone

from zerion_portfolio_manager.dca import DcaIntent
from zerion_portfolio_manager.safety import build_preview


def test_preview_contains_all_material_transaction_fields_and_requires_approval():
    preview = build_preview(
        intent=DcaIntent(
            asset="ETH",
            amount_usd=300,
            chain="ethereum",
            schedule="one_time",
            source="wallet:0xabc123",
            destination="wallet:0xdef456",
        ),
        expected_output=0.13,
        fees_usd=3.0,
        slippage_pct=0.5,
        quote_expiry=datetime(2026, 9, 3, 13, tzinfo=timezone.utc),
        max_fee_usd=5,
    )
    assert preview.approval_state == "required"
    assert preview.asset == "ETH"
    assert preview.amount_usd == 300
    assert preview.currency == "USD"
    assert preview.chain == "ethereum"
    assert preview.source == "wallet:0xabc123"
    assert preview.destination == "wallet:0xdef456"
    assert preview.expected_output == 0.13
    assert preview.fees_usd == 3
    assert preview.slippage_pct == 0.5
    assert preview.quote_expiry.year == 2026
    assert preview.schedule == "one_time"
    assert preview.max_fee_usd == 5
    assert "settlement" in preview.failure_behavior.lower()

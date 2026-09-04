from scout_portfolio_manager.verification import SettlementVerifier


def test_verifier_reads_both_execution_and_portfolio_sources_before_verifying():
    calls = []

    def execution_reader(execution_id):
        calls.append("execution")
        return {
            "id": execution_id,
            "status": "confirmed",
            "asset": "ETH",
            "amount_usd": 300,
            "destination": "wallet:0xdef456",
        }

    def portfolio_reader():
        calls.append("portfolio")
        return {"last_asset": "ETH", "last_amount_usd": 300, "last_destination": "wallet:0xdef456"}

    result = SettlementVerifier(execution_reader, portfolio_reader).verify_execution(
        "fake-tx-1",
        expected_asset="ETH",
        expected_amount_usd=300,
        expected_destination="wallet:0xdef456",
    )
    assert result.status == "verified"
    assert calls == ["execution", "portfolio"]


def test_verifier_rejects_mismatched_readback():
    verifier = SettlementVerifier(
        lambda _: {
            "status": "confirmed",
            "asset": "ETH",
            "amount_usd": 300,
            "destination": "wallet:wrong",
        },
        lambda: {"last_asset": "ETH", "last_amount_usd": 300, "last_destination": "wallet:wrong"},
    )
    result = verifier.verify_execution(
        "fake-tx-1",
        expected_asset="ETH",
        expected_amount_usd=300,
        expected_destination="wallet:0xdef456",
    )
    assert result.status == "mismatch"
    assert "destination" in result.reason

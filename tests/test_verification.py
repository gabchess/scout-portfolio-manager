from zerion_portfolio_manager.verification import SettlementVerifier


def test_verifier_requires_independent_evidence_configuration():
    verifier = SettlementVerifier()
    result = verifier.verify({"status": "confirmed", "portfolio_readback": True})
    assert result.status == "mismatch"
    assert "independent" in result.reason


def test_verifier_requires_observed_settlement_evidence():
    verifier = SettlementVerifier(
        lambda _: {
            "status": "confirmed",
            "asset": "ETH",
            "amount_usd": 300,
            "destination": "wallet:0xdef456",
        },
        lambda: {
            "last_asset": "ETH",
            "last_amount_usd": 300,
            "last_destination": "wallet:0xdef456",
        },
    )
    result = verifier.verify(
        {
            "execution_id": "fake-tx-1",
            "expected_asset": "ETH",
            "expected_amount_usd": 300,
            "expected_destination": "wallet:0xdef456",
        }
    )
    assert result.status == "verified"


def test_unconfirmed_execution_stays_pending():
    calls = []

    def execution_reader(_):
        calls.append("execution")
        return {"status": "submitted"}

    def portfolio_reader():
        calls.append("portfolio")
        return {}

    result = SettlementVerifier(execution_reader, portfolio_reader).verify_execution(
        "fake-tx-1",
        expected_asset="ETH",
        expected_amount_usd=300,
        expected_destination="wallet:0xdef456",
    )
    assert result.status == "pending"
    assert calls == ["execution"]

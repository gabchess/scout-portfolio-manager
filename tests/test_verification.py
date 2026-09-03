from zerion_portfolio_manager.verification import SettlementVerifier


def test_verifier_requires_observed_settlement_evidence():
    verifier = SettlementVerifier()
    assert verifier.verify({"status": "submitted"}).status == "pending"
    assert verifier.verify({"status": "confirmed", "portfolio_readback": True}).status == "verified"
    assert verifier.verify({"status": "confirmed", "portfolio_readback": False}).status == "mismatch"

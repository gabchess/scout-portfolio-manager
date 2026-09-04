from scout_portfolio_manager.ledger import TransactionLedger


def test_ledger_exposes_observed_transactions_and_user_basis_without_secrets():
    ledger = TransactionLedger()
    ledger.add("tx-1", kind="buy", asset="ETH", quantity=1.0, value_usd=2000.0)
    ledger.add_basis(asset="ETH", amount_usd=2000.0, source="user_input")
    assert ledger.transactions()[0].id == "tx-1"
    assert ledger.basis("ETH").amount_usd == 2000.0

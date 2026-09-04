from scout_portfolio_manager.dca import parse_dca_request


def test_dca_parser_returns_clarification_instead_of_inference():
    result = parse_dca_request("DCA another $300 of ETH")
    assert result.status == "needs_clarification"
    assert result.intent.asset == "ETH"
    assert result.intent.amount_usd == 300
    assert result.missing == ["chain", "schedule", "source", "destination"]
    assert "chain" in result.question.lower()

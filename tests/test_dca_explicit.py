from zerion_portfolio_manager.dca import parse_dca_request


def test_dca_parser_extracts_explicit_execution_fields():
    result = parse_dca_request(
        "DCA $300 ETH on ethereum weekly from wallet:0xabc123 to wallet:0xdef456"
    )
    assert result.status == "ready"
    assert result.missing == []
    assert result.intent.chain == "ethereum"
    assert result.intent.schedule == "weekly"
    assert result.intent.source == "wallet:0xabc123"
    assert result.intent.destination == "wallet:0xdef456"

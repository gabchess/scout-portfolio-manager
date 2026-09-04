import pytest

from scout_portfolio_manager.dca import parse_dca_request


@pytest.mark.parametrize(
    "text,field",
    [
        (
            "DCA $300 ETH on ethereum and on base weekly from wallet:0xabc123 to wallet:0xdef456",
            "chain",
        ),
        (
            (
                "DCA $300 ETH on ethereum weekly from wallet:0xabc123 "
                "to wallet:0xdef456 and to wallet:0x999999"
            ),
            "destination",
        ),
        (
            "DCA $300 ETH on ethereum weekly and monthly from wallet:0xabc123 to wallet:0xdef456",
            "schedule",
        ),
    ],
)
def test_ambiguous_material_fields_require_clarification(text, field):
    result = parse_dca_request(text)
    assert result.status == "needs_clarification"
    assert field in result.missing
    assert result.intent.model_dump()[field] is None

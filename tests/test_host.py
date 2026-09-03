from pathlib import Path

import pytest

from zerion_portfolio_manager import __version__
from zerion_portfolio_manager.host import TOOL_NAMES, ReadOnlyHost, default_host

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "portfolio.json"


@pytest.fixture
def host() -> ReadOnlyHost:
    return ReadOnlyHost(FIXTURE)


def test_tool_manifest_is_read_only_and_complete(host: ReadOnlyHost):
    names = [tool["name"] for tool in host.tool_manifest()]
    assert names == list(TOOL_NAMES)
    assert "execute" not in names
    assert "execute_dca" not in names


def test_tool_manifest_entries_carry_a_version(host: ReadOnlyHost):
    for tool in host.tool_manifest():
        assert tool["version"] == __version__


def test_get_portfolio_snapshot_observes_fixture(host: ReadOnlyHost):
    result = host.get_portfolio_snapshot()
    assert result["status"] == "ok"
    assert result["boundary"] == "observe"
    assert result["snapshot"]["wallet_address"] == "0xabc123"
    assert result["snapshot"]["holdings"][0]["asset"] == "ETH"
    assert result["snapshot"]["source"]["kind"] == "fixture"


def test_get_pnl_explains_fixture_unrealized_gain(host: ReadOnlyHost):
    result = host.get_pnl()
    assert result["status"] == "ok"
    assert result["boundary"] == "calculate"
    assert len(result["results"]) == 1
    pnl = result["results"][0]
    assert pnl["asset"] == "ETH"
    assert pnl["unrealized_usd"] == 250.0
    assert pnl["return_pct"] == 12.5
    assert result["unknown"] == []


def test_get_pnl_filters_unknown_asset(host: ReadOnlyHost):
    result = host.get_pnl(asset="BTC")
    assert result["results"] == []
    assert "no holding observed for BTC" in result["unknown"]


def test_parse_dca_asks_instead_of_inferring(host: ReadOnlyHost):
    result = host.parse_dca_request("DCA another $300 of ETH")
    assert result["status"] == "needs_clarification"
    assert result["boundary"] == "propose"
    assert "chain" in result["missing"]
    assert "schedule" in result["missing"]
    assert "source" in result["missing"]
    assert "destination" in result["missing"]
    assert result["question"]


def test_parse_dca_ready_when_explicit(host: ReadOnlyHost):
    result = host.parse_dca_request(
        "DCA $300 ETH on ethereum weekly from wallet:0xabc123 to wallet:0xdef456"
    )
    assert result["status"] == "ready"
    assert result["missing"] == []
    assert result["intent"]["amount_usd"] == 300
    assert result["intent"]["destination"] == "wallet:0xdef456"


def test_preview_dca_blocks_incomplete_request(host: ReadOnlyHost):
    result = host.preview_dca("DCA another $300 of ETH")
    assert result["status"] == "needs_clarification"
    assert result["preview"] is None


def test_preview_dca_requires_approval_and_refuses_execution(host: ReadOnlyHost):
    result = host.preview_dca(
        "DCA $300 ETH on ethereum weekly from wallet:0xabc123 to wallet:0xdef456",
        expected_output=0.13,
        fees_usd=3.0,
        slippage_pct=0.5,
        quote_expiry="2026-09-03T13:00:00+00:00",
        max_fee_usd=5.0,
    )
    assert result["status"] == "preview_ready"
    assert result["boundary"] == "approve"
    assert result["approval_state"] == "required"
    assert result["execution_available"] is False
    preview = result["preview"]
    assert preview["asset"] == "ETH"
    assert preview["amount_usd"] == 300
    assert preview["chain"] == "ethereum"
    assert preview["source"] == "wallet:0xabc123"
    assert preview["destination"] == "wallet:0xdef456"
    assert preview["approval_state"] == "required"


def test_call_tool_dispatches_and_rejects_execute(host: ReadOnlyHost):
    snap = host.call_tool("get_portfolio_snapshot")
    assert snap["boundary"] == "observe"
    with pytest.raises(PermissionError, match="not available on the read-only host"):
        host.call_tool("execute", {"text": "DCA $300 ETH"})
    with pytest.raises(ValueError, match="unknown tool"):
        host.call_tool("not_a_tool")


def test_default_host_resolves_repo_fixture():
    host = default_host()
    result = host.get_portfolio_snapshot()
    assert result["snapshot"]["holdings"][0]["quantity"] == 1.0


def test_default_host_uses_packaged_fixture():
    host = default_host()
    assert host.get_portfolio_snapshot()["status"] == "ok"

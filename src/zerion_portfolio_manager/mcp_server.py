"""MCP stdio server for the read-only portfolio host.

Requires the optional dependency: pip install -e '.[mcp]'

No execute, sign, wallet, or network tools are registered.
"""

from __future__ import annotations

import json
import os

from .host import ReadOnlyHost, default_host


def build_host() -> ReadOnlyHost:
    fixture = os.environ.get("ZPM_FIXTURE_PATH")
    if fixture:
        return ReadOnlyHost(fixture)
    return default_host()


def _require_mcp():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - exercised via import error path in tests
        raise SystemExit(
            "MCP extra is not installed. Run: pip install -e '.[mcp]'"
        ) from exc
    return FastMCP


def create_server(host: ReadOnlyHost | None = None):
    FastMCP = _require_mcp()
    host = host or build_host()
    server = FastMCP(
        "zerion-portfolio-manager",
        instructions=(
            "Read-only Zerion-shaped portfolio intelligence. "
            "Tools observe fixtures, calculate PnL, parse DCA requests, and build previews. "
            "There is no execute, sign, or wallet tool. Never invent missing DCA fields."
        ),
    )

    @server.tool(name="get_portfolio_snapshot")
    def get_portfolio_snapshot() -> str:
        """Observe the fixture-backed portfolio snapshot. Read-only."""
        return json.dumps(host.get_portfolio_snapshot(), indent=2, default=str)

    @server.tool(name="get_pnl")
    def get_pnl(asset: str | None = None) -> str:
        """Calculate explainable USD PnL. Optional asset filter. Read-only."""
        return json.dumps(host.get_pnl(asset=asset), indent=2, default=str)

    @server.tool(name="parse_dca_request")
    def parse_dca_request(text: str) -> str:
        """Parse a DCA request. Asks for missing fields instead of inferring them."""
        return json.dumps(host.parse_dca_request(text), indent=2, default=str)

    @server.tool(name="preview_dca")
    def preview_dca(
        text: str,
        expected_output: float | None = None,
        fees_usd: float | None = None,
        slippage_pct: float | None = None,
        quote_expiry: str | None = None,
        max_fee_usd: float | None = None,
    ) -> str:
        """Build a complete DCA preview with approval_state=required. Does not execute."""
        return json.dumps(
            host.preview_dca(
                text,
                expected_output=expected_output,
                fees_usd=fees_usd,
                slippage_pct=slippage_pct,
                quote_expiry=quote_expiry,
                max_fee_usd=max_fee_usd,
            ),
            indent=2,
            default=str,
        )

    return server


def main() -> None:
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()

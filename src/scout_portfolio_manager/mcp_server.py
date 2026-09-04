"""MCP stdio server for the read-only portfolio host.

Requires the optional dependency: pip install -e '.[mcp]'

No execute, sign, wallet, or network tools are registered. The only network access is
the read-only Zerion source, and only when ZERION_API_KEY and ZERION_WALLET_ADDRESS are
both set in the server's environment.
"""

from __future__ import annotations

import json
import os
from typing import Mapping

from .host import ReadOnlyHost, default_host
from .zerion_api import ZerionConfigError, reader_from_env


def build_host(environ: Mapping[str, str] | None = None) -> ReadOnlyHost:
    """Pick the source from the environment.

    Zerion API when ZERION_API_KEY and ZERION_WALLET_ADDRESS are both set; a partial pair
    raises ZerionConfigError. Otherwise ZPM_FIXTURE_PATH, then the packaged fixture.
    """
    env = os.environ if environ is None else environ
    reader = reader_from_env(env)
    if reader is not None:
        return ReadOnlyHost(reader)
    fixture = env.get("ZPM_FIXTURE_PATH")
    if fixture:
        return ReadOnlyHost(fixture)
    return default_host()


def _require_mcp():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - exercised via import error path in tests
        raise SystemExit("MCP extra is not installed. Run: pip install -e '.[mcp]'") from exc
    return FastMCP


def create_server(host: ReadOnlyHost | None = None):
    FastMCP = _require_mcp()
    host = host or build_host()
    server = FastMCP(
        "scout-portfolio",
        instructions=(
            "Read-only portfolio intelligence. "
            "Tools observe fixtures, calculate PnL, parse DCA requests, and build previews. "
            "There is no execute, sign, or wallet tool. Never invent missing DCA fields."
        ),
    )

    @server.tool(name="get_portfolio_snapshot")
    def get_portfolio_snapshot() -> str:
        """Observe the current portfolio snapshot from the configured read-only
        source (fixture-backed by default, or a live Zerion-backed wallet read
        when ZERION_API_KEY/ZERION_WALLET_ADDRESS are set). Read-only.
        """
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

    @server.tool(name="analyze_asset")
    def analyze_asset(asset: str) -> str:
        """Heuristic SMA/EMA/RSI/range/drawdown indicators for one asset. Read-only."""
        return json.dumps(host.analyze_asset(asset), indent=2, default=str)

    @server.tool(name="dca_windows")
    def dca_windows(
        asset: str,
        risk_profile: str = "balanced",
        amount_usd: float | None = None,
    ) -> str:
        """Classify the current window for a DCA buy. Proposes only; not financial advice."""
        return json.dumps(
            host.dca_windows(asset, risk_profile=risk_profile, amount_usd=amount_usd),
            indent=2,
            default=str,
        )

    return server


def main() -> None:
    try:
        server = create_server()
    except ZerionConfigError as exc:
        raise SystemExit(f"zpm-mcp: {exc}") from None
    server.run(transport="stdio")


if __name__ == "__main__":
    main()

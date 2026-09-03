"""Read-only host surface for agent runtimes.

Exposes observe/calculate/propose/preview only. No execute tool exists here.
Execution stays behind FakeExecutionAdapter and requires a separate authority path.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .dca import DcaIntent, parse_dca_request
from .pnl import PnlResult, calculate_pnl
from .portfolio import FixturePortfolioReader
from .safety import build_preview

TOOL_NAMES = (
    "get_portfolio_snapshot",
    "get_pnl",
    "parse_dca_request",
    "preview_dca",
)

# Deterministic fixture quote assumptions used only when the caller omits quote fields.
# Labeled as assumed so hosts never confuse them with observed market data.
DEFAULT_ETH_USD = 2250.0
DEFAULT_FEE_USD = 3.0
DEFAULT_SLIPPAGE_PCT = 0.5
DEFAULT_MAX_FEE_USD = 5.0
DEFAULT_QUOTE_TTL_SECONDS = 300


class ReadOnlyHost:
    """Fixture-backed read-only adapter suitable for MCP or direct Python hosts."""

    def __init__(self, fixture_path: Union[str, Path]):
        self.reader = FixturePortfolioReader(fixture_path)

    def tool_manifest(self) -> List[Dict[str, Any]]:
        """MCP-shaped tool descriptors. No execute capability is advertised."""
        return [
            {
                "name": "get_portfolio_snapshot",
                "description": (
                    "Observe the current fixture-backed portfolio snapshot. "
                    "Read-only. Returns typed holdings and transactions."
                ),
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
            {
                "name": "get_pnl",
                "description": (
                    "Calculate explainable USD PnL from the observed snapshot. "
                    "Optionally filter by asset symbol. Read-only."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "asset": {
                            "type": "string",
                            "description": "Optional asset filter, e.g. ETH",
                        }
                    },
                    "additionalProperties": False,
                },
            },
            {
                "name": "parse_dca_request",
                "description": (
                    "Parse a user DCA request into explicit fields. "
                    "Missing fields produce clarification questions. Never infers wallets, "
                    "chains, schedules, source, or destination."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Natural-language DCA request from the user",
                        }
                    },
                    "required": ["text"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "preview_dca",
                "description": (
                    "Parse a DCA request and, if complete, build a full preview with "
                    "approval_state=required. Does not execute, sign, or submit."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Natural-language DCA request from the user",
                        },
                        "expected_output": {
                            "type": "number",
                            "description": "Optional quote output quantity. Assumed from fixture price if omitted.",
                        },
                        "fees_usd": {
                            "type": "number",
                            "description": "Optional fee in USD. Defaults to a labeled fixture assumption.",
                        },
                        "slippage_pct": {
                            "type": "number",
                            "description": "Optional slippage percent. Defaults to a labeled fixture assumption.",
                        },
                        "quote_expiry": {
                            "type": "string",
                            "description": "Optional ISO-8601 quote expiry. Defaults to now+5m UTC.",
                        },
                        "max_fee_usd": {
                            "type": "number",
                            "description": "Optional max fee. Defaults to a labeled fixture assumption.",
                        },
                    },
                    "required": ["text"],
                    "additionalProperties": False,
                },
            },
        ]

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        arguments = arguments or {}
        if name == "get_portfolio_snapshot":
            return self.get_portfolio_snapshot()
        if name == "get_pnl":
            return self.get_pnl(asset=arguments.get("asset"))
        if name == "parse_dca_request":
            text = arguments.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError("parse_dca_request requires non-empty text")
            return self.parse_dca_request(text)
        if name == "preview_dca":
            text = arguments.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError("preview_dca requires non-empty text")
            return self.preview_dca(
                text,
                expected_output=arguments.get("expected_output"),
                fees_usd=arguments.get("fees_usd"),
                slippage_pct=arguments.get("slippage_pct"),
                quote_expiry=arguments.get("quote_expiry"),
                max_fee_usd=arguments.get("max_fee_usd"),
            )
        if name in {"execute", "execute_dca", "submit", "sign"}:
            raise PermissionError(
                f"{name} is not available on the read-only host; "
                "execution requires a separate authority decision"
            )
        raise ValueError(f"unknown tool: {name}")

    def get_portfolio_snapshot(self) -> Dict[str, Any]:
        snapshot = self.reader.snapshot()
        return {
            "status": "ok",
            "boundary": "observe",
            "snapshot": snapshot.model_dump(mode="json"),
        }

    def get_pnl(self, asset: Optional[str] = None) -> Dict[str, Any]:
        snapshot = self.reader.snapshot()
        target = asset.upper() if asset else None
        results: List[PnlResult] = []
        unknown: List[str] = []
        for holding in snapshot.holdings:
            if target and holding.asset.upper() != target:
                continue
            buys = [
                t for t in snapshot.transactions
                if t.asset == holding.asset and t.kind == "buy"
            ]
            basis = sum(t.value_usd + t.fee_usd for t in buys)
            if not basis:
                unknown.append(f"missing acquisition basis for {holding.asset}")
                continue
            results.append(
                calculate_pnl(
                    holding=holding,
                    basis_usd=basis,
                    valuation_at=snapshot.observed_at,
                    transactions=snapshot.transactions,
                )
            )
        if target and not results and not unknown:
            unknown.append(f"no holding observed for {target}")
        return {
            "status": "ok",
            "boundary": "calculate",
            "results": [r.model_dump(mode="json") for r in results],
            "unknown": unknown,
        }

    def parse_dca_request(self, text: str) -> Dict[str, Any]:
        parsed = parse_dca_request(text)
        return {
            "status": parsed.status,
            "boundary": "propose",
            "intent": parsed.intent.model_dump(mode="json"),
            "missing": parsed.missing,
            "question": parsed.question,
        }

    def preview_dca(
        self,
        text: str,
        *,
        expected_output: Optional[float] = None,
        fees_usd: Optional[float] = None,
        slippage_pct: Optional[float] = None,
        quote_expiry: Optional[Union[str, datetime]] = None,
        max_fee_usd: Optional[float] = None,
    ) -> Dict[str, Any]:
        parsed = parse_dca_request(text)
        if parsed.status != "ready":
            return {
                "status": "needs_clarification",
                "boundary": "propose",
                "intent": parsed.intent.model_dump(mode="json"),
                "missing": parsed.missing,
                "question": parsed.question,
                "preview": None,
            }

        assumed: List[str] = []
        intent = parsed.intent
        assert intent.amount_usd is not None  # ready status guarantees this

        if expected_output is None:
            expected_output = round(intent.amount_usd / DEFAULT_ETH_USD, 8) if intent.asset == "ETH" else 0.0
            assumed.append(
                f"expected_output derived from fixture {intent.asset} price "
                f"${DEFAULT_ETH_USD if intent.asset == 'ETH' else 'unknown'}"
            )
        if fees_usd is None:
            fees_usd = DEFAULT_FEE_USD
            assumed.append(f"fees_usd assumed {DEFAULT_FEE_USD}")
        if slippage_pct is None:
            slippage_pct = DEFAULT_SLIPPAGE_PCT
            assumed.append(f"slippage_pct assumed {DEFAULT_SLIPPAGE_PCT}")
        if max_fee_usd is None:
            max_fee_usd = DEFAULT_MAX_FEE_USD
            assumed.append(f"max_fee_usd assumed {DEFAULT_MAX_FEE_USD}")
        if quote_expiry is None:
            expiry = datetime.now(timezone.utc) + timedelta(seconds=DEFAULT_QUOTE_TTL_SECONDS)
            assumed.append(f"quote_expiry assumed now+{DEFAULT_QUOTE_TTL_SECONDS}s")
        elif isinstance(quote_expiry, str):
            expiry = datetime.fromisoformat(quote_expiry.replace("Z", "+00:00"))
        else:
            expiry = quote_expiry

        preview = build_preview(
            intent=DcaIntent.model_validate(intent.model_dump()),
            expected_output=float(expected_output),
            fees_usd=float(fees_usd),
            slippage_pct=float(slippage_pct),
            quote_expiry=expiry,
            max_fee_usd=float(max_fee_usd) if max_fee_usd is not None else None,
        )
        return {
            "status": "preview_ready",
            "boundary": "approve",
            "intent": intent.model_dump(mode="json"),
            "missing": [],
            "question": None,
            "assumed": assumed,
            "preview": preview.model_dump(mode="json"),
            "approval_state": preview.approval_state,
            "execution_available": False,
            "note": (
                "Preview only. Explicit approval and a separately authorized execution "
                "rail are required before any submission."
            ),
        }


def default_host(repo_root: Optional[Union[str, Path]] = None) -> ReadOnlyHost:
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[2]
    return ReadOnlyHost(root / "fixtures" / "portfolio.json")

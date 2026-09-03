from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass(frozen=True)
class VerificationResult:
    status: str
    reason: str


class SettlementVerifier:
    """Independent readback boundary. It never submits or mutates execution."""

    def __init__(self, execution_reader: Optional[Callable[[str], Dict[str, Any]]] = None,
                 portfolio_reader: Optional[Callable[[], Dict[str, Any]]] = None):
        self.execution_reader = execution_reader
        self.portfolio_reader = portfolio_reader

    def verify(self, evidence: Dict[str, Any]) -> VerificationResult:
        if evidence.get("status") != "confirmed":
            return VerificationResult("pending", "settlement confirmation has not been observed")
        if evidence.get("portfolio_readback") is not True:
            return VerificationResult("mismatch", "confirmed transaction lacks matching portfolio readback")
        return VerificationResult("verified", "transaction and portfolio settlement evidence agree")

    def verify_execution(self, execution_id: str, *, expected_asset: str,
                         expected_amount_usd: float, expected_destination: str) -> VerificationResult:
        if self.execution_reader is None or self.portfolio_reader is None:
            raise ValueError("independent execution and portfolio readers are required")
        execution = self.execution_reader(execution_id)
        if execution.get("status") != "confirmed":
            return VerificationResult("pending", "settlement confirmation has not been observed")
        portfolio = self.portfolio_reader()
        expected = {
            "asset": expected_asset,
            "amount_usd": expected_amount_usd,
            "destination": expected_destination,
        }
        observed = {
            "asset": portfolio.get("last_asset"),
            "amount_usd": portfolio.get("last_amount_usd"),
            "destination": portfolio.get("last_destination"),
        }
        mismatches = [key for key in expected if execution.get(key) != expected[key] or observed[key] != expected[key]]
        if mismatches:
            return VerificationResult("mismatch", "readback mismatch: " + ", ".join(mismatches))
        return VerificationResult("verified", "independent transaction and portfolio readback agree")

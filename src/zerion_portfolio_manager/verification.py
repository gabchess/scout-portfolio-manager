from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class VerificationResult:
    status: str
    reason: str


class SettlementVerifier:
    """Independent readback boundary. It never submits or mutates execution."""

    def verify(self, evidence: Dict[str, Any]) -> VerificationResult:
        if evidence.get("status") != "confirmed":
            return VerificationResult("pending", "settlement confirmation has not been observed")
        if evidence.get("portfolio_readback") is not True:
            return VerificationResult("mismatch", "confirmed transaction lacks matching portfolio readback")
        return VerificationResult("verified", "transaction and portfolio settlement evidence agree")

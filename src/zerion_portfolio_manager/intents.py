from typing import List

from pydantic import BaseModel, ConfigDict

from .contracts import PortfolioSnapshot
from .pnl import calculate_pnl


class ReadIntentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str
    observed: List[str]
    calculated: List[str]
    assumed: List[str]
    unknown: List[str]


def read_intent(text: str, snapshot: PortfolioSnapshot) -> ReadIntentResult:
    lowered = text.lower()
    if "buy" in lowered or "purchase" in lowered:
        intent = "last_purchase"
    elif "change since" in lowered:
        intent = "change_since_date"
    elif "pnl" in lowered or "profit" in lowered:
        intent = "pnl"
    else:
        intent = "holdings"
    observed = [
        f"{h.asset}: {h.quantity} units, ${h.value_usd:.2f} current value"
        for h in snapshot.holdings
    ]
    calculated = []
    unknown = []
    if intent == "last_purchase":
        purchases = [t for t in snapshot.transactions if t.kind == "buy"]
        if purchases:
            latest = max(purchases, key=lambda tx: tx.occurred_at)
            observed = [f"{latest.asset}: ${latest.value_usd:.2f} on {latest.occurred_at.date()}"]
        else:
            unknown.append("no purchases observed")
    elif intent == "change_since_date":
        unknown.append("historical valuation series is not available in this fixture")
    if intent in ("last_purchase", "change_since_date"):
        return ReadIntentResult(
            intent=intent, observed=observed, calculated=[], assumed=[], unknown=unknown
        )
    if intent == "pnl":
        for holding in snapshot.holdings:
            buys = [
                t for t in snapshot.transactions if t.asset == holding.asset and t.kind == "buy"
            ]
            basis = sum(t.value_usd + t.fee_usd for t in buys)
            if basis:
                result = calculate_pnl(
                    holding=holding,
                    basis_usd=basis,
                    valuation_at=snapshot.observed_at,
                    transactions=snapshot.transactions,
                )
                sign = "+" if result.unrealized_usd >= 0 else ""
                calculated.append(f"{sign}${result.unrealized_usd:.0f} ({result.return_pct:.1f}%)")
            else:
                unknown.append(f"missing acquisition basis for {holding.asset}")
    return ReadIntentResult(
        intent=intent, observed=observed, calculated=calculated, assumed=[], unknown=unknown
    )

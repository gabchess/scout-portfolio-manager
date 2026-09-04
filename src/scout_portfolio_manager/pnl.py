from datetime import datetime
from typing import List, Literal, Optional, Sequence

from pydantic import BaseModel, ConfigDict

from .contracts import Holding, Transaction


class PnlResult(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    asset: str
    realized_usd: float = 0
    unrealized_usd: float
    total_usd: float
    return_pct: float
    valuation_at: datetime
    fees_usd: float
    formula: str
    confidence: Literal["high", "medium", "low"]
    warnings: List[str]


def calculate_pnl(
    *,
    holding: Holding,
    basis_usd: float,
    valuation_at: datetime,
    fee_usd: float = 0,
    transactions: Optional[Sequence[Transaction]] = None,
) -> PnlResult:
    transactions = list(transactions or [])
    sells = [t for t in transactions if t.asset == holding.asset and t.kind == "sell"]
    buys = [t for t in transactions if t.asset == holding.asset and t.kind == "buy"]
    bought_quantity = sum(t.quantity for t in buys)
    sold_quantity = sum(t.quantity for t in sells)
    realized = 0.0
    remaining_basis = basis_usd
    formula = "current_value_usd - basis_usd - fees_usd"
    if sells and bought_quantity:
        allocated_basis = basis_usd * min(sold_quantity / bought_quantity, 1)
        realized = sum(t.value_usd for t in sells) - allocated_basis
        remaining_basis = basis_usd - allocated_basis
        formula = "sell proceeds - allocated basis; current value - remaining basis"
    unrealized = holding.value_usd - remaining_basis - fee_usd
    total = realized + unrealized
    return PnlResult(
        asset=holding.asset,
        realized_usd=round(realized, 4),
        unrealized_usd=round(unrealized, 4),
        total_usd=round(total, 4),
        return_pct=round(total / basis_usd * 100, 4) if basis_usd else 0,
        valuation_at=valuation_at,
        fees_usd=fee_usd,
        formula=formula,
        confidence="high" if basis_usd > 0 else "low",
        warnings=[] if basis_usd > 0 else ["missing acquisition basis"],
    )

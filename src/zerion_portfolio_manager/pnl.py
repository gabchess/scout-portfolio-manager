from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, ConfigDict

from .contracts import Holding


class PnlResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset: str
    unrealized_usd: float
    return_pct: float
    valuation_at: datetime
    fees_usd: float
    formula: str
    confidence: Literal["high", "medium", "low"]
    warnings: List[str]


def calculate_pnl(*, holding: Holding, basis_usd: float,
                  valuation_at: datetime, fee_usd: float = 0) -> PnlResult:
    gain = holding.value_usd - basis_usd - fee_usd
    return PnlResult(
        asset=holding.asset,
        unrealized_usd=gain,
        return_pct=round(gain / basis_usd * 100, 4) if basis_usd else 0,
        valuation_at=valuation_at,
        fees_usd=fee_usd,
        formula="current_value_usd - basis_usd - fees_usd",
        confidence="high" if basis_usd > 0 else "low",
        warnings=[] if basis_usd > 0 else ["missing acquisition basis"],
    )

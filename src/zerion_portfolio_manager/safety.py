from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

from .dca import DcaIntent


class DcaPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset: str
    amount_usd: float
    currency: Literal["USD"]
    chain: str
    source: str
    destination: str
    expected_output: float
    fees_usd: float
    slippage_pct: float
    quote_expiry: datetime
    schedule: str
    max_fee_usd: Optional[float]
    approval_state: Literal["required"]
    failure_behavior: str


def build_preview(*, intent: DcaIntent, expected_output: float, fees_usd: float,
                  slippage_pct: float, quote_expiry: datetime,
                  max_fee_usd: Optional[float]) -> DcaPreview:
    if not all((intent.asset, intent.amount_usd, intent.chain, intent.schedule,
                intent.source, intent.destination)):
        raise ValueError("complete DCA intent required for preview")
    return DcaPreview(
        asset=intent.asset, amount_usd=intent.amount_usd, currency="USD",
        chain=intent.chain, source=intent.source, destination=intent.destination,
        expected_output=expected_output, fees_usd=fees_usd, slippage_pct=slippage_pct,
        quote_expiry=quote_expiry, schedule=intent.schedule, max_fee_usd=max_fee_usd,
        approval_state="required",
        failure_behavior="If the quote expires or settlement fails, do not report success; surface the failure for review.",
    )

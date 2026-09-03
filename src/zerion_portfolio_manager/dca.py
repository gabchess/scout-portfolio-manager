import re
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DcaIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset: Optional[str] = None
    amount_usd: Optional[float] = None
    chain: Optional[str] = None
    schedule: Optional[str] = None
    source: Optional[str] = None
    destination: Optional[str] = None


class DcaParseResult(BaseModel):
    intent: DcaIntent
    status: str
    missing: List[str]
    question: Optional[str] = None


def parse_dca_request(text: str) -> DcaParseResult:
    amount = re.search(r"\$(\d+(?:\.\d+)?)", text)
    asset = re.search(r"\b(ETH|BTC|USDC|SOL)\b", text, re.I)
    intent = DcaIntent(
        asset=asset.group(1).upper() if asset else None,
        amount_usd=float(amount.group(1)) if amount else None,
    )
    missing = [name for name in ("asset", "amount_usd", "chain", "schedule", "source", "destination")
               if getattr(intent, name) is None]
    question = f"Which {missing[0].replace('_', ' ')} should I use?" if missing else None
    return DcaParseResult(intent=intent, status="needs_clarification" if missing else "ready",
                          missing=missing, question=question)

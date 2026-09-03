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
    chain = re.search(r"\bon\s+([a-z][a-z0-9-]*)", text, re.I)
    schedule = re.search(r"\b(one[- ]?time|daily|weekly|monthly)\b", text, re.I)
    source = re.search(r"\bfrom\s+(wallet:[^\s]+|rail:[^\s]+)", text, re.I)
    destination = re.search(r"\bto\s+(wallet:[^\s]+|rail:[^\s]+)", text, re.I)
    intent = DcaIntent(
        asset=asset.group(1).upper() if asset else None,
        amount_usd=float(amount.group(1)) if amount else None,
        chain=chain.group(1).lower() if chain else None,
        schedule=schedule.group(1).lower().replace("-", "_").replace(" ", "_") if schedule else None,
        source=source.group(1) if source else None,
        destination=destination.group(1) if destination else None,
    )
    missing = [name for name in ("asset", "amount_usd", "chain", "schedule", "source", "destination")
               if getattr(intent, name) is None]
    question = f"Which {missing[0].replace('_', ' ')} should I use?" if missing else None
    return DcaParseResult(intent=intent, status="needs_clarification" if missing else "ready",
                          missing=missing, question=question)

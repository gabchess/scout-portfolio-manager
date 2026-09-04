from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["fixture", "zerion_api", "user_input"]
    locator: str
    retrieved_at: datetime


class Holding(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    asset: str = Field(min_length=1)
    quantity: float = Field(ge=0, strict=True)
    value_usd: float = Field(ge=0, strict=True)


class Transaction(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    id: str = Field(min_length=1)
    kind: Literal["buy", "sell", "transfer", "fee"]
    asset: str = Field(min_length=1)
    quantity: float = Field(ge=0, strict=True)
    value_usd: float = Field(ge=0, strict=True)
    fee_usd: float = Field(default=0, ge=0, strict=True)
    occurred_at: datetime
    wallet_address: str = Field(min_length=1)


class PortfolioSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    wallet_address: str = Field(min_length=1)
    chain: str = Field(min_length=1)
    observed_at: datetime
    source: SourceMetadata
    holdings: list[Holding]
    transactions: list[Transaction]

    @field_validator("wallet_address")
    @classmethod
    def reject_secret_like_wallet_fields(cls, value: str) -> str:
        if any(marker in value.lower() for marker in ("private", "seed", "secret")):
            raise ValueError("secret-bearing wallet identifiers are not allowed")
        return value


class BasisInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset: str = Field(min_length=1)
    amount_usd: float = Field(gt=0)
    source: Literal["observed_transactions", "user_input"]
    as_of: Optional[datetime] = None

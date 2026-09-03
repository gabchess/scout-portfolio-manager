"""Read-only adapter for Zerion's wallet portfolio endpoint.

Only the aggregate portfolio endpoint is used.  Zerion's aggregate response
contains no transaction ledger, so the domain snapshot intentionally exposes a
single aggregate holding and an empty transaction list rather than inventing
asset-level or transaction data.
"""

from __future__ import annotations

import base64
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .contracts import Holding, PortfolioSnapshot, SourceMetadata


class ZerionAPIError(RuntimeError):
    """Base class for safe, typed Zerion adapter failures."""

    def __init__(self, message: str, *, status: Optional[int] = None) -> None:
        self.status = status
        super().__init__(message)


class ZerionAPIAuthError(ZerionAPIError):
    """The API rejected the configured credential."""


class ZerionAPIRateLimitError(ZerionAPIError):
    """The API rate limit was reached."""


class ZerionAPITransportError(ZerionAPIError):
    """The request could not be completed or decoded."""


class ZerionConfigError(ValueError):
    """The environment enables the Zerion source only partially or invalidly."""


@dataclass(frozen=True)
class ZerionAPIConfig:
    """Connection settings; the API key is excluded from representations."""

    api_key: str = field(repr=False)
    base_url: str = "https://api.zerion.io/v1"
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        if not isinstance(self.api_key, str) or not self.api_key.strip():
            raise ValueError("api_key must be non-empty")
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive and finite")


Transport = Callable[[Request, float], Mapping[str, Any]]


class ZerionAPIReader:
    """Observe one wallet through Zerion's read-only portfolio endpoint."""

    def __init__(self, config: ZerionAPIConfig, *, transport: Optional[Transport] = None) -> None:
        self.config = config
        self._transport = transport or self._request

    def snapshot(self, wallet_address: str, chain: str = "multi-chain") -> PortfolioSnapshot:
        """Fetch and map the aggregate portfolio without executing any action."""
        if not isinstance(wallet_address, str) or not wallet_address.strip():
            raise ValueError("wallet_address must be non-empty")
        if not isinstance(chain, str) or not chain.strip():
            raise ValueError("chain must be non-empty")

        path = f"/wallets/{quote(wallet_address, safe='')}/portfolio"
        retrieved_at = datetime.now(timezone.utc)
        try:
            payload = self._transport(self._build_request(path), self.config.timeout_seconds)
        except ZerionAPIError:
            raise
        except Exception as exc:
            # Injected transports are untrusted boundaries too; never expose
            # their exception text because it may contain credentials or URLs.
            raise ZerionAPITransportError("Zerion API transport failed") from exc

        attributes = self._attributes(payload)
        total = self._number(attributes.get("total", {}).get("positions"))
        if total is None:
            raise ZerionAPIError("Zerion response did not contain a valid portfolio total")

        observed_at = self._parse_timestamp(
            attributes.get("updated_at") or attributes.get("observed_at"), retrieved_at
        )
        return PortfolioSnapshot(
            wallet_address=wallet_address,
            chain=chain,
            observed_at=observed_at,
            source=SourceMetadata(kind="zerion_api", locator=path, retrieved_at=retrieved_at),
            holdings=[Holding(asset="PORTFOLIO", quantity=1.0, value_usd=total)],
            transactions=[],
        )

    @staticmethod
    def _number(value: Any) -> Optional[float]:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        value = float(value)
        return value if math.isfinite(value) and value >= 0 else None

    @staticmethod
    def _parse_timestamp(value: Any, fallback: datetime) -> datetime:
        if value is None:
            return fallback
        if not isinstance(value, str):
            raise ZerionAPIError("Zerion response contained an invalid timestamp")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise ZerionAPIError("Zerion response contained an invalid timestamp") from None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    def _build_request(self, path: str) -> Request:
        encoded = base64.b64encode((self.config.api_key + ":").encode("utf-8")).decode("ascii")
        url = (
            f"{self.config.base_url.rstrip('/')}{path}?"
            "filter%5Bpositions%5D=only_simple&currency=usd"
        )
        return Request(
            url,
            headers={"Authorization": f"Basic {encoded}", "Accept": "application/json"},
            method="GET",
        )

    @staticmethod
    def _attributes(payload: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            attributes = payload["data"]["attributes"]
        except (KeyError, TypeError):
            raise ZerionAPIError("malformed Zerion portfolio response") from None
        if not isinstance(attributes, Mapping):
            raise ZerionAPIError("malformed Zerion portfolio response")
        return attributes

    @staticmethod
    def _request(request: Request, timeout: float) -> Mapping[str, Any]:
        try:
            with urlopen(request, timeout=timeout) as response:  # noqa: S310 - configured API host
                payload = json.loads(response.read())
        except HTTPError as exc:
            if exc.code in {401, 403}:
                raise ZerionAPIAuthError(
                    "Zerion API authorization failed", status=exc.code
                ) from None
            if exc.code == 429:
                raise ZerionAPIRateLimitError(
                    "Zerion API rate limit reached", status=exc.code
                ) from None
            raise ZerionAPIError(f"Zerion API returned HTTP {exc.code}", status=exc.code) from None
        except (
            URLError,
            TimeoutError,
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as exc:
            raise ZerionAPITransportError("Zerion API request or response failed") from exc
        if not isinstance(payload, Mapping):
            raise ZerionAPITransportError("Zerion API returned a non-object JSON response")
        return payload


class ZerionWalletReader:
    """One-wallet view of ZerionAPIReader matching the host's zero-argument reader protocol."""

    def __init__(
        self, reader: ZerionAPIReader, wallet_address: str, chain: str = "multi-chain"
    ) -> None:
        if not isinstance(wallet_address, str) or not wallet_address.strip():
            raise ValueError("wallet_address must be non-empty")
        self._reader = reader
        self.wallet_address = wallet_address
        self.chain = chain

    def snapshot(self) -> PortfolioSnapshot:
        return self._reader.snapshot(self.wallet_address, self.chain)


# Environment variables that enable the read-only Zerion source. The key and the wallet
# must BOTH be present; a partial configuration is an error, never a fixture fallback.
API_KEY_ENV = "ZERION_API_KEY"
WALLET_ENV = "ZERION_WALLET_ADDRESS"
CHAIN_ENV = "ZERION_CHAIN"


def reader_from_env(
    environ: Mapping[str, str], *, transport: Optional[Transport] = None
) -> Optional[ZerionWalletReader]:
    """Build the Zerion source from the environment, or return None when it is not enabled.

    Returns None only when neither variable is set. Raises ZerionConfigError when exactly
    one is set, so a half-configured host fails loudly instead of silently serving the
    fixture. The error message never contains the credential value.
    """
    key = (environ.get(API_KEY_ENV) or "").strip()
    wallet = (environ.get(WALLET_ENV) or "").strip()
    if not key and not wallet:
        return None
    if not key or not wallet:
        missing = WALLET_ENV if key else API_KEY_ENV
        raise ZerionConfigError(
            f"{API_KEY_ENV} and {WALLET_ENV} must both be set to enable the Zerion API "
            f"source; {missing} is missing. The fixture is not used as a fallback."
        )
    chain = (environ.get(CHAIN_ENV) or "").strip() or "multi-chain"
    api_reader = ZerionAPIReader(ZerionAPIConfig(api_key=key), transport=transport)
    return ZerionWalletReader(api_reader, wallet, chain)

# TA-01: Price-history fixture + pure analytics functions

Prerequisites: none. First ticket.

## Objective

Land the data and the math with no tool surface yet. Fully self-contained:
nothing in `host.py`, `mcp_server.py`, or any manifest changes this ticket.

## Files this ticket may touch

- `fixtures/price_history.json` (new)
- `src/scout_portfolio_manager/contracts.py` (add `PricePoint`,
  `AssetPriceHistory`)
- `src/scout_portfolio_manager/price_history.py` (new)
- `src/scout_portfolio_manager/analytics.py` (new)
- `tests/test_price_history.py` (new)
- `tests/test_analytics.py` (new)

## Interface / contract

`fixtures/price_history.json`: object keyed by asset symbol (e.g. `"ETH"`).
Each value: `{"source": {"kind": "fixture", "locator": ..., "retrieved_at": ...},
"daily_close": [{"date": "YYYY-MM-DD", "close_usd": <float>}, ...]}`. Dates
ascending, no gaps, at least 40 points, ending on or after
`fixtures/portfolio.json`'s `observed_at` date (2026-09-03). `date` is a
calendar date string, not a datetime: this is daily-close data, distinct
from the intraday timestamps used elsewhere in the codebase. Values are
synthetic and deterministic (hand-authored or scripted with a fixed seed);
no live network call, ever, from this fixture's reader.

`contracts.py` additions, `extra="forbid"` like every other model here:

```python
class PricePoint(BaseModel):
    date: date  # calendar date, not datetime
    close_usd: float = Field(ge=0, strict=True)

class AssetPriceHistory(BaseModel):
    asset: str = Field(min_length=1)
    source: SourceMetadata
    points: list[PricePoint]
```

`price_history.py`, mirroring `portfolio.py`'s reader shape:

```python
class PriceHistoryReader(Protocol):
    def series(self, asset: str) -> Optional[AssetPriceHistory]: ...

class FixturePriceHistoryReader:
    def __init__(self, fixture_path): ...
    def series(self, asset: str) -> Optional[AssetPriceHistory]:
        # None (not an exception) when the asset key is absent from the
        # fixture; callers turn that into an "unknown" entry, matching the
        # existing observed/calculated/assumed/unknown idiom.
```

`analytics.py`, pure functions, no I/O, no pydantic required on the
signatures (plain floats/lists in, plain values out):

```python
def sma(closes: list[float], window: int) -> Optional[float]: ...
def ema(closes: list[float], window: int) -> Optional[float]: ...
def rsi(closes: list[float], window: int = 14) -> Optional[float]: ...
def range_30d(closes: list[float]) -> Optional[dict]:  # {"low": ..., "high": ...}
def distance_from_range_pct(current: float, low: float, high: float) -> dict:
    # {"from_low_pct": ..., "from_high_pct": ...}
def drawdown_from_cost_basis_pct(current_value_usd: float, basis_usd: float) -> float:
    # (current_value_usd - basis_usd) / basis_usd * 100; caller guarantees basis_usd > 0
```

Each function returns `None` (never raises, never fabricates a number) when
the input list is shorter than the required window. `closes` is assumed
oldest-first; callers pass `[p.close_usd for p in history.points]`.

## Invariant it must not break

Pure functions only: no network, no file I/O, no `datetime.now()`, in
`analytics.py`. Given the same list, the same answer, every time.
`extra="forbid"` on both new pydantic models, matching every existing
contract in this file.

## Acceptance check

`pytest tests/test_analytics.py tests/test_price_history.py -q` green.
Cover: SMA/EMA/RSI/range on the real fixture data; each function's
`None`-on-insufficient-data path; `FixturePriceHistoryReader.series("ETH")`
returns a validated `AssetPriceHistory`; `series("NOSUCHASSET")` returns
`None`, not an exception.

## Escalation trigger

If hitting all of SMA-20, EMA-12, RSI-14, and a full 30-day range at the
fixture's last date needs more than about 40 points to avoid `None`
results, extend the fixture rather than shrinking the windows: the windows
are pinned by TA-02/TA-03's output contract.

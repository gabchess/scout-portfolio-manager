# TA-03: `dca_windows` host + MCP tool

Prerequisites: TA-02.

## Objective

A sixth read-only tool, `dca_windows`, that classifies the current window as
favorable, neutral, or unfavorable for a DCA buy, sized by a risk-profile
fraction. Carries the mandatory not-financial-advice line.

## Files this ticket may touch

- `src/scout_portfolio_manager/dca_windows.py` (new: the pure classification
  function)
- `src/scout_portfolio_manager/host.py`
- `src/scout_portfolio_manager/mcp_server.py`
- `scripts/check_plugin_manifest.py` (extend `EXPECTED_TOOLS`)
- `README.md` (add `` `dca_windows` `` to "Tools registered:")
- `LOADOUT-MANIFEST.json` (`surfaces.python_host`, `surfaces.mcp`)
- `tests/test_mcp_server.py` (extend the exact registered-tools list)
- `tests/test_dca_windows.py` (new, pure-function tests)
- `tests/test_host_dca_windows.py` (new, host-level tests)

## Interface / contract

Pure function in `dca_windows.py`, no I/O:

```python
def classify_window(
    *,
    rsi_14: Optional[float],
    distance_from_range_pct: Optional[dict],  # {"from_low_pct", "from_high_pct"}
    risk_profile: Literal["conservative", "balanced", "aggressive"],
    amount_usd: Optional[float] = None,
) -> dict: ...
```

Classification rule, compound conditions only (never a single indicator
touch, per crypto-active-trading's RSI-pins-at-extremes finding):

- `favorable`: `rsi_14 is not None and rsi_14 < 35` AND
  `distance_from_range_pct["from_low_pct"] <= 15`.
- `unfavorable`: `rsi_14 is not None and rsi_14 > 70` AND
  `distance_from_range_pct["from_high_pct"] >= -5`.
- `neutral`: anything else, including when `rsi_14` or the range distance
  is `None` (missing data classifies as neutral, never favorable or
  unfavorable; an unclassifiable window is not a signal).

Sizing-fraction table, fixed constants:

```python
SIZING_FRACTION = {"conservative": 0.25, "balanced": 0.5, "aggressive": 1.0}
```

`suggested_amount_usd = amount_usd * SIZING_FRACTION[risk_profile]` only
when `amount_usd` is given; omit the key otherwise.

`ReadOnlyHost.dca_windows(asset: str, risk_profile: str = "balanced", amount_usd: Optional[float] = None) -> Dict[str, Any]`:
calls `analyze_asset(asset)` internally, reuses its `rsi_14` and
`distance_from_range_pct` (do not recompute), then calls `classify_window`.
Output:

```json
{
  "status": "ok",
  "boundary": "propose",
  "asset": "ETH",
  "window": "current",
  "label": "favorable",
  "risk_profile": "balanced",
  "sizing_fraction": 0.5,
  "suggested_amount_usd": 150.0,
  "rationale": "RSI 14 at 28.4 and 8.1% above the 30-day low",
  "sensitivity_note": "If RSI is off by 10 points, this classification could flip; treat as directional, not precise.",
  "confidence": "low",
  "disclosure": "Heuristic indicators, not backtested; treat as descriptive, not predictive.",
  "not_financial_advice": "This is analysis, not financial advice."
}
```

`boundary` is `"propose"`, matching `parse_dca_request`'s own boundary,
since this proposes a window and amount, it does not execute anything.
An invalid `risk_profile` value raises `ValueError` at the host layer, same
style as `preview_dca`'s `text` validation.

Add `"dca_windows"` to `TOOL_NAMES`, `tool_manifest()` (`inputSchema`
requires `asset`, optional `risk_profile` enum, optional `amount_usd`
number), and `call_tool` dispatch. Add the matching `@server.tool` wrapper.

## Invariant it must not break

`window: "current"` only, never a forecasted day or date. No new
execute-shaped tool name. The two pinned strings
(`not_financial_advice`, `disclosure`) must be byte-identical to the spec's
verbatim text, since Harrier and Kestrel grep for them literally.

## Acceptance check

`pytest -q` green, including:

- `tests/test_dca_windows.py`: each classification branch (favorable,
  unfavorable, neutral-by-missing-data, neutral-by-no-agreement); sizing
  fraction math for all three risk profiles; `suggested_amount_usd` omitted
  when `amount_usd` is `None`.
- `tests/test_host_dca_windows.py`: end-to-end against the real fixtures;
  invalid `risk_profile` raises; both pinned strings present verbatim.
- `tests/test_mcp_server.py`'s exact registered-tools list includes
  `dca_windows`.
- `python scripts/check_plugin_manifest.py` exits 0.

## Escalation trigger

If the compound-condition thresholds (35/70 RSI, 15%/-5% range distance)
produce a `neutral` result on every asset in the fixture (never favorable or
unfavorable), that is a test-fixture problem, not a threshold problem: fix
`fixtures/price_history.json` in a follow-up to TA-01 rather than loosening
the thresholds to force a hit.

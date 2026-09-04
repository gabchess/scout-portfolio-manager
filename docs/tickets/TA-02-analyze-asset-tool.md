# TA-02: `analyze_asset` host + MCP tool

Prerequisites: TA-01.

## Objective

Wire TA-01's fixture and pure functions into a fifth read-only tool,
`analyze_asset`, on the host and the MCP server, self-labeled as heuristic
and carrying the freshness gate.

## Files this ticket may touch

- `src/scout_portfolio_manager/host.py`
- `src/scout_portfolio_manager/mcp_server.py`
- `scripts/check_plugin_manifest.py` (extend `EXPECTED_TOOLS`)
- `README.md` (one line: add `` `analyze_asset` `` to the existing
  "Tools registered:" list; no other prose change here, that's TA-06)
- `LOADOUT-MANIFEST.json` (`surfaces.python_host`, `surfaces.mcp`, add
  `"technical_analysis": true` under `capabilities`)
- `tests/test_mcp_server.py` (extend the exact registered-tools list)
- `tests/test_host_analyze_asset.py` (new)

## Interface / contract

`ReadOnlyHost.analyze_asset(asset: str) -> Dict[str, Any]`:

```json
{
  "status": "ok",
  "boundary": "calculate",
  "asset": "ETH",
  "as_of": "2026-09-03T12:00:00Z",
  "freshness": {"stale": false, "max_age_days": 2, "last_price_date": "2026-09-03"},
  "indicators": {
    "sma_20": 2100.0,
    "ema_12": 2150.0,
    "rsi_14": 55.2,
    "range_30d": {"low": 1900.0, "high": 2300.0},
    "distance_from_range_pct": {"from_low_pct": 18.4, "from_high_pct": -2.2},
    "drawdown_from_cost_basis_pct": -5.0
  },
  "unknown": [],
  "confidence": "low",
  "disclosure": "Heuristic indicators, not backtested; treat as descriptive, not predictive."
}
```

Rules:

- Reuse `host.get_pnl()`'s basis calculation for `drawdown_from_cost_basis_pct`
  (call the existing basis-sum logic, do not recompute it a second way). If
  no basis is observed for the asset, omit `drawdown_from_cost_basis_pct`
  from `indicators` and add `"missing acquisition basis for {asset}"` to
  `unknown`, matching `get_pnl`'s own wording style.
- If `FixturePriceHistoryReader.series(asset)` returns `None`, every
  price-derived indicator is omitted and `unknown` gets
  `"no price history observed for {asset}"`. The response still returns
  `status: "ok"`, never an error, since a partial answer with a named gap is
  the house style (see `reporting.py`, `intents.py`).
- Freshness: `stale = (snapshot.observed_at.date() - last_price_date).days > max_age_days`,
  `max_age_days` defaults to 2. `stale: true` never suppresses an
  indicator; it only adds the flag. A caller decides what to do with a
  stale read.
- `confidence` is always the literal string `"low"`. Never computed, never
  `"high"` or `"medium"`, regardless of price-series length (see spec's
  non-obvious decisions).
- Add `"analyze_asset"` to `ReadOnlyHost.TOOL_NAMES`, `tool_manifest()`
  (with an `inputSchema` requiring `asset: string`), and `call_tool`
  dispatch. Add the matching `@server.tool(name="analyze_asset")` wrapper in
  `mcp_server.py`, same JSON-passthrough shape as the other four.

## Invariant it must not break

Read-only. No new entry to the `{"execute", "execute_dca", "submit", "sign"}`
rejection set is needed (nothing here executes), but that set itself must
not shrink. `test_create_server_registers_only_read_tools`'s banned-word
check (`execute`, `sign`, `submit`, `send`, `transfer`) must still pass with
`analyze_asset` in the registered list.

## Acceptance check

`pytest -q` green, including:

- `tests/test_host_analyze_asset.py`: ok path against the real fixtures;
  missing-basis unknown path; missing-price-history unknown path; stale
  freshness path (construct a `FixturePriceHistoryReader` pointed at a
  temp fixture with an old last date); `confidence == "low"` always;
  disclosure string present verbatim.
- `tests/test_mcp_server.py`'s exact registered-tools list includes
  `analyze_asset` and still passes the banned-word check.
- `python scripts/check_plugin_manifest.py` exits 0 (README now documents
  `analyze_asset`, `EXPECTED_TOOLS` includes it).

## Escalation trigger

If `get_pnl`'s basis logic is not easily callable as a shared helper
without duplicating it, extract it into a small private function in
`host.py` or `pnl.py` in this same ticket rather than copy-pasting the
basis-sum loop a second time. Do not defer that extraction to a later
ticket; the stock-vs-flow discipline this spec pins depends on there being
exactly one basis calculation.

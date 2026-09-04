# TA-04: `set_alert` / `check_alerts` host + MCP tools

Prerequisites: TA-02 (reuses `analyze_asset`'s indicators and freshness
gate). Independent of TA-03.

## Objective

Two paired read-only tools: `set_alert` stores a user-defined rule locally,
`check_alerts` evaluates stored rules on demand. No daemon, no cron, no
push. Stale price data is flagged on a fired or not-fired result, never
silently used to decide it.

Bundled in one ticket because neither tool is independently testable
end-to-end without the other: `check_alerts` needs a rule to check, and
`set_alert` alone proves nothing observable.

## Files this ticket may touch

- `src/scout_portfolio_manager/alerts.py` (new: `AlertRule`, `AlertStore`,
  `evaluate_alert`)
- `src/scout_portfolio_manager/host.py`
- `src/scout_portfolio_manager/mcp_server.py`
- `scripts/check_plugin_manifest.py` (extend `EXPECTED_TOOLS`)
- `README.md` (add `` `set_alert` ``, `` `check_alerts` `` to
  "Tools registered:")
- `LOADOUT-MANIFEST.json` (`surfaces.python_host`, `surfaces.mcp`, add
  `"alerts": true` under `capabilities`)
- `.gitignore` (add `.scout/`)
- `tests/test_mcp_server.py` (extend the exact registered-tools list)
- `tests/test_alerts.py` (new, pure-function and `AlertStore` tests)
- `tests/test_host_alerts.py` (new, host-level tests)

## Interface / contract

`alerts.py`:

```python
class AlertRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    asset: str
    kind: Literal["price_pct_below_cost_basis", "rsi_below"]
    threshold: float
    created_at: datetime

class AlertStore:
    def __init__(self, path: Union[str, Path]): ...
    def add(self, *, asset: str, kind: str, threshold: float) -> AlertRule: ...
    def list(self, asset: Optional[str] = None) -> list[AlertRule]: ...
    # Reads/writes one JSON file. Creates the parent directory and an empty
    # store on first write. No locking: single-process, on-demand use only,
    # matching the "no daemon" constraint.

def evaluate_alert(rule: AlertRule, *, analysis: dict, pnl: Optional[dict]) -> dict:
    # Returns {"rule_id", "asset", "kind", "threshold", "observed_value",
    # "fired": bool, "stale": bool}. "stale" comes from analysis["freshness"]["stale"]
    # when the rule is price/RSI-derived; it is always reported, never used
    # to suppress or force a firing decision.
```

`ReadOnlyHost.__init__` gains an optional `alerts_path` kwarg, defaulting to
`.scout/alerts.json` relative to the process's current working directory
when not given.

`ReadOnlyHost.set_alert(asset: str, kind: str, threshold: float) -> Dict[str, Any]`:

```json
{"status": "ok", "boundary": "propose", "rule": {"id": "...", "asset": "ETH", "kind": "rsi_below", "threshold": 30.0, "created_at": "..."}, "rule_count": 1}
```

`ReadOnlyHost.check_alerts(asset: Optional[str] = None) -> Dict[str, Any]`:

```json
{
  "status": "ok",
  "boundary": "calculate",
  "fired": [{"rule_id": "...", "asset": "ETH", "kind": "rsi_below", "threshold": 30.0, "observed_value": 28.4, "stale": false}],
  "not_fired": [],
  "unknown": [],
  "not_financial_advice": "This is analysis, not financial advice."
}
```

`check_alerts` calls `analyze_asset` (and `get_pnl` for
`price_pct_below_cost_basis` rules) once per distinct asset among the
stored rules, not once per rule, to avoid redundant recomputation. A rule
whose asset has no observed price history or basis goes to `unknown` with
the same wording style as TA-02, not silently dropped.

Add `"set_alert"` and `"check_alerts"` to `TOOL_NAMES`, `tool_manifest()`,
and `call_tool` dispatch. Add matching `@server.tool` wrappers.

## Invariant it must not break

`AlertStore` never triggers a background thread, timer, or scheduled task.
Evaluation happens exclusively inside the synchronous `check_alerts` call.
No new execute-shaped name. `stale` is reported on every fired and
not-fired entry when the rule depends on price/RSI data; it must never be
silently dropped.

## Acceptance check

`pytest -q` green, including:

- `tests/test_alerts.py`: `AlertStore` round-trips through a temp path;
  `evaluate_alert` fires/does-not-fire correctly for both rule kinds;
  `stale` propagates from `analysis["freshness"]["stale"]` without
  changing the fire/no-fire outcome.
- `tests/test_host_alerts.py`: `set_alert` then `check_alerts` end-to-end
  against a temp `alerts_path` and the real fixtures; an unknown asset
  lands in `unknown`, not silently dropped; `not_financial_advice` string
  present verbatim.
- `tests/test_mcp_server.py`'s exact registered-tools list includes both
  new names.
- `python scripts/check_plugin_manifest.py` exits 0.

## Escalation trigger

If `check_alerts` needs to run against a live, shared alert store across
multiple concurrent MCP clients (not just one `/loop` process), that is a
concurrency/locking design question outside this ticket's scope: escalate
to Forge for a design call rather than adding ad hoc file locking here.

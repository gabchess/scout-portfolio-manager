---
name: watch
description: Run Scout's full observe-through-alert chain on demand and write scout-report.html
---

# Watch

## Scope

Read-only, one on-demand pass per invocation. No execute, no daemon, no cron, no push.
Suitable for a Claude Code `/loop` tick: every run is a fresh process, so state (alert
rules) lives in `.scout/alerts.json` on disk, not in memory.

Chains all six read-only tools in order:

1. `get_portfolio_snapshot` (observe)
2. `get_pnl` (calculate)
3. `analyze_asset`, once per held asset (calculate)
4. `dca_windows`, once per held asset (propose)
5. `check_alerts` (calculate)

Then writes a static, self-contained HTML report to `$SCOUT_REPORT_PATH`
(default `./scout-report.html`), overwriting whatever was there from the
previous run. No fetch calls, no external script or style references: the
report is a plain file, safe to open with no server behind it.

## Safety rules

Same boundary as `skills/portfolio-intelligence/`, restated because this skill runs
unattended:

- Never sign, submit, execute, route, or claim settlement of a transaction.
- Never infer a chain, schedule, source wallet, destination wallet, amount, or asset.
- Every indicator carries `"Heuristic indicators, not backtested; treat as descriptive,
  not predictive."`. Every DCA-window and alert result carries `"This is analysis, not
  financial advice."`.
- If price data is stale, say so. Never suppress an indicator or silently decide a
  fire/no-fire alert outcome on stale data.
- `set_alert`/`check_alerts` never run in the background. This skill's own invocation is
  the only trigger; nothing here schedules itself.

## Running it

Direct Python entry point, no MCP server needed:

```bash
uv run python -m scout_portfolio_manager.reporting_html
```

Source selection matches the MCP server: the read-only Zerion API when
`ZERION_API_KEY`/`ZERION_WALLET_ADDRESS` are both set, else `$ZPM_FIXTURE_PATH`, else the
packaged fixture. Set `SCOUT_REPORT_PATH` to change the output location.

Under `/loop`, point the loop at this same command; each tick re-runs the chain once and
overwrites the report.

## Output shape

Report panels: portfolio snapshot (observe), PnL (calculate), technical indicators per
held asset (calculate, including each `dca_windows` label), and alerts (calculate,
empty-state text when no rules are set). State the source (fixture vs. Zerion API) and
whether any indicator is flagged stale.

See `reference.md` for the report's data contract and `examples.md` for sample runs.

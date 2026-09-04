# Spec: Scout TA layer + watch skill (0.3.0)

Status: resolved direction, ready for tickets. No interview needed.

## World-change

Scout gains a read-only technical-analysis (TA) layer on top of its existing
observe/calculate/propose/approve tools, plus a `watch` skill that chains the
whole tool set into one HTML report, runnable under Claude Code's `/loop`.
Docs stop apologizing for what Scout can't do yet and start naming what's
coming. No execution capability is added anywhere.

Version moves 0.2.0 -> 0.3.0.

## In scope

1. `analyze_asset(asset)`: SMA, EMA, RSI, drawdown-from-cost-basis,
   distance-from-30-day-range, computed from ledger transactions (existing
   `Transaction` records) plus a new synthetic fixture,
   `fixtures/price_history.json`. Self-labels as heuristic, carries a
   freshness gate.
2. `dca_windows(asset, risk_profile, amount_usd=None)`: rule-based
   favorable/neutral/unfavorable classification of the current window for a
   DCA buy, sized by a risk-profile fraction. Carries the mandatory
   not-financial-advice line.
3. `set_alert(asset, kind, threshold)` / `check_alerts(asset=None)`:
   user-defined rules, evaluated on demand only. No daemon, no push. Stale
   data is flagged, never silently used to fire or suppress.
4. `skills/watch/`: a new plugin skill, sibling of
   `skills/portfolio-intelligence/`, that chains
   snapshot -> pnl -> analyze_asset -> dca_windows -> check_alerts and writes
   `scout-report.html`, reusing the demo's existing markup/CSS. Designed to
   run unattended under `/loop`.
5. Docs reframe: README.md, START-HERE.md, docs/ARCHITECTURE.md, SECURITY.md,
   DATA-AND-PRIVACY.md keep "Scout recommends/analyzes" language, drop
   "can't touch your money"-style framing, add the pinned roadmap sentence,
   keep every boundary fact (approval required, no execute tool) as a fact.
6. Version bump to 0.3.0, CHANGELOG entry, release artifacts (dist zip,
   SHA256SUMS.txt) rebuilt via the repo's existing scripts before the pre-ship review
   sees it.

## Explicit non-goals

- **No live Zerion price-history endpoint.** The product owner's ruling stands: only
  `positions` and `transactions` are confirmed live. Live price history is a
  documented follow-up ticket (see Roadmap below), not built this loop.
- **No forecasting of future days.** `dca_windows` classifies the *current*
  observation window. It does not predict which day later this week will be
  better, since no forward-looking or intraday feed exists.
- **No daemon, cron, or push notifications.** `check_alerts` only evaluates
  when explicitly called (CLI, MCP tool call, or a `/loop` tick of the
  `watch` skill).
- **No stop-loss / position-sizing tool.** The 1-2%-risk-sizing and
  ATR-scaled-stop patterns Omnara surfaced are noted as a roadmap item, not
  built now; nothing in this brief asked for a stop-loss tool.
- **No execute, sign, submit, or wallet tool**, anywhere, including inside
  the `watch` skill. `approval_state=required` and `execution_available=false`
  are unchanged and untouched.
- **No change to `skills/portfolio-intelligence/`.** The new tools live in
  `watch`'s scope and in the four original tools' own doc surfaces; the
  original skill's SKILL.md is not required to learn about them this loop.
- **The launch video source is untouched.** Out of scope per repo
  convention at the time of this ticket set. (It has since been removed
  from the repo entirely; the video ships on socials instead.)

## Non-obvious decisions

- **Confidence is always `"low"` for TA output.** `analyze_asset` and
  `dca_windows` never claim `"high"` or `"medium"` confidence, regardless of
  price-series length. Per quant-backtest-validation's binding pattern ("a
  rule is a claim, not a result"), nothing here has been backtested, so the
  field is a fixed constant, not a computed one. This also sidesteps needing
  to hit any specific sample-size threshold to unlock a higher confidence
  claim.
- **Compound conditions for RSI extremes, not a single touch.** Per
  crypto-active-trading's finding that RSI pins at extremes in strong
  trends, `dca_windows`'s favorable/unfavorable classification requires RSI
  *and* distance-from-30-day-range to agree, never RSI alone. See TA-03.
- **`dca_windows` reuses `analyze_asset`'s indicators**, it does not
  recompute them. One RSI/SMA/EMA implementation, one place.
- **Drawdown reuses `get_pnl`'s basis calculation**, not a second
  independent basis sum. Per lena-quant-defi-methodology's stock-vs-flow
  discipline: basis is a *flow* sum (buy transactions), current value is a
  *stock* (one snapshot). Recomputing basis a second way risks the two
  drifting apart silently.
- **Alert rules persist to a local JSON file** (`AlertStore`, default path
  `.scout/alerts.json`, gitignored), not in-memory-only and not a database.
  Rationale: a `/loop` tick is a fresh process each time; in-memory state
  would silently forget every rule between ticks. This is a new mechanism
  (build-plan-sections.md's mechanism-verifier contract applies): existence
  check is "the file exists and parses," consumption check is "`check_alerts`
  reads it every call," owner is the ticket itself (TA-04), cadence is
  "every `check_alerts` invocation, no cron."
- **`scout-report.html` is written to the repo working directory** (default,
  overridable via `SCOUT_REPORT_PATH`), not to Desktop. This is the
  product's own generated deliverable for whoever runs `watch`, not a
  personal side-artifact of the operator's session.
- **Sizing-fraction convention**: conservative=0.25, balanced=0.5,
  aggressive=1.0, applied to a caller-supplied `amount_usd` when given.
  Mirrors decision-under-uncertainty's quarter/half/full confidence
  weighting, not a bucket invented from scratch.
- **New LOADOUT-MANIFEST.json capability keys are additive**: `alerts` and
  `technical_analysis` join the existing observe/calculate/propose/... keys
  rather than overloading one of them, since neither TA nor alerting maps
  cleanly onto the existing boundary vocabulary.
- **Two pinned, verbatim strings**, so the security and release review passes can grep for them
  instead of re-reading prose each time:
  - Not-financial-advice line (mandatory on `dca_windows` and
    `check_alerts` output, and anywhere docs describe Scout recommending an
    entry or a DCA window): `"This is analysis, not financial advice."`
  - Heuristic label (on `analyze_asset` and `dca_windows` output):
    `"Heuristic indicators, not backtested; treat as descriptive, not
    predictive."`
  - Roadmap sentence (docs only, Gabe's exact wording):
    `"Execution is optional and coming: Scout will DCA for you or just
    alert you, your choice."`

## Roadmap (named, not built)

- Live Zerion price-history endpoint, replacing the synthetic fixture, once
  Zerion ships or confirms one (the product owner owns re-checking this).
- Actual DCA execution and standing alert daemon/push, the two directions
  the roadmap sentence names. Both stay `approval_state=required`-gated
  even once built; this spec does not pre-authorize either.
- ATR-scaled stop-loss / position-sizing tool (Omnara's crypto-active-trading
  pattern), not requested this loop.
- `skills/portfolio-intelligence/` learning about the new TA tools, if usage
  shows the split skill boundary is awkward in practice.

## Acceptance evidence

- `pytest -q` green, including new tests for `analytics.py`, `price_history.py`,
  `analyze_asset`, `dca_windows`, `set_alert`/`check_alerts`, and the
  `watch` report renderer.
- `python scripts/check_plugin_manifest.py` exits 0.
- `python scripts/security_scan.py` (via `test_quality_gates.py`) stays clean.
- `python scripts/write_checksums.py --check` exits 0 at the final commit
  handed off for release review.
- `grep -r "This is analysis, not financial advice." src/ skills/watch/ README.md START-HERE.md`
  finds it on every entry-recommending surface.
- No tool name in `ReadOnlyHost.TOOL_NAMES`, `tool_manifest()`, or the MCP
  server contains `execute`, `sign`, `submit`, `send`, or `transfer`.
- `docs/ARCHITECTURE.md`'s tool-versioning and execution-rail-enforcement
  sections still read true after the new tools land (each new tool carries
  a `version` field; `call_tool` still rejects the same four write-shaped
  names).

## Ticket order

See `docs/tickets/TA-01` through `TA-07`. Sequential; each is buildable and
testable on its own before the next starts.

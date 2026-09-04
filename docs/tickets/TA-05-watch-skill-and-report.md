# TA-05: `watch` skill + static HTML report

Prerequisites: TA-02, TA-03, TA-04 (chains all six tools).

## Objective

A new plugin skill, `skills/watch/`, sibling of
`skills/portfolio-intelligence/`, that runs the full chain
(snapshot -> pnl -> analyze_asset -> dca_windows -> check_alerts) once per
invocation and writes a static, self-contained `scout-report.html`. Reuses
the demo's markup and CSS. Designed to run unattended under Claude Code's
`/loop`.

## Files this ticket may touch

- `skills/watch/SKILL.md` (new)
- `skills/watch/reference.md` (new)
- `skills/watch/examples.md` (new)
- `src/scout_portfolio_manager/reporting_html.py` (new)
- `.gitignore` (add `scout-report.html`)
- `tests/test_reporting_html.py` (new)

## Interface / contract

`reporting_html.py`:

```python
def render_report(
    *,
    snapshot: dict,
    pnl: dict,
    analyses: dict[str, dict],      # per held asset, analyze_asset() output
    windows: dict[str, dict],       # per held asset, dca_windows() output
    alerts: dict,                   # check_alerts() output
) -> str:
    """Return a complete, self-contained HTML document as a string. No fetch
    calls, no external script/style references beyond what's inlined: this
    runs with no server behind it, unlike the interactive demo."""
```

Visual structure and CSS classes are adapted from
`demo/zerion-portfolio-agent/static/{index.html,styles.css}`: reuse the
existing panel layout (pipeline strip, snapshot panel, PnL panel) and add
two new panels (TA indicators, alerts) in the same visual language, not a
new design. The demo's `app.js` is not reused directly since it does
client-side fetching; `reporting_html.py` inlines the already-computed data
server-side instead.

A CLI entry point (a `main()` in `reporting_html.py` or a thin script under
`scripts/`) that builds a `ReadOnlyHost` against the default fixtures, runs
the chain for every held asset in the snapshot, and writes the result to
`$SCOUT_REPORT_PATH` (default `./scout-report.html`). Document the exact
invocation (`uv run python -m scout_portfolio_manager.reporting_html` or
equivalent) in `skills/watch/SKILL.md`.

`SKILL.md` frontmatter matches the existing skill's shape:

```yaml
---
name: watch
description: Run Scout's full observe-through-alert chain on demand and write scout-report.html
---
```

Scope section states plainly: read-only, no execute, no daemon; each run is
one on-demand pass, suitable for a `/loop` tick; the report overwrites the
previous one at the same path.

## Invariant it must not break

No execute/sign/submit anywhere in the chain. The skill calls only the six
read-only tools that already exist by TA-04. `render_report` performs no
network I/O and no live Zerion call regardless of how the host was
constructed upstream (same rule the demo server follows).

## Acceptance check

`pytest tests/test_reporting_html.py -q` green: rendering against the real
fixture outputs produces valid HTML containing the snapshot's wallet
address, the PnL total, each analyzed asset's RSI value, the `dca_windows`
label, and the alerts section (empty-state text when no rules are set).
Assert the pinned not-financial-advice and heuristic-disclosure strings
appear in the rendered HTML wherever the underlying tool output carried
them.

Manual check (not a unit test): running the CLI entry point against the
repo's own fixtures produces a file at `scout-report.html` that opens
cleanly in a browser with no console errors, no fetch attempts.

## Escalation trigger

If reusing the demo's exact CSS file verbatim produces broken layout for
the two new panels (TA indicators, alerts), copy and adapt the stylesheet
into `reporting_html.py`'s own inline `<style>` block rather than editing
`demo/zerion-portfolio-agent/static/styles.css` in place. The demo's own
styling stays the demo's; this ticket must not risk breaking the
interactive demo to make the static report look right.

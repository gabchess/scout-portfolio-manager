# TA-06: Docs reframe

Prerequisites: TA-02, TA-03, TA-04, TA-05 (documents real tool names and
the real `watch` skill).

## Objective

Keep every "Scout recommends/analyzes trades" line. Drop
"can't touch your money"-style defensive framing in favor of the pinned
roadmap sentence. Keep every boundary fact (approval required, no execute
tool today) stated as fact, not softened. Add the not-financial-advice
sentence everywhere Scout describes recommending an entry or a DCA window.
Document running `watch` under `/loop`.

## Files this ticket may touch

- `README.md`
- `START-HERE.md`
- `docs/ARCHITECTURE.md`
- `SECURITY.md`
- `DATA-AND-PRIVACY.md`
- `evals/behavioral-evals.md` (new rows for the four new tools)

Not in scope: the launch video source (explicitly out of scope per the
brief, and since removed from the repo entirely),
`skills/portfolio-intelligence/` (non-goal, see spec).

## Interface / contract

Exact strings to add, verbatim, matching TA-02/TA-03/TA-04's pinned text:

- Roadmap sentence, in README.md's "Where it stops" section and
  START-HERE.md's "Boundaries" section:
  `"Execution is optional and coming: Scout will DCA for you or just alert
  you, your choice."`
- Not-financial-advice sentence, wherever `dca_windows` or `check_alerts`
  is described as producing a recommendation: README.md's tool list,
  `skills/watch/SKILL.md` (already added in TA-05, verify it's there),
  START-HERE.md's boundaries section:
  `"This is analysis, not financial advice."`

What changes and what does not:

- README.md: extend "Tools registered:" list (already incrementally
  updated by TA-02 through TA-04; verify all six names are present with
  backticks), add a short new section describing `analyze_asset`,
  `dca_windows`, `set_alert`/`check_alerts`, and `watch`. Keep "You
  approve. It never signs, sends, or trades." and "No trade button. No
  signing. No sending funds." as-is: these are boundary facts, not the
  defensive framing being removed. Add the roadmap sentence to "Where it
  stops," right after those facts, so the sentence reads as "here's the
  boundary today, and here's what's coming," not a replacement for the
  boundary.
- START-HERE.md: extend the "Boundaries" section with the roadmap sentence
  and the not-financial-advice sentence. Add a "Run it on a loop" mention
  of `skills/watch/`, pointing at `skills/watch/SKILL.md` for the full
  invocation.
- docs/ARCHITECTURE.md: extend the pipeline diagram to show the four new
  tools branching off the same `ReadOnlyHost` line, still ending before
  "execution: not exposed." Confirm the tool-versioning and
  execution-rail-enforcement sections' claims ("each tool descriptor
  carries a version field," "`call_tool` raises `PermissionError` for
  execute/execute_dca/submit/sign") still read true with six tools instead
  of four; they should, since TA-02 through TA-04 did not touch that
  rejection set.
- SECURITY.md: add one line to "Product boundary" naming the TA and alert
  tools as read-only and stating they are heuristic, not investment advice.
  No change to the "Secrets and data" or "Reporting a vulnerability"
  sections.
- DATA-AND-PRIVACY.md: add one line noting `fixtures/price_history.json` is
  synthetic (same status as `fixtures/portfolio.json`) and that
  `.scout/alerts.json` (TA-04) is local-only, never transmitted, and
  contains no secrets, only user-chosen thresholds.
- evals/behavioral-evals.md: add one row per new tool, same table format,
  e.g. `Analyze ETH` -> "Report SMA/EMA/RSI/drawdown with the heuristic
  disclosure and freshness gate, never a buy/sell instruction."

## Invariant it must not break

Every boundary fact stated today stays stated: no wallet connect, no
signing, no submission, `approval_state=required`,
`execution_available=false`. `scripts/check_plugin_manifest.py`'s marker
checks (`"### Optional MCP server"`, `"zpm-mcp"`, `"Tools registered:"`,
and all backticked tool names) must still pass after this edit; this is a
docs-prose ticket, not a marker-removal ticket.

## Acceptance check

- `python scripts/check_plugin_manifest.py` exits 0.
- `grep -rl "This is analysis, not financial advice." README.md START-HERE.md skills/watch/`
  finds it in all three.
- `grep -l "Execution is optional and coming" README.md START-HERE.md`
  finds it in both.
- `grep -i "can't touch\|cannot touch\|never touch your money" README.md START-HERE.md docs/ARCHITECTURE.md SECURITY.md DATA-AND-PRIVACY.md`
  finds nothing.
- `pytest -q` still green (`test_quality_gates.py`'s secret scan and
  manifest check are part of the suite).

## Escalation trigger

If the "can't touch your money" framing turns out to live only in
the (since-removed) launch video source (it did, per prior grep of this
tree) and nowhere in the five
named docs, do not invent a phrase to delete just to satisfy the letter of
the brief. State that finding plainly in the PR description and move on to
adding the roadmap sentence, which is the actionable part of this ticket
regardless.

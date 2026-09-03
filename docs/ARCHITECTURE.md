# Architecture

```text
agent runtime / MCP client
  -> ReadOnlyHost (get_portfolio_snapshot | get_pnl | parse_dca_request | preview_dca)
       -> observe: FixturePortfolioReader or optional ZerionAPIReader -> typed PortfolioSnapshot
       -> calculate: PnL calculator -> explainable PnlResult
       -> propose: DCA parser -> partial DcaIntent
       -> preview: complete request -> approval_state=required
       -> execution: not exposed by the host or MCP server
```

The default source is a local synthetic fixture. `zpm-mcp` wraps the same four read-only tools over stdio MCP and selects the source from the environment: the Zerion API only when `ZERION_API_KEY` and `ZERION_WALLET_ADDRESS` are both set, otherwise the fixture. A partial pair is a startup error, and an API failure at call time returns a typed error rather than fixture data. The optional API adapter is an external, read-only data boundary: its availability, authorization, freshness, and response shape depend on the configured Zerion account and endpoint contract.

The package contains a fake execution adapter for isolated domain/test behavior; it is not wired into the host or MCP server and does not move funds.

## Pagination

`ZerionAPIReader` reads two endpoints with different pagination shapes, per Zerion's own
documentation. `GET /wallets/{addr}/positions/` takes no pagination parameters and returns
every position in one call. `GET /wallets/{addr}/transactions/` paginates: the reader
requests `page[size]=100` and follows `links.next` until the API stops returning a next
cursor, bounded by `ZerionAPIReader.MAX_PAGES` (20). Hitting the page cap while a next
cursor is still present, or receiving a malformed or repeated cursor, raises
`ZerionAPIPaginationError` rather than silently truncating the ledger.

## Tool versioning

Each tool descriptor returned by `ReadOnlyHost.tool_manifest()` carries a `version` field,
set to the package version. Deprecation policy: a breaking change to a tool's input or
output schema ships under a new tool name or a new major package version, is announced in
`CHANGELOG.md` under an `Unreleased` or dated entry naming the affected tool, and the prior
schema stays callable for one minor release cycle after the announcement before removal.
This policy is the smallest reasonable default for the current single-consumer surface; it
is a proposal from this docs pass, not a policy validated against production tool
consumers.

## Execution-rail governance review

Ali (commerce-agents specialist) reviewed the safety and execution-rail boundary in this
repo on 2026-09-03, grounded in the codebase and a local fork of
`anthropics/commerce-agents`. The verdict: the stage separation holds in the harness, not
only in the prompt. `ReadOnlyHost.call_tool` raises `PermissionError` by name for
`execute`, `execute_dca`, `submit`, and `sign`, so no tool exists for a model to call past
preview, and `DcaPreview.approval_state` is a pydantic `Literal`, checked at construction,
not a string a caller can talk past. The review also names a gap for Epic C: approval is a
label today, not a host-written record tied to who set it, and recommends building that
record before any real execution adapter replaces the fake one. Full review:
`Career Upgrade/Zerion/50-GOVERNANCE/ALI-EXECUTION-RAIL-REVIEW-2026-09-03.md` in the
project vault.

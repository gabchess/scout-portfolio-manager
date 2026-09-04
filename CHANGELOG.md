# Changelog

## Unreleased

### Added

- The Zerion adapter now reads real per-asset holdings from `GET /wallets/{addr}/positions/` and a mapped transaction ledger from `GET /wallets/{addr}/transactions/`, replacing the earlier single synthetic aggregate holding. Transaction pages follow `links.next` up to `ZerionAPIConfig.max_pages` (default 20). `get_pnl` computes basis from each asset's observed buy transactions.
- Every observe-boundary error now carries a `retryable` flag alongside its error kind, so a caller can decide whether to retry without pattern-matching the message text. A 404 now reports a `not_found` kind, and a 5xx server error honors a `Retry-After` header the same way a 429 rate limit does, when the response actually sends one.
- Each tool listed in `ReadOnlyHost.tool_manifest()` now reports a `version` field. See `docs/ARCHITECTURE.md` for the deprecation policy this enables.
- Every completed DCA preview now carries a `preview_id`, a host-minted id for future audit or idempotency use. It is not an authorization token: the preview still requires `approval_state=required`, and no execute step exists in this package.
- Added a structured log line and an in-process counter, keyed by error kind, for every typed observe-boundary error.

### Changed

- `Holding`, `Transaction`, and `PnlResult` now reject `Infinity`, `NaN`, and boolean or string values coerced into a float field, instead of accepting them silently.
- `ZerionAPIConfig` validates `base_url` when it's constructed: a non-`https` scheme or an unexpected host raises immediately instead of failing later at request time.
- `ReadOnlyHost` now accepts any zero-argument portfolio reader, not only a fixture path, so the optional Zerion adapter can plug in without a separate host implementation.

### Fixed

- `.mcp.json` launched a bare `zpm-mcp` command, which failed with `ENOENT` unless the repo's `.venv/bin` happened to already be on the launching shell's PATH. It now runs `uv run --project ${CLAUDE_PLUGIN_ROOT:-.} --extra mcp zpm-mcp`, which resolves the project and its optional `mcp` extra through `uv` alone, whether the repo is opened directly or installed through the plugin marketplace. `ZPM_FIXTURE_PATH` uses the same `${CLAUDE_PLUGIN_ROOT:-.}` default-syntax prefix, so the fixture resolves correctly either way.
- The optional Zerion API source is now wired through the host and `zpm-mcp`, enabled only when both `ZERION_API_KEY` and `ZERION_WALLET_ADDRESS` are set. A partial pair fails at startup rather than at first call, and an API failure returns a typed error with no silent fallback to the fixture.

## 0.1.0 - 2026-09-03

Early release.

### Added

- A synthetic fixture-backed portfolio reader and explainable USD PnL.
- Explicit DCA intent parsing and approval-required previews.
- A read-only host and an optional stdio MCP server.
- An opt-in, read-only Zerion aggregate portfolio adapter.
- Documentation of the no-wallet, no-signing, no-submission, and no-execution boundary.

Known limits: the default fixture isn't live data. The API adapter exposed only an aggregate observation, not yet a transaction ledger, as of this release. No production availability, endpoint compatibility, or support SLA is claimed.

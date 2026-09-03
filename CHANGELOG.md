# Changelog

## Unreleased

- Replaced the single synthetic `PORTFOLIO` holding with real per-asset holdings from `GET /wallets/{addr}/positions/` and a mapped transaction ledger from `GET /wallets/{addr}/transactions/` (cursor-paginated via `links.next`, bounded by `ZerionAPIReader.MAX_PAGES`). `get_pnl` now computes basis from observed buy transactions per asset.
- Expanded the Zerion error taxonomy with `ZerionAPIPaginationError` (cap hit or broken cursor) and `ZerionAPINotFoundError` (404); `ZerionAPIServerError` (5xx) now reads `Retry-After` the same way `ZerionAPIRateLimitError` does.
- `Holding`, `Transaction`, and `PnlResult` now reject `Infinity`, `NaN`, and boolean/string values coerced into float fields instead of silently accepting them.
- `ZerionAPIConfig` validates `base_url` at construction: a non-`https` scheme or an unexpected host raises `ValueError` immediately instead of failing at request time.
- Each tool descriptor in `ReadOnlyHost.tool_manifest()` now carries a `version` field; see `docs/ARCHITECTURE.md` for the deprecation policy.
- Added a structured log line and an in-process counter, keyed by `error.kind`, for every typed observe-boundary error.
- Fixed `.mcp.json` launching a bare `zpm-mcp` command, which failed with `ENOENT` unless the repo's `.venv/bin` happened to be on the launching shell's PATH. It now runs `uv run --project . --extra mcp zpm-mcp`, which resolves the project and its optional `mcp` extra from `uv` alone. `ZPM_FIXTURE_PATH` is now a plain relative path (`fixtures/portfolio.json`) instead of a `${CLAUDE_PLUGIN_ROOT}`-prefixed one, since that placeholder is unset when this repo is opened directly as a Claude Code project rather than installed through the plugin marketplace.
- Wired the read-only Zerion adapter through the host and `zpm-mcp`. Enabled only when `ZERION_API_KEY` and `ZERION_WALLET_ADDRESS` are both set; a partial pair fails at startup, and API failures return typed errors with no fixture fallback.
- `ReadOnlyHost` now accepts any zero-argument portfolio reader in addition to a fixture path.

## 0.1.0 — 2026-09-03

Early public release.

- Added a synthetic fixture-backed portfolio reader and explainable USD PnL.
- Added explicit DCA intent parsing and approval-required previews.
- Added a read-only host and optional stdio MCP server.
- Added an opt-in, read-only Zerion aggregate portfolio adapter.
- Documented the no-wallet, no-signing, no-submission, and no-execution boundary.

Known limits: the default fixture is not live data; the API adapter exposes an aggregate observation rather than a transaction ledger; no production availability, endpoint compatibility, or support SLA is claimed.

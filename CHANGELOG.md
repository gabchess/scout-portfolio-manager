# Changelog

## Unreleased

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

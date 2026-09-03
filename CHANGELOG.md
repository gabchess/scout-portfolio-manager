# Changelog

## 0.1.0 — 2026-09-03

Early public release.

- Added a synthetic fixture-backed portfolio reader and explainable USD PnL.
- Added explicit DCA intent parsing and approval-required previews.
- Added a read-only host and optional stdio MCP server.
- Added an opt-in, read-only Zerion aggregate portfolio adapter.
- Documented the no-wallet, no-signing, no-submission, and no-execution boundary.

Known limits: the default fixture is not live data; the API adapter exposes an aggregate observation rather than a transaction ledger; no production availability, endpoint compatibility, or support SLA is claimed.

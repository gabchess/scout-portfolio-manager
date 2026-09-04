# Release honesty: what is incomplete or can break

This file records important limits so the release is not mistaken for a production wallet or trading integration.

- The default data is synthetic and may be stale by design; it is not a live portfolio.
- The optional Zerion adapter relies on the configured endpoint, credentials, permissions, rate limits, network, and response shape. A successful request is not a guarantee of complete or current data.
- The adapter now maps real per-asset holdings and a transaction ledger from Zerion's positions and transactions endpoints, replacing the earlier single synthetic `PORTFOLIO` holding. It still does not invent an acquisition basis: an asset with no observed buy transaction reports a missing basis instead.
- Transaction pagination is bounded by `ZerionAPIConfig.max_pages` (default 20 pages of `page[size]=100`, overridable per deployment; no upper bound is enforced beyond a positive integer). A wallet with a longer history than the configured bound raises a typed pagination error rather than returning a silently truncated ledger.
- `retry_after_seconds` on rate-limit errors is parsed and exposed on the exception for the caller to act on; this package performs no automatic retry or backoff itself.
- The adapter's transaction request filters `operation_types` to `trade,send,receive` at fetch time; the other 12 of Zerion's 15 documented operation types (approve, bid, burn, claim, delegate, deploy, deposit, execute, mint, revoke, revoke_delegation, withdraw) are never requested, not filtered after arrival, so DeFi actions like staking, lending, and approvals do not appear in the ledger at all.
- Positions and transactions responses are mapped defensively: a position with no resolvable symbol, or a transaction with an unmapped transfer direction or a missing quantity/value, is skipped with a logged warning rather than guessed at.
- DCA parsing and previews do not submit, sign, execute, or verify settlement. A preview is not evidence that an order occurred.
- The package contains a fake execution adapter for isolated domain behavior; it is not connected to the host or MCP server and does not touch funds.
- No production deployment, uptime target, support SLA, investment advice, or Zerion endorsement is claimed.
- The `quantity` field on positions and transactions responses is confirmed by Zerion's own API reference to always be the object `{int, decimals, float, numeric}`, never a bare number; `_numeric_amount()` already reads `.get("float")` off that object, so no code change was needed here. The earlier "moderate confidence, live-unconfirmed" caveat was a stale doc note, not an open risk.

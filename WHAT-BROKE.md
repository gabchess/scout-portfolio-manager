# Release honesty: what is incomplete or can break

This file records important limits so the release is not mistaken for a production wallet or trading integration.

- The default data is synthetic and may be stale by design; it is not a live portfolio.
- The optional Zerion adapter relies on the configured endpoint, credentials, permissions, rate limits, network, and response shape. A successful request is not a guarantee of complete or current data.
- The adapter now maps real per-asset holdings and a transaction ledger from Zerion's positions and transactions endpoints, replacing the earlier single synthetic `PORTFOLIO` holding. It still does not invent an acquisition basis: an asset with no observed buy transaction reports a missing basis instead.
- Transaction pagination is bounded by `ZerionAPIReader.MAX_PAGES` (20 pages of `page[size]=100`). A wallet with a longer history than that bound raises a typed pagination error rather than returning a silently truncated ledger.
- Positions and transactions responses are mapped defensively: a position with no resolvable symbol, or a transaction with an unmapped operation type, an unmapped transfer direction, or a missing quantity/value, is skipped with a logged warning rather than guessed at.
- DCA parsing and previews do not submit, sign, execute, or verify settlement. A preview is not evidence that an order occurred.
- The package contains a fake execution adapter for isolated domain behavior; it is not connected to the host or MCP server and does not touch funds.
- No production deployment, uptime target, support SLA, investment advice, or Zerion endorsement is claimed.

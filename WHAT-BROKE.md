# Release honesty: what is incomplete or can break

This file records important limits so the release is not mistaken for a production wallet or trading integration.

- The default data is synthetic and may be stale by design; it is not a live portfolio.
- The optional Zerion adapter relies on the configured endpoint, credentials, permissions, rate limits, network, and response shape. A successful request is not a guarantee of complete or current data.
- The adapter maps the aggregate portfolio to one holding and does not invent asset-level cost basis or transaction history.
- DCA parsing and previews do not submit, sign, execute, or verify settlement. A preview is not evidence that an order occurred.
- The package contains a fake execution adapter for isolated domain behavior; it is not connected to the host or MCP server and does not touch funds.
- No production deployment, uptime target, support SLA, investment advice, or Zerion endorsement is claimed.

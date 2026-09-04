# Show me: runtime shape

Multi-wallet Zerion calls hit real 429 storms in production. Teams fanning out across chains and wallets have shipped that failure mode before: a blank chart, a missing wallet row, no way to tell a rate limit from an empty portfolio.

This host makes that state typed and retryable, not a silent blank chart. A `rate_limit` error carries `Retry-After`. A snapshot never goes quiet.

It also stays quota-light. One full snapshot costs about 21 calls, 1.05% of the free daily quota, because PnL is computed from positions and transactions instead of the metered PnL endpoint.

Point it at Zerion's own API for one wallet, read-only, or a fixture with no key at all. It returns a typed portfolio snapshot, PnL with the acquisition basis shown or flagged missing, and a DCA preview a human still approves elsewhere.

The agent never gets a tool that can sign or send. That's not a promise. Tool names like `execute`, `sign`, and `submit` don't exist in this host at all, so there is nothing for a prompt to talk it into calling. The boundary is structural, not stated.

```text
Synthetic fixture (default) or optional read-only API source
  -> ReadOnlyHost.get_portfolio_snapshot()
  -> PortfolioSnapshot
  -> ReadOnlyHost.get_pnl()
  -> PnlResult

DCA text
  -> ReadOnlyHost.parse_dca_request()
  -> partial DcaIntent
  -> clarification, never inference
  -> ReadOnlyHost.preview_dca()
  -> approval_state = required
  -> execution_available = false
```

The important boundary is:

```text
proposal != submission != confirmation != verification
```

The host and MCP server do not connect to a wallet, sign, submit, or execute. The optional API adapter only observes an aggregate portfolio.

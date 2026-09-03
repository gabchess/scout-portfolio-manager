# Show me: runtime shape

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

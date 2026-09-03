# Show me: runtime shape

```text
Fixture JSON
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
  -> (host stops here; no execute tool)
  -> FakeExecutionAdapter.execute()   # separate, non-host path only
  -> SettlementVerifier.verify(readback)
```

The important boundary is that submission is not settlement:

```text
submitted != confirmed != verified
```

No class in this MVP connects to a wallet or network.

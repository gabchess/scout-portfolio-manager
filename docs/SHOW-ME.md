# Show me: runtime shape

```text
Fixture JSON
  -> FixturePortfolioReader.observe()
  -> PortfolioSnapshot
  -> read_intent("What is my PnL?")
  -> PnlResult

DCA text
  -> parse_dca_request()
  -> partial DcaIntent
  -> clarification, never inference
  -> build_preview()
  -> approval_state = required
  -> FakeExecutionAdapter.execute()
  -> SettlementVerifier.verify(readback)
```

The important boundary is that submission is not settlement:

```text
submitted != confirmed != verified
```

No class in this MVP connects to a wallet or network.

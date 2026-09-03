# Architecture

```text
agent runtime
  -> observe: FixturePortfolioReader -> typed PortfolioSnapshot
  -> calculate: PnL calculator -> explainable PnlResult
  -> propose: DCA parser -> partial DcaIntent
  -> approve: preview requires explicit approval state
  -> execute: FakeExecutionAdapter only
  -> verify: SettlementVerifier reads evidence independently
```

The MVP intentionally has no network boundary. A future Zerion adapter belongs behind the observe interface. A future execution rail belongs behind the fake adapter interface and requires a separately approved authority design.

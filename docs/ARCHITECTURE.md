# Architecture

```text
agent runtime / MCP client
  -> ReadOnlyHost (get_portfolio_snapshot | get_pnl | parse_dca_request | preview_dca)
       -> observe: FixturePortfolioReader -> typed PortfolioSnapshot
       -> calculate: PnL calculator -> explainable PnlResult
       -> propose: DCA parser -> partial DcaIntent
       -> approve: preview requires explicit approval state
  -> execute: NOT on host; FakeExecutionAdapter only, separate authority
  -> verify: SettlementVerifier reads evidence independently
```

The read-only host is the preferred agent boundary. Optional `zpm-mcp` wraps the same four tools over stdio MCP. The MVP intentionally has no network boundary. A future Zerion adapter belongs behind the observe interface. A future execution rail belongs behind the fake adapter interface and requires a separately approved authority design.

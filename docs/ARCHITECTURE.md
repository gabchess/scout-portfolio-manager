# Architecture

```text
agent runtime / MCP client
  -> ReadOnlyHost (get_portfolio_snapshot | get_pnl | parse_dca_request | preview_dca)
       -> observe: FixturePortfolioReader or optional ZerionAPIReader -> typed PortfolioSnapshot
       -> calculate: PnL calculator -> explainable PnlResult
       -> propose: DCA parser -> partial DcaIntent
       -> preview: complete request -> approval_state=required
       -> execution: not exposed by the host or MCP server
```

The default source is a local synthetic fixture. `zpm-mcp` wraps the same four read-only tools over stdio MCP and selects the source from the environment: the Zerion API only when `ZERION_API_KEY` and `ZERION_WALLET_ADDRESS` are both set, otherwise the fixture. A partial pair is a startup error, and an API failure at call time returns a typed error rather than fixture data. The optional API adapter is an external, read-only data boundary: its availability, authorization, freshness, and response shape depend on the configured Zerion account and endpoint contract.

The package contains a fake execution adapter for isolated domain/test behavior; it is not wired into the host or MCP server and does not move funds.

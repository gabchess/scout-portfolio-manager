# Tool reference

The plugin's optional MCP server exposes four tools:

| Tool | Purpose | Writes or executes? |
|---|---|---|
| `get_portfolio_snapshot` | Read the current fixture or configured read-only snapshot | No |
| `get_pnl` | Calculate explainable USD PnL, optionally filtered by asset | No |
| `parse_dca_request` | Extract explicit DCA fields and missing-field questions | No |
| `preview_dca` | Build a proposal with assumptions and safety checks | No |

The fixture path is controlled by `ZPM_FIXTURE_PATH`. The packaged default is
`${CLAUDE_PLUGIN_ROOT}/fixtures/portfolio.json` when launched through the plugin MCP config.

The read-only Zerion source is enabled only when `ZERION_API_KEY` and `ZERION_WALLET_ADDRESS` are both set in the MCP server environment. `ZERION_CHAIN` is an optional label. Setting only one of the two required variables is an error and the server does not start. When enabled, the snapshot reports `source.kind = "zerion_api"`, one aggregate `PORTFOLIO` holding, and no transactions; API failures come back as `status: "error"` with `fallback: "none"`. Say which source was used when reporting results.

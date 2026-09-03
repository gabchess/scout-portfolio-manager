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

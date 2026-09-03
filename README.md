# Zerion Portfolio Intelligence

A read-only portfolio intelligence plugin and Python package for portfolio snapshots, explainable USD PnL, DCA intent clarification, and approval-required previews.

The default source is the synthetic fixture at `fixtures/portfolio.json`. An optional `ZerionAPIReader` can read one wallet's aggregate portfolio through an explicitly configured, read-only Zerion API connection. The adapter does not submit transactions or expose credentials in results.

## Safety boundary

This project does not connect to wallets, use or move funds, sign transactions, submit transactions, or provide investment advice. A preview is a proposal, not a completed transaction.

The product keeps these stages distinct:

`observe != calculate != propose != approve != execute != verify`

No execution or signing tool is provided by the host or MCP server.

## Quick start

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[test]'
.venv/bin/pytest -q
```

The fixture contains 1 ETH bought for $2,000 and valued at $2,250, producing a transparent $250 unrealized gain. Fixture values are examples, not live market data.

## Python API

```python
from pathlib import Path
from zerion_portfolio_manager.portfolio import FixturePortfolioReader
from zerion_portfolio_manager.intents import read_intent

snapshot = FixturePortfolioReader(Path("fixtures/portfolio.json")).snapshot()
answer = read_intent("What is my PnL?", snapshot)
```

The read-only host exposes observations, calculations, intent parsing, and previews:

```python
from zerion_portfolio_manager.host import ReadOnlyHost

host = ReadOnlyHost("fixtures/portfolio.json")
host.get_portfolio_snapshot()
host.get_pnl()
host.parse_dca_request("DCA another $300 of ETH")
host.preview_dca(
    "DCA $300 ETH on ethereum weekly from wallet:0xabc123 to wallet:0xdef456"
)
```

DCA previews require amount, asset, chain, schedule, source, and destination. Missing details are returned for clarification rather than inferred. A complete preview remains `approval_state=required` and `execution_available=false`.

## Optional Zerion API adapter

The package includes an opt-in, read-only adapter for the aggregate wallet portfolio endpoint. Configure `ZerionAPIConfig` with an API key supplied by your own secret manager; do not paste keys into source, fixtures, prompts, or issue reports. The adapter returns an aggregate holding and does not provide transaction history or execution capabilities. See [`DATA-AND-PRIVACY.md`](DATA-AND-PRIVACY.md) and [`SECURITY.md`](SECURITY.md).

The adapter depends on the endpoint contract and access permitted by your Zerion account. It is not enabled by the default fixture or MCP configuration.

### Optional MCP server

```bash
.venv/bin/pip install -e '.[mcp]'
.venv/bin/zpm-mcp
```

Tools registered: `get_portfolio_snapshot`, `get_pnl`, `parse_dca_request`, `preview_dca`. The default remains fixture-backed and offline.

Tools registered: `get_portfolio_snapshot`, `get_pnl`, `parse_dca_request`, and `preview_dca`. Set `ZPM_FIXTURE_PATH` to use another local fixture. No wallet, signing, submission, execution, or settlement-verification tool is registered.

## Claude Code plugin

This repository is also a Claude Code plugin for read-only portfolio intelligence. Local installation and commands are documented in [`PLUGIN-START-HERE.md`](PLUGIN-START-HERE.md).

## Documentation

- [`START-HERE.md`](START-HERE.md) — install and first use
- [`SECURITY.md`](SECURITY.md) — security boundary and reporting guidance
- [`DATA-AND-PRIVACY.md`](DATA-AND-PRIVACY.md) — data handling and API-adapter considerations
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — runtime boundary
- [`docs/SHOW-ME.md`](docs/SHOW-ME.md) — request and preview flow
- [`CHANGELOG.md`](CHANGELOG.md) — release history
- [`SUPPORT.md`](SUPPORT.md) — questions and issue reports

## Status

Version `0.1.0` is an early release: fixture-backed functionality, a read-only host, an optional read-only API adapter, and an optional read-only MCP server. Treat API-backed observations as external data with freshness, availability, and authorization limits.

# Zerion Agentic Portfolio Manager

A portable, fixture-backed MVP for the agentic crypto operator. It answers portfolio and PnL questions, parses a user-directed DCA request, produces a complete preview, and simulates execution through a fake adapter.

## Safety boundary

This repository does not connect to wallets, use real funds, request credentials, sign transactions, or call Zerion. It is not investment advice or an autonomous trader.

The code keeps these boundaries explicit:

`observe != calculate != propose != approve != execute != verify`

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'
.venv/bin/pytest -q
```

The deterministic fixture is `fixtures/portfolio.json`. The current example contains 1 ETH bought for $2,000 and valued at $2,250, producing a transparent $250 unrealized gain.

## Example surfaces

```python
from pathlib import Path
from zerion_portfolio_manager.portfolio import FixturePortfolioReader
from zerion_portfolio_manager.intents import read_intent

snapshot = FixturePortfolioReader(Path("fixtures/portfolio.json")).snapshot()
answer = read_intent("What is my PnL?", snapshot)
```

### Read-only host adapter

Agent runtimes should prefer the host surface. It exposes only observe, calculate, propose, and preview:

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

There is no execute tool on the host. `call_tool("execute", ...)` raises `PermissionError`.

### Optional MCP server

```bash
.venv/bin/pip install -e '.[mcp]'
.venv/bin/zpm-mcp
```

Tools registered: `get_portfolio_snapshot`, `get_pnl`, `parse_dca_request`, `preview_dca`. Fixture path override: `ZPM_FIXTURE_PATH`.

DCA requests remain incomplete until the user explicitly supplies chain, schedule, source, and destination. The fake adapter requires explicit approval, rejects stale quotes and unsafe destinations, protects idempotency keys, and never establishes settlement by itself. `SettlementVerifier` requires independent transaction plus portfolio readback evidence.

## Project status

Local MVP and read-only host adapter are implemented. This is not a production Zerion integration. See `IMPLEMENTATION-PLAN.md` for the dependency graph and evidence gates. No public push, deployment, outreach, or real execution is authorized by this repository.

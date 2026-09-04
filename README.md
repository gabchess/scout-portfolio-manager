# Scout

A read-only agent for one wallet. It watches, calculates, and proposes DCA plans. You approve.

Scout is a Python package and Claude Code plugin built on the Zerion API. The default source is the synthetic fixture at `fixtures/portfolio.json`; an optional `ZerionAPIReader` can read one real wallet's holdings and transaction ledger through an explicitly configured, read-only Zerion API connection. The adapter does not submit transactions or expose credentials in results.

## The problem

> I bought the dip. I don't know what I paid, when, or on which chain.

Scout shows your activity, where your money is, and your PnL if you ask.

## "What's the PnL, Scout?"

Scout answers with cost basis and current value, not a guess:

- Cost basis: 1 ETH bought for $2,000 on Aug 3, 2026.
- Current value: ETH at $2,250 in this snapshot (Sept 3, 2026).
- Result: +12.5%, current value minus basis minus fees.

The fixture at [`fixtures/portfolio.json`](fixtures/portfolio.json) backs these numbers by default. See [Quick start](#quick-start) to run it yourself.

## "DCA $300 into ETH, weekly"

Ask Scout for a DCA plan and it drafts a complete proposal: asset, amount, chain, and schedule.

Status: approval required. Scout stops here.

## Video

A short video walkthrough covers the same two minutes: the problem, the PnL question, and the DCA proposal.

<!-- TODO: link to video render once Colin's pass lands -->
Provisional path: `video/out/ScoutVideo.mp4`

## Safety boundary

Scout does not connect wallets, move funds, sign, submit, or execute transactions, or provide investment advice. A preview is a proposal, not a completed transaction. `observe != calculate != propose != approve != execute != verify`, and no execution or signing tool is registered on the host or MCP server. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how that boundary is enforced in code.

## Quick start

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[test,mcp]'
.venv/bin/pytest -q
```

The `mcp` extra is required for the full test suite to pass, since some tests exercise the optional MCP server.

The fixture contains 1 ETH bought for $2,000 and valued at $2,250, producing a transparent $250 unrealized gain. Fixture values are examples, not live market data.

## Demo

A browser demo lives at `demo/zerion-portfolio-agent/`, a small stdlib-only Python server plus a static page that renders this repo's agent loop: portfolio snapshot, explainable PnL, and a DCA chat that ends at a preview a human still approves. It runs entirely on the fixture wallet. No Zerion API key is needed.

![Zerion Portfolio Agent demo, dashboard with portfolio snapshot, PnL, and a completed DCA preview showing approval_state required and execution_available false](docs/zerion-portfolio-demo-screenshot.png)

See [`demo/zerion-portfolio-agent/README.md`](demo/zerion-portfolio-agent/README.md) for run instructions.

## Python API

```python
from pathlib import Path
from scout_portfolio_manager.portfolio import FixturePortfolioReader
from scout_portfolio_manager.intents import read_intent

snapshot = FixturePortfolioReader(Path("fixtures/portfolio.json")).snapshot()
answer = read_intent("What is my PnL?", snapshot)
```

The read-only host exposes observations, calculations, intent parsing, and previews:

```python
from scout_portfolio_manager.host import ReadOnlyHost

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

The package includes an opt-in, read-only adapter for the wallet positions and transactions endpoints. Configure `ZerionAPIConfig` with an API key supplied by your own secret manager; do not paste keys into source, fixtures, prompts, or issue reports. The adapter returns per-asset holdings and a mapped transaction ledger; it does not provide execution capabilities. See [`DATA-AND-PRIVACY.md`](DATA-AND-PRIVACY.md) and [`SECURITY.md`](SECURITY.md).

The adapter depends on the endpoint contract and access permitted by your Zerion account. It is not enabled by the default fixture or MCP configuration.

### Enabling the Zerion source for the host and MCP server

The host and `zpm-mcp` read the source from the environment at startup. Both variables are required; setting only one is a configuration error, and the server exits with a message that names the missing variable and never echoes the key.

| Variable | Required | Meaning |
|---|---|---|
| `ZERION_API_KEY` | yes | Read-only Zerion API key from your secret manager |
| `ZERION_WALLET_ADDRESS` | yes | The one wallet address to observe |
| `ZERION_CHAIN` | no | Label stored on the snapshot; defaults to `multi-chain` |
| `ZPM_FIXTURE_PATH` | no | Local fixture used only when the Zerion source is not enabled |

```bash
export ZERION_API_KEY=$(cat ~/secrets/zerion-api-key)   # never paste the value inline
export ZERION_WALLET_ADDRESS=0xYourWalletAddress
.venv/bin/zpm-mcp
```

When enabled, `get_portfolio_snapshot` returns `source.kind = "zerion_api"` with real per-asset holdings and a transaction ledger mapped from Zerion's `trade`, `send`, and `receive` operation types. `get_pnl` computes basis from observed buy transactions per asset; an asset with no observed buy reports a missing acquisition basis rather than an invented one. If the API rejects the key, rate-limits, hits a pagination fault, or fails, the tools return `status: "error"` with a typed `error.kind` and `fallback: "none"`. The fixture is never served in place of a failed API call.

Python callers can do the same without environment variables:

```python
from scout_portfolio_manager.host import ReadOnlyHost
from scout_portfolio_manager.zerion_api import ZerionAPIConfig, ZerionAPIReader, ZerionWalletReader

reader = ZerionWalletReader(ZerionAPIReader(ZerionAPIConfig(api_key=key_from_secret_manager)), wallet)
host = ReadOnlyHost(reader)
```

### Optional MCP server

```bash
.venv/bin/pip install -e '.[mcp]'
.venv/bin/zpm-mcp
```

Tools registered: `get_portfolio_snapshot`, `get_pnl`, `parse_dca_request`, `preview_dca`. The default remains fixture-backed and offline. Set `ZPM_FIXTURE_PATH` to use another local fixture, or set both `ZERION_API_KEY` and `ZERION_WALLET_ADDRESS` to observe one real wallet read-only (see above). No wallet, signing, submission, execution, or settlement-verification tool is registered.

## Install as a plugin

This repository is also a Claude Code plugin, with an Agent Skills-compatible Codex layout, for read-only portfolio intelligence. Every install route (Claude Code plugin, Codex, or plain Python) is documented in [`START-HERE.md`](START-HERE.md).

## Documentation

- [`START-HERE.md`](START-HERE.md): install and first use
- [`SECURITY.md`](SECURITY.md): security boundary and reporting guidance
- [`DATA-AND-PRIVACY.md`](DATA-AND-PRIVACY.md): data handling and API-adapter considerations
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): runtime boundary
- [`docs/SHOW-ME.md`](docs/SHOW-ME.md): request and preview flow
- [`CHANGELOG.md`](CHANGELOG.md): release history
- [`SUPPORT.md`](SUPPORT.md): questions and issue reports

## Status

Version `0.2.0` is an early release: fixture-backed functionality, a read-only host, an optional read-only API adapter, and an optional read-only MCP server. Treat API-backed observations as external data with freshness, availability, and authorization limits.

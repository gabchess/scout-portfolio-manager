# Start here

## 1. Install

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[test,mcp]'
```

Python 3.11 or newer is required. The MCP extra is optional if you only use the Python host or Claude Code command.

## 2. Verify the install

```bash
.venv/bin/pytest -q
```

## 3. Try the fixture-backed host

```bash
.venv/bin/python - <<'PY'
from zerion_portfolio_manager.host import ReadOnlyHost

host = ReadOnlyHost("fixtures/portfolio.json")
print(host.get_pnl())
print(host.parse_dca_request("DCA another $300 of ETH"))
PY
```

The default fixture is synthetic. It is the default data source and is not live portfolio data.

## 4. Use the Claude Code plugin locally

```text
/plugin marketplace add /path/to/zerion-portfolio-manager
/plugin install zerion-portfolio-intelligence@zerion-portfolio-manager
```

Then try:

```text
/portfolio-intelligence What is my PnL?
/portfolio-intelligence Preview a DCA request for $300 of ETH every week
```

See [`PLUGIN-START-HERE.md`](PLUGIN-START-HERE.md) for plugin details.

## 5. Optional MCP server

```bash
.venv/bin/zpm-mcp
```

The server exposes only `get_portfolio_snapshot`, `get_pnl`, `parse_dca_request`, and `preview_dca`. Set `ZPM_FIXTURE_PATH` to point to another local fixture.

## Boundaries

DCA previews require amount, asset, chain, schedule, source, and destination. Missing fields are clarified, never guessed. A complete preview is approval-required and does not execute.

This release does not provide wallet connection, signing, transaction submission, execution, or settlement verification. Never add API keys, private keys, seed phrases, or wallet secrets to this repository, prompts, fixtures, or logs. For data handling and security details, read [`DATA-AND-PRIVACY.md`](DATA-AND-PRIVACY.md) and [`SECURITY.md`](SECURITY.md).

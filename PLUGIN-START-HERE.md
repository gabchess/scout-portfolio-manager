# Claude Code plugin onboarding

## Install the Python package

From this repository:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[test,mcp]'
.venv/bin/pytest -q
```

The package install provides the `zpm-mcp` command used by `.mcp.json`.

## Load the plugin locally

In Claude Code, add the repository as a local marketplace, then install the listed plugin:

```text
/plugin marketplace add /path/to/zerion-portfolio-manager
/plugin install zerion-portfolio-intelligence@zerion-portfolio-manager
```

The exact CLI spelling can vary by Claude Code release. The marketplace file is kept beside
the plugin manifest so local installation by name has a catalog entry.

## Use it

```text
/portfolio-intelligence What is my PnL?
/portfolio-intelligence Preview a DCA request for $300 of ETH every week
```

The optional MCP server starts with the fixture at `fixtures/portfolio.json`. To use another
fixture, set `ZPM_FIXTURE_PATH` in the host environment. The default fixture is synthetic.

## Boundaries

This plugin reads portfolio-shaped data, calculates PnL, parses intent, and creates previews.
It does not connect wallets, sign, submit, execute, or verify settlement. It never needs a
signing key or recovery phrase. An API adapter, if separately configured, is read-only and must
be treated as an external data source with its own freshness and authorization limits.

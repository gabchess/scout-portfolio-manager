# Start here

Scout is a read-only portfolio intelligence package: fixture-backed by default, with an optional read-only Zerion API adapter. This file is the exact install route for the harness you are on. Pick one.

Current version: `0.2.0`, an early release. See [`RELEASE-MANIFEST.json`](RELEASE-MANIFEST.json) for what it proves and does not prove.

## What installing this package does and does not authorize

Installing Scout, by any route below, authorizes only local package installation: copying files, registering a plugin or skill with the host, and running the fixture-backed Python code.

It does **not** authorize:

- a live Zerion API key, a wallet connection, or any network call. The default source is the synthetic fixture at `fixtures/portfolio.json`; the optional Zerion adapter activates only when an operator explicitly sets both `ZERION_API_KEY` and `ZERION_WALLET_ADDRESS` (see [`DATA-AND-PRIVACY.md`](DATA-AND-PRIVACY.md));
- signing, submitting, or executing any transaction. No component in this package has an execute, sign, or submit code path;
- a background service, a scheduled task, or persistent state. Nothing in this package runs unless a host explicitly invokes its tools or a caller runs its server process.

## Route 1: Claude Code plugin (local marketplace)

From a terminal, with the Claude Code CLI installed:

```bash
claude plugin marketplace add /path/to/scout-portfolio-manager
claude plugin install scout-portfolio@scout-portfolio-manager
```

`marketplace.json`, not `plugin.json`, is the catalog `claude plugin marketplace add` reads; the repository ships both so installation by name works. The exact CLI spelling can vary by Claude Code release. Inside an already-running Claude Code session, the equivalent slash-command form also works:

```text
/plugin marketplace add /path/to/scout-portfolio-manager
/plugin install scout-portfolio@scout-portfolio-manager
```

Then try:

```text
/scout-portfolio:portfolio-intelligence What is my PnL?
/scout-portfolio:portfolio-intelligence Preview a DCA request for $300 of ETH every week
```

Claude Code launches the bundled MCP server itself, through `.mcp.json`, which runs `uv run --project ${CLAUDE_PLUGIN_ROOT:-.} --extra mcp zpm-mcp`. This needs `uv` on the launching shell's PATH; no separate `pip install` or PATH setup for the package itself is required for this route.

## Route 2: Codex (Agent Skills layout)

The repository also ships a Codex-compatible plugin layout under `codex/`, generated from the same canonical source as the Claude Code plugin.

```bash
codex plugin marketplace add /path/to/scout-portfolio-manager/codex/.agents/plugins
codex plugin add scout-portfolio --marketplace scout-portfolio-manager
codex plugin list
```

Use the path syntax your operating system and shell expect. The exact CLI flags can vary by Codex release; if a command above fails, run `codex plugin --help` and adjust the verb, not the marketplace path. Restart the host and open a new session after changing plugin state.

## Route 3: Plain Python (no plugin host)

```bash
uv sync --extra test --extra mcp
uv run pytest -q
```

Or without `uv`:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[test,mcp]'
.venv/bin/pytest -q
```

Python 3.11 or newer is required. Try the fixture-backed host directly:

```bash
uv run python - <<'PY'
from scout_portfolio_manager.host import ReadOnlyHost

host = ReadOnlyHost("fixtures/portfolio.json")
print(host.get_pnl())
print(host.parse_dca_request("DCA another $300 of ETH"))
PY
```

The default fixture is synthetic. It is the default data source, not live portfolio data.

To run the optional MCP server directly, without a plugin host:

```bash
uv run --extra mcp zpm-mcp
```

The server exposes `get_portfolio_snapshot`, `get_pnl`, `parse_dca_request`, `preview_dca`, `analyze_asset`, `dca_windows`, `set_alert`, and `check_alerts`. Set `ZPM_FIXTURE_PATH` to point at another local fixture.

## Try the browser demo (any route)

```bash
uv run --project . demo/zerion-portfolio-agent/server.py
```

Then open `http://127.0.0.1:8787`. The demo runs entirely offline on the fixture; it never reads `ZERION_API_KEY`. See [`demo/zerion-portfolio-agent/README.md`](demo/zerion-portfolio-agent/README.md).

## Enable the Zerion API adapter (any route)

By default Scout reads the local fixture. To read one real wallet instead, set both environment variables below before starting the host, `zpm-mcp`, or the plugin. Setting only one is a configuration error; the process exits and names the missing variable without ever echoing the key.

| Variable | Required | Meaning |
|---|---|---|
| `ZERION_API_KEY` | yes | Read-only Zerion API key from your own secret manager. |
| `ZERION_WALLET_ADDRESS` | yes | The one wallet address to observe. |
| `ZERION_CHAIN` | no | Label stored on the snapshot; defaults to `multi-chain`. |
| `ZPM_FIXTURE_PATH` | no | Local fixture used only when the Zerion source is not enabled. |

```bash
export ZERION_API_KEY=$(cat ~/secrets/zerion-api-key)   # never paste the value inline
export ZERION_WALLET_ADDRESS=0xYourWalletAddress
uv run --extra mcp zpm-mcp
```

Once enabled, `get_pnl` computes cost basis from each asset's observed buy transactions; an asset with no observed buy reports a missing basis rather than an invented one. If the Zerion API rejects the key, rate-limits, or fails outright, the tools return a typed error. The fixture never fills in for a failed API call.

Python callers can set the same thing directly, without environment variables:

```python
from scout_portfolio_manager.host import ReadOnlyHost
from scout_portfolio_manager.zerion_api import ZerionAPIConfig, ZerionAPIReader, ZerionWalletReader

reader = ZerionWalletReader(ZerionAPIReader(ZerionAPIConfig(api_key=key_from_secret_manager)), wallet)
host = ReadOnlyHost(reader)
```

Full data-handling detail: [`DATA-AND-PRIVACY.md`](DATA-AND-PRIVACY.md).

## Run it on a loop

[`skills/watch/SKILL.md`](skills/watch/SKILL.md) chains all read-only tools into one
on-demand pass, observe through alert, and writes a static HTML report. Each run is a
fresh process; alert rules persist in `.scout/alerts.json` on disk, not in memory. This
is the shape built for a Claude Code `/loop` tick. See that file for the exact command
and output contract.

## Boundaries

`observe != calculate != propose != approve != execute != verify`. DCA previews require amount, asset, chain, schedule, source, and destination. Missing fields are clarified, never guessed. A complete preview is `approval_state=required` and `execution_available=false`; wallet handoff and execution are a future product direction, not a current capability. See [`docs/SHOW-ME.md`](docs/SHOW-ME.md) for the full request-and-preview flow.

Execution is optional and coming: Scout will DCA for you or just alert you, your choice. Until then, `dca_windows` and `check_alerts` only classify and report: "This is analysis, not financial advice."

Never add API keys, private keys, seed phrases, or wallet secrets to this repository, prompts, fixtures, or logs. For the full data and security boundary, read [`DATA-AND-PRIVACY.md`](DATA-AND-PRIVACY.md) and [`SECURITY.md`](SECURITY.md). If installation or discovery fails, continue with [`SUPPORT.md`](SUPPORT.md).

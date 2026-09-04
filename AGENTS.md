# AGENTS.md

Give an agent this repository folder or ZIP. Install Scout. Do not invent capabilities from marketing copy. Read [`CLAIMS.md`](CLAIMS.md) before repeating product claims.

## Install routes

1. Claude Code: [`START-HERE.md`](START-HERE.md) Route 1 (`scout-portfolio@scout-portfolio-manager`).
2. Codex: Route 2 under `codex/`.
3. Plain Python: Route 3 (`uv sync` / venv). Package version **0.3.0**.
4. Cursor or any MCP client: merge [`.mcp.json`](.mcp.json) into the host MCP config (or copy to `.cursor/mcp.json`). Needs `uv` on PATH. Starts `zpm-mcp` over stdio.

Discovery is not the same as copy. After install, ask the host to list MCP tools or run `/portfolio-intelligence What is my PnL?`.

## Do

- Use the fixture by default.
- Treat Zerion as optional and read-only when both `ZERION_API_KEY` and `ZERION_WALLET_ADDRESS` are set.
- Keep DCA incomplete fields as clarification, never guessed.

## Do not

- Post, spend, or call live Zerion unless the operator set both env vars.
- Claim channel push alerts, WalletConnect, or automated buys.
- Call execute, sign, or submit. Those tools are not available.
- Paste secrets into the repo, prompts, fixtures, or logs.

## Honesty

See [`CLAIMS.md`](CLAIMS.md), [`SECURITY.md`](SECURITY.md), [`DATA-AND-PRIVACY.md`](DATA-AND-PRIVACY.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

# Start here

1. Create the virtual environment and install test dependencies:

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -e '.[test]'
   ```

2. Run the suite:

   ```bash
   .venv/bin/pytest -q
   ```

3. Read `fixtures/portfolio.json` and `tests/` to see the observable contract.
4. Exercise the read-only host:

   ```bash
   .venv/bin/python - <<'PY'
   from zerion_portfolio_manager.host import ReadOnlyHost
   host = ReadOnlyHost("fixtures/portfolio.json")
   print(host.get_pnl())
   print(host.parse_dca_request("DCA another $300 of ETH"))
   PY
   ```

5. Optional MCP surface (still read-only):

   ```bash
   .venv/bin/pip install -e '.[mcp]'
   .venv/bin/zpm-mcp
   ```

6. Read `IMPLEMENTATION-PLAN.md` before extending the system.

The MVP is fixture-only and simulation-only. Never add credentials, private keys, seed phrases, or real transaction code to this repository.

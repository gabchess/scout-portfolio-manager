# Zerion portfolio-manager agent demo

A self-contained, fixture-backed demo UI for the read-only portfolio
intelligence in this repository. One page shows the whole agent loop:

1. **Portfolio snapshot** (boundary: *observe*) — holdings and the transaction
   ledger from the synthetic fixture at `fixtures/portfolio.json`.
2. **Explainable USD PnL** (boundary: *calculate*) — realized/unrealized/total
   with the formula, basis provenance, and confidence shown, not just a number.
3. **DCA agent** (boundary: *propose/approve*) — type a natural-language DCA
   request. Missing details produce a clarification question (never a guess);
   a complete request produces a preview with `approval_state=required` and
   `execution_available=false`.

The demo is a thin window onto `zerion_portfolio_manager.host.ReadOnlyHost`.
It adds no portfolio logic and no execution capability of any kind.

## Safety boundary

`observe ≠ calculate ≠ propose ≠ approve ≠ execute ≠ verify`

- No wallet connect, no signing, no transaction submission, no fund movement,
  no investment advice.
- The demo server exposes only four read-only endpoints mirroring the host
  tools; there is no execute/sign/submit route to call.
- Runs entirely offline on the synthetic fixture. `ZERION_API_KEY` is **not**
  required and is never read by the demo. Fixture values are examples, not
  live market data.

## Run it

From the repository root (Python 3.11+):

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python demo/zerion-portfolio-agent/server.py
```

Then open http://127.0.0.1:8787.

If port 8787 is taken, pick another: `DEMO_PORT=8899 .venv/bin/python demo/zerion-portfolio-agent/server.py`.

(Any environment where the package's one dependency, `pydantic>=2.5`, is
importable works — the server adds `src/` to `sys.path`, so a plain
`pip install 'pydantic>=2.5'` followed by
`python3 demo/zerion-portfolio-agent/server.py` also runs.)

## Things to try

- Click **incomplete → clarification** (`DCA another $300 of ETH`): the intent
  grid shows which fields parsed and which are missing, and the agent asks a
  clarification question instead of inferring a chain, schedule, or wallet.
- Click **complete → preview**
  (`DCA $300 ETH on ethereum weekly from wallet:0xabc123 to wallet:0xdef456`):
  a full preview renders with `approval_state: required`,
  `execution_available: false`, and every assumed quote value labeled as a
  fixture placeholder.
- Type your own request and watch the parser refuse to guess.

## Files

| File | Purpose |
|---|---|
| `PLAN.md` | Goal, MVP scope, outs, stack rationale (written before implementation) |
| `server.py` | Stdlib HTTP server wrapping `ReadOnlyHost`; serves the API + static UI |
| `static/index.html` | Product chrome: pipeline strip, snapshot, PnL, DCA agent panels |
| `static/app.js` | Fetches host responses and renders them; no portfolio logic |
| `static/styles.css` | Dashboard styling |

## API surface (all read-only)

| Endpoint | Host method |
|---|---|
| `GET /api/snapshot` | `get_portfolio_snapshot()` |
| `GET /api/pnl?asset=ETH` | `get_pnl(asset)` |
| `POST /api/dca/parse` `{"text": …}` | `parse_dca_request(text)` |
| `POST /api/dca/preview` `{"text": …}` | `preview_dca(text)` |

Anything else — including any execute, sign, or submit path — returns 404.

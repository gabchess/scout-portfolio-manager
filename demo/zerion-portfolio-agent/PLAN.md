# PLAN: Zerion portfolio-manager agent demo

## Goal

A self-contained, runnable demo surface that lets someone *see* the
portfolio-manager agent loop this repository implements around Zerion-shaped
data, without reading Python. One screen shows the whole boundary story:

1. **Observe**: a portfolio snapshot (holdings + transaction ledger) from the
   default synthetic fixture.
2. **Calculate**: explainable USD PnL with the formula, basis, and confidence
   visible, not just a number.
3. **Propose / Approve**: a natural-language DCA request is parsed into
   explicit fields; missing fields produce a clarification question, and a
   complete request produces a preview with `approval_state=required` and
   `execution_available=false`.

The demo is a *window onto* `scout_portfolio_manager.host.ReadOnlyHost`. It
adds no new portfolio logic of its own.

## MVP (in scope)

- A thin local Python demo server (stdlib `http.server`, zero new
  dependencies) that wraps `ReadOnlyHost` and exposes four read-only JSON
  endpoints mirroring the host tools: snapshot, PnL, DCA parse, DCA preview.
- A single-page front-end (plain HTML/CSS/JS, no build step) with real product
  chrome: snapshot card, PnL card, and an interactive DCA agent panel with
  example prompts for both the clarification path and the complete-preview
  path.
- Boundary labels everywhere: every card is tagged with its stage
  (observed / calculated / proposal), the pipeline strip shows
  `observe → calculate → propose → approve` with execute/verify visibly out of
  scope, and preview output shows `approval_state=required` and
  `execution_available=false` verbatim.
- `README.md` with copy-paste run steps that work offline on the fixture.

## Out of scope

- Real Zerion API calls in the default demo path (the package's optional
  adapter exists, but the demo runs on `fixtures/portfolio.json` and never
  requires `ZERION_API_KEY`).
- Any execute, sign, submit, wallet-connect, or fund-moving path. The server
  registers no such endpoint and the UI renders no such control.
- Investment advice of any kind.
- Redesigning or modifying the existing package. Changes stay under
  `demo/zerion-portfolio-agent/`.

## Stack rationale

- **Server: Python stdlib `http.server`.** The host is already Python; a
  ~150-line stdlib server keeps the demo dependency-free (only the package
  itself, i.e. pydantic), keeps the read-only surface auditable in one file,
  and avoids adding FastAPI/Flask to a repo that deliberately has a tiny
  dependency footprint.
- **Front-end: plain HTML/CSS/JS served by the same server.** No Bun/Vite
  build step means no lockfiles, no node_modules, no supply-chain surface, and
  one command to run. The page is small enough (three panels) that a framework
  buys nothing; hand-rolled chrome still reads as a real product.
- **Fixture-first.** The demo binds `ReadOnlyHost` to
  `fixtures/portfolio.json` explicitly. This makes the demo deterministic,
  offline, and safe to run anywhere.

## Definition of done

- `python3 demo/zerion-portfolio-agent/server.py` serves the UI at
  `http://127.0.0.1:8787` with all three flows working against the fixture.
- Both DCA paths are demonstrable from example chips: clarification
  (`"DCA another $300 of ETH"`) and complete preview
  (`"DCA $300 ETH on ethereum weekly from wallet:0xabc123 to wallet:0xdef456"`).
- Safety copy is visible in the UI, not just the docs.

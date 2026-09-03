# Zerion Agentic Portfolio Manager MVP

## Repository boundary

- **Repository:** this repository
- **Status at start:** did not exist; no files or git history.
- **Related but excluded:** unrelated repositories are outside this project and are not modified.
- **Local instructions:** no `AGENTS.md`, `CLAUDE.md`, `README`, or project config exists at the new boundary. The governing product and safety notes are the public product requirements and docs in this repository.
- **Authority:** implementation of the approved local MVP is authorized. Real wallet connection, real funds, production credentials, public deployment, GitHub push, and outreach are explicitly excluded and require a separate approval.

## Observable objective

Build a standalone, installable Python 3.11+ MVP that provides fixture-backed Zerion-shaped portfolio reads, explainable USD PnL, agent intents, DCA parsing and clarification, a complete preview, fake execution failure coverage, idempotency, and settlement verification while preserving the boundaries `observe != calculate != propose != approve != execute != verify`.

## Done when

1. Typed portfolio and transaction contracts are exercised by fixture-backed tests.
2. PnL returns formula, timestamps, fee treatment, basis warnings, and uncertainty.
3. Holdings, PnL, last-purchase, and change-since-date read intents work deterministically.
4. DCA parsing extracts explicit fields and asks instead of inferring missing or ambiguous source, chain, destination, schedule, or authorization.
5. Preview contains every material transaction field and approval state.
6. Fake execution covers success plus stale quote, insufficient balance, duplicate request, wrong destination, rejected authorization, timeout, and settlement mismatch.
7. Idempotency prevents duplicate execution and verification is a distinct readback boundary.
8. README, START-HERE, SECURITY, DATA-AND-PRIVACY, architecture notes, fixtures, tests, behavioral evals, and Zerion-facing product brief explain the product and limitations.
9. Tests, security/secret scan, and clean-install verification have fresh observed output.
10. Builder and verifier evidence remain separate in the engineering record.

## Non-goals

No real API calls, wallet connections, signatures, funds, credentials, seeds, private keys, autonomous trading, investment advice, production deployment, public push, or outreach.

## Dependency-aware tickets

### ZPM-001 Contracts and fixture boundary

- **Outcome:** Pydantic contracts represent portfolio snapshots, holdings, transactions, basis inputs, quote data, intents, receipts, and verification evidence.
- **Owned surface:** `src/zerion_portfolio_manager/contracts.py`, `fixtures/`, contract tests.
- **Protected boundaries:** no secrets; fixture-shaped data must be labeled as such; read models cannot execute.
- **Dependencies and inputs:** approved product contract and system design.
- **Red evidence:** repository has no implementation yet; contract tests must fail before implementation.
- **Verifier:** focused pytest contract suite.
- **Expected artifact:** typed models and deterministic JSON fixtures.
- **Attempt budget:** 3.
- **Stop condition:** any contract requires an unapproved real-provider assumption.
- **Authority gate:** local implementation only.

### ZPM-002 Portfolio reads and ledger

- **Outcome:** fixture-backed adapter loads snapshots and transaction history through an observe-only interface; ledger records supported transaction and basis forms without secrets.
- **Owned surface:** `portfolio.py`, `ledger.py`, fixture loader tests.
- **Dependencies:** ZPM-001.
- **Verifier:** focused portfolio and ledger tests.

### ZPM-003 Explainable PnL

- **Outcome:** realized/unrealized USD PnL includes formula, valuation time, fee treatment, missing-basis warnings, and confidence.
- **Owned surface:** `pnl.py`, PnL tests.
- **Dependencies:** ZPM-001, ZPM-002.
- **Verifier:** focused PnL tests including $2,000 to $2,250 = +$250 and +12.5%.

### ZPM-004 Read intents and reporting

- **Outcome:** holdings, PnL, last purchase, and change-since-date requests produce source-grounded reports separating observed, calculated, assumed, and unknown.
- **Owned surface:** `intents.py`, `reporting.py`, read intent tests.
- **Dependencies:** ZPM-002, ZPM-003.
- **Verifier:** focused intent/report tests.

### ZPM-005 DCA parsing and clarification

- **Outcome:** explicit DCA language becomes a partial typed proposal; missing or ambiguous fields produce one useful clarification at a time and never infer wallets, destinations, chains, schedules, or authorization.
- **Owned surface:** DCA parser and clarification tests.
- **Dependencies:** ZPM-001.
- **Verifier:** focused parser behavior suite.

### ZPM-006 Preview, quote, and approval boundary

- **Outcome:** preview includes asset, amount, currency, chain, source, destination, expected output, fees, slippage, quote expiry, schedule, limits, failure behavior, and approval state; approval is distinct from proposal.
- **Owned surface:** preview/safety modules and tests.
- **Dependencies:** ZPM-005.
- **Verifier:** preview completeness and approval-gate tests.

### ZPM-007 Fake adapter and failure taxonomy

- **Outcome:** fake adapter models success and all required failures without touching networks or funds.
- **Owned surface:** adapter and error modules plus tests.
- **Dependencies:** ZPM-001, ZPM-006.
- **Verifier:** focused adapter failure suite.

### ZPM-008 Idempotency and settlement verifier

- **Outcome:** duplicate intents cannot execute twice; verifier independently reads transaction and portfolio settlement evidence and refuses optimistic success.
- **Owned surface:** idempotency, receipt, verifier modules and tests.
- **Dependencies:** ZPM-007.
- **Verifier:** replay and settlement tests.

### ZPM-009 Packaging and proof

- **Outcome:** installable package and agent-facing documentation/evals are complete; security, secret, full test, and clean-install checks are run.
- **Owned surface:** packaging and docs.
- **Dependencies:** ZPM-004, ZPM-008.
- **Verifier:** independent review pass plus command evidence.

### ZPM-010 Read-only host adapter

- **Outcome:** agent-facing host exposes `get_portfolio_snapshot`, `get_pnl`, `parse_dca_request`, and `preview_dca` only; optional MCP stdio entry wraps the same surface; execute remains unavailable on the host.
- **Owned surface:** `host.py`, `mcp_server.py`, host tests, docs.
- **Protected boundaries:** no wallet, network, signing, funds, credentials, or real rail; missing DCA fields still force clarification; preview keeps `approval_state=required` and `execution_available=false`.
- **Dependencies:** ZPM-009.
- **Verifier:** focused host tests plus full suite and security scan.

## Execution order

`ZPM-001 -> ZPM-002 -> ZPM-003 -> ZPM-004` and `ZPM-001 -> ZPM-005 -> ZPM-006 -> ZPM-007 -> ZPM-008`, then `ZPM-009`, then `ZPM-010`.

## Re-entry condition

Local MVP (ZPM-001..009) and read-only host (ZPM-010) are the current boundary. Next reversible work is optional packaging polish or a separately authorized real observe adapter. Real execution rail, push, deploy, and outreach remain blocked without a new authority decision. If package/tooling assumptions conflict with the source notes, stop and revise the plan rather than widening into real integrations.

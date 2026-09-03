# Zerion-facing product brief

## Hypothesis

Zerion can become the portfolio-intelligence layer inside agentic financial workflows by exposing predictable, interpretable portfolio observations that an agent can combine with a user-selected execution rail.

## MVP evidence

This local reference implementation demonstrates fixture-backed typed portfolio reads, explainable PnL, DCA intent clarification, complete action previews, fake execution, idempotency, and settlement verification.

## What it does not claim

The fixture is not a Zerion API response. This repository does not establish private Zerion architecture, internal SLOs, customer demand, or endpoint behavior. Those claims require authorized documentation, interviews, or internal data.

## Useful future questions

- Which portfolio and transaction fields are stable enough for agent contracts?
- How should cost basis, quote expiry, execution status, and readback be represented?
- Which authorization and webhook semantics are appropriate for user-selected rails?

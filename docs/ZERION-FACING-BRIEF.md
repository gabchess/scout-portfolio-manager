# Product brief

## Purpose

This repository explores a portable, read-only portfolio-intelligence surface for agentic financial workflows: typed portfolio observations, explainable PnL, explicit DCA intent clarification, and approval-required previews.

## Available evidence

The repository includes a synthetic fixture, a read-only host, an optional aggregate Zerion API adapter, an optional read-only MCP server, and tests for the documented behavior. The fixture is not a Zerion API response. API-backed behavior depends on the configured account, endpoint contract, authorization, and network availability.

## What this project does not claim

This repository does not make claims about Zerion's architecture, SLOs, customer demand, product endorsement, or endpoint guarantees. It is not a production integration, trading system, wallet, signing service, or investment-advice product.

## Questions for an integration owner

- Which portfolio fields and freshness indicators are appropriate for an agent contract?
- How should cost basis and quote expiry be represented when the data source is aggregate?
- What authorization, rate-limit, and error semantics should an approved integration expose?

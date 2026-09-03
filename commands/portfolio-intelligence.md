---
name: portfolio-intelligence
description: Inspect a portfolio, explain PnL, or preview a DCA request without execution
argument-hint: "[question or DCA request]"
---

Use the `zerion-portfolio-intelligence:portfolio-intelligence` skill for this request.

Treat the local fixture as the default source. If the read-only MCP server is connected,
use its tools for observations and calculations. State the source and observation time.

For DCA requests, extract amount, asset, chain, schedule, source, and destination. Ask for
missing fields. A complete request gets a preview only. Never sign, submit, execute, infer
wallet details, or present a preview as a completed transaction.

User request: $ARGUMENTS

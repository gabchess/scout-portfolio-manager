# zerion-adapter terms of use

## What this component is

`ZerionAPIReader` and `ZerionWalletReader` (`src/scout_portfolio_manager/zerion_api.py`) are an opt-in, read-only client for Zerion's hosted wallet positions and transactions endpoints at `https://api.zerion.io`. The adapter is disabled by default; it activates only when an operator sets both `ZERION_API_KEY` and `ZERION_WALLET_ADDRESS`. It performs no write, sign, submit, or execute call, and this repository provides no such capability anywhere in the codebase.

## Governing terms

This project's MIT license covers the adapter's own source code. It does not cover, extend, or modify Zerion's API terms. Any use of the live API, meaning any run with real credentials against `api.zerion.io`, is governed entirely by Zerion's own terms, published at https://zerion.io/terms, and by the scope, rate limits, and authorization of the operator's own Zerion account. Review Zerion's current terms directly before enabling this adapter with real credentials; this project does not restate, summarize, or interpret them, and Zerion's terms may change independently of this repository.

## Operator responsibility

The operator supplies and controls the API key, through their own secret manager, per [`SECURITY.md`](../../SECURITY.md) and [`DATA-AND-PRIVACY.md`](DATA-AND-PRIVACY.md) in this folder. This project does not store, transmit to a third party, or have any visibility into the operator's Zerion account or credentials.

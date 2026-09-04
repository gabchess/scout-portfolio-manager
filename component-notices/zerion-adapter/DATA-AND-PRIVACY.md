# zerion-adapter data and privacy

## Default state

The adapter is disabled by default. With no `ZERION_API_KEY` and `ZERION_WALLET_ADDRESS` set, this component makes no request and touches no data.

## When enabled

When both environment variables are present, the adapter makes a read-only request for one wallet's positions and transaction history. It:

- reads the API key and wallet address once at process startup, holds the key in memory for the process lifetime, and excludes it from object representations, error messages, tool results, and any log line this package writes;
- returns per-asset holdings and a mapped transaction ledger; the wallet address itself is sent to Zerion in the request path and appears in the returned snapshot, so treat results as containing personal wallet data;
- stops the host process on a partial credential pair (one variable set, not both) rather than silently falling back to the fixture;
- performs no write, sign, submit, or settlement-verification call, and has no code path that could perform one.

## What this component does not control

Zerion's own logging, retention, and data handling for the request path are outside this repository's control; see Zerion's published terms and privacy documentation, referenced in [`TERMS-OF-USE.md`](TERMS-OF-USE.md), for that boundary. Credential storage, host-level network logs, and access control are the operator's responsibility; see [`SECURITY.md`](../../SECURITY.md).

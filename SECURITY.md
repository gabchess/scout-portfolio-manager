# Security

- No real wallets, funds, credentials, private keys, or seed phrases.
- No network calls in the MVP.
- Contracts reject unknown fields to prevent accidental secret-bearing payloads.
- The host/MCP surface is read-only: observe, calculate, propose, preview only.
- Host `call_tool` refuses execute/sign/submit names with `PermissionError`.
- Execution is fake-adapter-only and requires explicit approval.
- Idempotency keys prevent duplicate simulated execution.
- Settlement is not trusted from submission. Verification requires readback evidence.
- Treat fixture data as synthetic and do not put personal wallet data into tests.

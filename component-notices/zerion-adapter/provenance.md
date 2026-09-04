# zerion-adapter provenance

## Authorization

Gabriel Abreu, the repository maintainer, authorized building and releasing this adapter as an opt-in, read-only component, and separately authorized this augment-packaging effort on 2026-09-04.

## Original versus sourced

This component is original: it is not a fork, port, or derivative of a Zerion-published SDK. It was written against Zerion's public API contract (`GET /wallets/{addr}/positions/`, `GET /wallets/{addr}/transactions/` at `api.zerion.io`), as documented in this repository's own `CHANGELOG.md` (`Unreleased` section) and test suite (`tests/test_zerion_api.py`, `tests/test_zerion_source_wiring.py`).

## Dated inputs and known limits

Per this repository's `WHAT-BROKE.md`, as of the most recent release: transaction pagination is bounded by `ZerionAPIConfig.max_pages` (default 20 pages of 100); a live rate limit (HTTP 429) was hit during development before the `quantity` field's exact response shape (bare float versus a `{"float": ...}` object) could be confirmed against a real payload, so the adapter accepts both shapes defensively; and the one successful live transactions call used a wallet with zero items either way. These are stated as known, live-unconfirmed caveats in the repository's own release-honesty file, not resolved by this notice.

## Evidence boundary

This artifact declares contents and provenance; it does not prove runtime behavior on any machine other than the one that produced it.

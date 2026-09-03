# Zerion API DX proposal

Date: 2026-09-03
Status: proposal, not yet reviewed by Zerion product or engineering
Owner: crew synthesis, drafted by Masthead

## Purpose

This document collects five developer-experience proposals for the Zerion API,
based on crew findings from 2026-09-03. Each proposal names a concrete measure
of success: a signal you can check, not an aspiration you can't. It also lists
three open questions for Abi, Zerion's product lead, that the proposal set
raises.

## A note on source verification

The proposals below draw on two source sets with different verification
status. Keep the distinction when you read or cite this document.

- **Zerion facts**: documented, checked by the crew's Seat D against Zerion's
  own docs on 2026-09-03. Treat these as verified.
- **Arkham facts**: documented from an email Gabe received on 2026-09-03.
  Status: reported, independently unverified. The crew's fetch against
  Arkham's own announcement returned an HTTP 503, so nobody has read the
  primary source yet. Proposal 1 below cites Arkham's shape as *inspiration
  only*. Don't read it as a confirmed Arkham precedent, and don't upgrade it
  to verified fact anywhere downstream of this doc.

## The five proposals

### 1. Resumable pull endpoint or documented replay semantics

Add a resumable pull endpoint, for example `GET
/wallets/{addr}/positions/updates?cursor=`, or publish documented
webhook-replay semantics for the existing push model. Today, Zerion's
real-time delivery is webhook-based and push-only; there's no documented
"give me everything since cursor X" equivalent.

This proposal takes its shape from an email Gabe received from Arkham
describing a new endpoint, `GET /intelligence/addresses/updates`, with a
resumable cursor. That claim is reported and unverified (see the note above).
Cite it here as an example of the shape a resumable pull endpoint could take,
not as evidence Arkham shipped it or that Zerion should copy it precedent-for-precedent.

**Measure of success**: A client that misses a webhook delivery (network
blip, deploy window, queue backlog) can recover the missed events with one
follow-up call, without replaying the full wallet history. Check: a test
client disconnects for 5 minutes during active wallet activity, then
reconnects and calls the resumable endpoint with its last-known cursor; it
receives exactly the events it missed, no more, no fewer.

### 2. Typed error code field, generated from OpenAPI

Add a typed `code` field to error responses, generated from Zerion's OpenAPI
spec, so clients can switch on a stable machine-readable code instead of
parsing free-text error messages.

**Measure of success**: An SDK or client library can map every documented
error response to a specific handling branch by reading `code` alone, with
zero string-matching against `message`. Check: grep any official Zerion SDK's
error-handling code for message-text comparisons; that count should drop to
zero once the field ships.

### 3. Rate-limit headers on every reference page, with a worked example

Document rate-limit headers (remaining count, reset time) on every endpoint's
reference page, paired with a worked backoff example a developer can copy.
Zerion's default rate limit is 150 requests per second; today a client has to
infer its remaining budget rather than read it.

**Measure of success**: A developer building backoff logic never has to guess
at the current limit or read the changelog to find it. Check: every
endpoint's reference page includes the header names and a runnable backoff
snippet; a support ticket asking "what's the rate limit for this endpoint"
becomes answerable by pointing at that page.

### 4. Common-pitfall callout on the aggregate `/portfolio` endpoint

Add a "common pitfall" callout to the `/portfolio` endpoint's docs page,
pointing readers to `/positions/` when they need per-asset holdings instead
of one aggregate number.

This isn't a hypothetical confusion. It's the reason Slice 1 of this repo's
adapter work exists: the original implementation called `/portfolio` only,
mapped its single aggregate figure to one synthetic holding, and every
live-backed PnL calculation reported "missing basis" as a result. A callout
on the docs page would have caught this at build time instead of at review
time.

**Measure of success**: A new integrator reads the `/portfolio` docs page
before writing their first request and picks `/positions/` correctly on the
first attempt, without a support ticket or a stack-overflow-style workaround.
Check: if Zerion tracks it, a drop in support tickets that ask why
`/portfolio` doesn't return per-asset data.

### 5. Raise the `/transactions/` `page[size]` cap

Raise the documented `page[size]` cap on `/transactions/` from 100 toward the
250-500 range already precedented on the NFT positions endpoint (observed
2026-05-29). Whether `/positions/` or `/transactions/` already support a
higher cap undocumented is unverified; this repo's adapter spec pins
`page[size]=100` until that's checked, precisely to avoid depending on an
unconfirmed higher limit.

**Measure of success**: A wallet with a long transaction history needs fewer
round trips to page through its full ledger. Check: fetching 1,000
transactions for a test wallet takes 2-4 requests instead of 10, with no
change in per-request latency.

## Open questions for Abi

These are questions this proposal set raises, not positions the crew is
taking.

1. Push-only webhooks vs. a resumable poll model: is Zerion already
   considering an Arkham-style resumable-cursor pattern, or is push-only a
   deliberate product bet?
2. Is a typed error-code initiative, generated from OpenAPI, already underway
   anywhere in the API surface?
3. How much support load traces back to the aggregate-portfolio-vs-positions
   confusion described in proposal 4? If that's measurable, it's the
   strongest case for the docs callout.

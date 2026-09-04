# demo-ui terms of use

The demo UI is a local, fixture-backed demonstration surface. It has no account system, no telemetry, and no live Zerion API call; it runs entirely against the synthetic fixture at `fixtures/portfolio.json`.

## Scope

The demo shows the read-only agent loop this repository implements: portfolio snapshot, explainable PnL, and a DCA chat that ends at an approval-required preview. It registers no execute, sign, or submit endpoint. See [`demo/zerion-portfolio-agent/README.md`](../../demo/zerion-portfolio-agent/README.md) for the full safety boundary and run instructions.

## Use terms

Use of the demo is governed by the repository's MIT license (see [`LICENSE.md`](LICENSE.md) in this folder). Running the demo does not create a hosted service, a support commitment, or a data-processing relationship with the repository maintainers. Fixture output is synthetic and must not be presented as live portfolio data.

## No warranty

The demo is provided as-is, per the repository's MIT license terms, without warranty of any kind. It is a demonstration surface, not a production integration.

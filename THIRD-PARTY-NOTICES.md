# Third-party and component notices

Scout Portfolio Manager is MIT-licensed (see [`LICENSE.md`](LICENSE.md)). This file lists the third-party software the project depends on, the external API terms that govern the optional Zerion adapter, and the source of the visual brand tokens used in the browser demo. Per-component provenance, licensing, and data-handling detail lives under [`component-notices/`](component-notices/).

## Python dependencies

The table covers every dependency declared directly in [`pyproject.toml`](pyproject.toml): the one runtime dependency and the three development/optional extras (`test`, `quality`, `mcp`). License names below match each project's published PyPI classifier and repository license file.

| Package | Constraint | Role | License | Upstream |
|---|---|---|---|---|
| `pydantic` | `>=2.5,<3` | Runtime | MIT | https://github.com/pydantic/pydantic |
| `pytest` | `>=8,<9` | Dev (`test` extra) | MIT | https://github.com/pytest-dev/pytest |
| `ruff` | `>=0.6,<1` | Dev (`quality` extra) | MIT | https://github.com/astral-sh/ruff |
| `mypy` | `>=1.11,<2` | Dev (`quality` extra) | MIT | https://github.com/python/mypy |
| `mcp` | `>=1.2,<2` | Optional runtime (`mcp` extra) | MIT | https://github.com/modelcontextprotocol/python-sdk |

Every license above is the standard MIT License, unmodified, as published in each project's own repository. This project does not vendor or modify any of their source.

This table lists the five dependencies declared directly in `pyproject.toml`. `uv.lock` at the repository root resolves 34 additional transitive packages (things `pydantic`, `mcp`, `pytest`, `ruff`, and `mypy` themselves depend on, such as `httpx`, `starlette`, `uvicorn`, `pydantic-core`, and `jsonschema`). Those are not separately enumerated here; `uv.lock` is the authoritative artifact for a full transitive supply-chain audit. License fields for the five direct dependencies were read from installed package metadata on 2026-09-04 (pydantic 2.13.5, pytest 8.4.2, ruff 0.16.6, mypy 1.20.2, mcp 1.29.1; all report MIT).

## Zerion API terms (optional adapter)

The optional `ZerionAPIReader` adapter in `src/scout_portfolio_manager/zerion_api.py` makes read-only requests to `https://api.zerion.io`, Zerion's own hosted API. This project does not redistribute Zerion's API, data, or software; the adapter is original code written against Zerion's public endpoint contract. Use of the live API is governed entirely by Zerion's own terms, published at https://zerion.io/terms, and by the authorization, rate limits, and data scope of the Zerion account the operator configures. Review Zerion's current terms before enabling the adapter with real credentials; this project does not restate or interpret them. See [`component-notices/zerion-adapter/`](component-notices/zerion-adapter/) for the component-level notice.

## Zerion brand tokens (demo only)

The browser demo at `demo/zerion-portfolio-agent/` uses a color and typography palette sourced from Zerion's public brand and design guidance at https://design.zerion.io (`/color` and `/typography`). These are visual reference values (hex colors, a type-family name and weight), not software. No Zerion logo, wordmark, or other brand asset is shipped in this repository. Use of the palette does not imply Zerion's endorsement or a partnership. See [`component-notices/zerion-brand-tokens/`](component-notices/zerion-brand-tokens/) for the component-level notice.

## Evidence boundary

This artifact declares contents and provenance; it does not prove runtime behavior on any machine other than the one that produced it.

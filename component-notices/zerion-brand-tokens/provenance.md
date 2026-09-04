# zerion-brand-tokens provenance

## Authorization

Gabriel Abreu, the repository maintainer, authorized styling the demo with Zerion's published brand guidance to visually align it with the API it demonstrates, and separately authorized this augment-packaging effort on 2026-09-04.

## Original versus sourced

- **Sourced:** eight color values, six gradient pairs, and one type family and weight, transcribed from `design.zerion.io/color` and `design.zerion.io/typography`. The exact date of that lookup is not recorded in the source comments in `demo/zerion-portfolio-agent/static/styles.css`; only the source page is cited inline.
- **Original:** the semantic role assignment (`--positive`, `--negative`), and every value in the same file explicitly marked as a house default (surface tints, border colors, corner radii) rather than a Zerion value.

## Dated inputs

`demo/zerion-portfolio-agent/static/styles.css` itself is the dated artifact: each token's source comment names the exact Zerion design-system page it was read from, verifiable by re-reading that page against the file's committed values.

## Evidence boundary

This artifact declares contents and provenance; it does not prove runtime behavior on any machine other than the one that produced it.

# demo-ui provenance

## Authorization

Gabriel Abreu, the repository maintainer, merged GitHub pull request #3 (commit `e0ba0ed`) into this MIT-licensed repository, and separately authorized this augment-packaging effort on 2026-09-04 as part of renaming the project to Scout.

## Original versus sourced

- **Sourced (PR #3, Cursor-crew authored):** the original demo surface, commit `e0ba0ed`. This commit's object is present in this repository's git object store at `.git/objects/e0/ba0ed7921e88e30cbc59c3e417820204a6e0ee`; merged 2026-09-04T08:04:32-03:00 per `git log -1 --format=%cI e0ba0ed`, verified by Nova the same day.
- **Adapted (repository maintainer's own work, after PR #3):** rewiring the demo to the renamed `scout_portfolio_manager` package and its current host contract, and bringing the folder under this augment's documentation, licensing, and provenance discipline.

## Dated inputs

- The demo's color and typography values were pulled from Zerion's published brand guidance at `design.zerion.io/color` and `design.zerion.io/typography`, as recorded inline in `demo/zerion-portfolio-agent/static/styles.css`. The exact date of that lookup is not recorded in the source comments.
- The demo's read-only API surface (`/api/snapshot`, `/api/pnl`, `/api/dca/parse`, `/api/dca/preview`) mirrors `ReadOnlyHost`'s four tools as of this repository's `0.2.0` line; see `demo/zerion-portfolio-agent/README.md` and `PLAN.md` for the demo's own design record.

## Evidence boundary

This artifact declares contents and provenance; it does not prove runtime behavior on any machine other than the one that produced it.

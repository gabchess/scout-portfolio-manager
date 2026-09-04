# TA-07: Version bump, CHANGELOG, and release artifact rebuild

Prerequisites: TA-01 through TA-06, all of them. This is the last ticket,
run once, after everything else has landed. Do not start it early: every
later ticket invalidates the checksums and zip this one produces.

## Objective

Bump to 0.3.0, write the CHANGELOG entry, regenerate the Codex host mirror,
refresh `SHA256SUMS.txt`, and rebuild the release zip, so the tree handed
to release review is internally consistent and self-verifying.

## Files this ticket may touch

- `pyproject.toml` (`version = "0.3.0"`)
- `CHANGELOG.md` (new `## 0.3.0` section)
- `LOADOUT-MANIFEST.json` (`version`, `component_versions.product`,
  `surfaces.python_host`/`surfaces.mcp` final six-tool lists if not already
  complete, `capabilities` final state)
- `RELEASE-MANIFEST.json` (`version`; `release_artifacts` is rewritten by
  `scripts/build_release_zip.py`, not hand-edited)
- `codex/` (regenerated, never hand-edited)
- `SHA256SUMS.txt` (regenerated)
- `dist/scout-portfolio-0.3.0.zip` (built, gitignored per existing
  `dist/` entry in `.gitignore`)

## Interface / contract

Order of operations, each one gating the next:

1. `pyproject.toml`: bump `version` to `"0.3.0"`.
2. `CHANGELOG.md`: new `## 0.3.0 - <date>` section, `### Added` naming
   `analyze_asset`, `dca_windows`, `set_alert`/`check_alerts`, the `watch`
   skill and `scout-report.html`, and `fixtures/price_history.json`.
   `### Changed` naming the README/START-HERE/ARCHITECTURE/SECURITY/
   DATA-AND-PRIVACY reframe from TA-06, matching the 0.2.0 entry's level of
   specificity (name the actual files and behaviors, not "improved docs").
3. `LOADOUT-MANIFEST.json`: bump `version` and
   `component_versions.product` to `"0.3.0"`. Confirm `surfaces.python_host`
   and `surfaces.mcp` both list all six tool names. Confirm `capabilities`
   carries `"technical_analysis": true` and `"alerts": true` alongside the
   existing keys.
4. `RELEASE-MANIFEST.json`: bump `version` to `"0.3.0"`. Leave
   `release_artifacts` alone; step 7 rewrites it.
5. `python scripts/build_host_layouts.py`: regenerates `codex/` from the
   canonical `.claude-plugin/` and `skills/` trees, picking up
   `skills/watch/`.
6. `python scripts/write_checksums.py`: refresh `SHA256SUMS.txt` against
   the current tree (all new files from TA-01 through TA-06, plus the
   regenerated `codex/` tree).
7. `python scripts/build_release_zip.py`: builds
   `dist/scout-portfolio-0.3.0.zip`, runs `security_scan.py` against the
   staged tree first (aborts on any finding), then appends the new digest
   to both `SHA256SUMS.txt` and `RELEASE-MANIFEST.json`'s
   `release_artifacts`.
8. `python scripts/write_checksums.py --check`: must exit 0. If it does
   not, something in steps 5 to 7 changed a tracked file after the
   checksum refresh; rerun step 6.

## Invariant it must not break

`RELEASE-MANIFEST.json`'s `execution_boundary` block
(`wallet_connection`/`signing`/`submission`/`execution`/
`settlement_verification`, all `false`) is unchanged. This release adds
read-only tools; it does not change what the package is authorized to do.

## Acceptance check

- `pytest -q` fully green, one final run against the completed tree.
- `python scripts/check_plugin_manifest.py` exits 0.
- `python scripts/write_checksums.py --check` exits 0.
- `python scripts/build_release_zip.py` completes without the security
  scan aborting it.
- `git status` shows the expected changed/new files only: no stray
  `.scout/alerts.json` or `scout-report.html` committed (both must be
  gitignored per TA-04 and TA-05).
- `dist/scout-portfolio-0.3.0.zip` exists locally (it is gitignored, not
  committed; Release review happens against the commit, the zip is a
  local build artifact proving the build step works).

## Escalation trigger

If `write_checksums.py --check` still fails after a re-run of step 6,
stop and diff `SHA256SUMS.txt` against `git status` output line by line
rather than re-running the whole pipeline again; a repeated failure here
usually means an untracked file that should be gitignored (like a stray
`scout-report.html` from local testing) is leaking into the checksum set.

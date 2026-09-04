"""Write and verify SHA256SUMS.txt for the repo tree.

Covers every file git would track: tracked files plus untracked-but-not-ignored
files (so newly authored files count before their first `git add`), minus
SHA256SUMS.txt itself. Output is deterministic: paths sorted, forward slashes,
LF line endings, lowercase hex, the standard `sha256sum`/`shasum -a 256` format
so the file doubles as input to `shasum -a 256 -c SHA256SUMS.txt`.

Usage:
    python scripts/write_checksums.py            # write/refresh SHA256SUMS.txt
    python scripts/write_checksums.py --check     # verify, exit 1 on drift
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

SUMS_FILENAME = "SHA256SUMS.txt"


def _tracked_and_untracked_files(root: Path) -> list[str]:
    """Every file git would track: staged/committed plus untracked-not-ignored.

    Uses git so build artifacts, caches, and .gitignore'd paths are excluded
    without duplicating .gitignore's rules here.
    """
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    paths = [p for p in result.stdout.decode("utf-8").split("\0") if p]
    return sorted(set(paths))


def _sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_sums(root: Path) -> str:
    lines = []
    for rel in _tracked_and_untracked_files(root):
        if rel == SUMS_FILENAME:
            continue
        path = root / rel
        if not path.is_file():
            continue
        lines.append(f"{_sha256_of(path)}  {rel}")
    return "\n".join(lines) + "\n" if lines else ""


def write(root: Path) -> Path:
    sums_path = root / SUMS_FILENAME
    sums_path.write_text(compute_sums(root))
    return sums_path


def check(root: Path) -> list[str]:
    """Return a list of drift descriptions; empty means no drift."""
    sums_path = root / SUMS_FILENAME
    if not sums_path.exists():
        return [f"{SUMS_FILENAME} does not exist; run without --check to create it"]
    expected = compute_sums(root)
    actual = sums_path.read_text()
    if expected == actual:
        return []

    expected_lines = {line for line in expected.splitlines() if line}
    actual_lines = {line for line in actual.splitlines() if line}
    errors = []
    for line in sorted(actual_lines - expected_lines):
        errors.append(f"stale or mismatched entry: {line}")
    for line in sorted(expected_lines - actual_lines):
        errors.append(f"missing or drifted entry: {line}")
    return errors


def main() -> int:
    root = Path.cwd()
    if "--check" in sys.argv[1:]:
        errors = check(root)
        if errors:
            print("\n".join(errors))
            print(f"\n{SUMS_FILENAME} is stale. Run: python scripts/write_checksums.py")
            return 1
        print(f"{SUMS_FILENAME} matches the tree")
        return 0

    sums_path = write(root)
    line_count = sum(1 for _ in sums_path.read_text().splitlines())
    print(f"wrote {sums_path} ({line_count} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

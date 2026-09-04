"""Build a deterministic, checksummed release zip for the installable package.

Packages the pieces an installer actually needs: the `.claude-plugin` manifest
(if present), the Python package source under `src/`, the top-level docs and
manifest files, and `demo/`. Deliberately leaves out anything that isn't part
of the shipped artifact: `.git`, caches, `.venv`, `.remember`, and `tracking/`.

Determinism: files are added in sorted path order with a fixed `date_time`
(1980-01-01, the earliest zip timestamp allowed) and fixed permission bits, so
two runs against an identical source tree produce a byte-identical zip and a
stable checksum.

Safety: runs `scripts/security_scan.py` against a staged copy of exactly the
files that will be packaged before writing the zip. A finding aborts the
build; nothing gets zipped.

Usage:
    python scripts/build_release_zip.py            # build dist/scout-portfolio-<version>.zip
    python scripts/build_release_zip.py /path/repo  # build from a different repo root
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from collections.abc import Iterable, Iterator
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    ".remember",
    "tracking",
}
LICENSE_CANDIDATES = ("LICENSE", "LICENSE.md", "LICENSE.txt")
TOP_LEVEL_FILES = ("START-HERE.md", "README.md", "RELEASE-MANIFEST.json", "pyproject.toml")


def _read_version(root: Path) -> str:
    manifest = tomllib.loads((root / "pyproject.toml").read_text())
    version = manifest.get("project", {}).get("version")
    if not version:
        raise SystemExit("pyproject.toml is missing project.version")
    return str(version)


def _is_excluded(relative_parts: tuple[str, ...]) -> bool:
    if any(part in EXCLUDED_DIR_NAMES for part in relative_parts):
        return True
    if any(part.endswith(".egg-info") for part in relative_parts):
        return True
    return relative_parts[-1] == ".DS_Store"


def _walk_included(directory: Path, root: Path) -> Iterator[tuple[Path, str]]:
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if _is_excluded(relative.parts):
            continue
        yield path, relative.as_posix()


def _find_package_dirs(root: Path) -> Iterable[Path]:
    src = root / "src"
    if not src.is_dir():
        return []
    return sorted(p for p in src.iterdir() if p.is_dir() and (p / "__init__.py").is_file())


def collect_release_files(root: Path) -> list[tuple[Path, str]]:
    """Return (absolute_path, arcname) pairs for everything the release ships."""
    files: dict[str, Path] = {}

    def _add(pairs: Iterable[tuple[Path, str]]) -> None:
        for abs_path, arcname in pairs:
            files[arcname] = abs_path

    claude_plugin_dir = root / ".claude-plugin"
    if claude_plugin_dir.is_dir():
        _add(_walk_included(claude_plugin_dir, root))

    for package_dir in _find_package_dirs(root):
        _add(_walk_included(package_dir, root))

    for name in (*TOP_LEVEL_FILES, *LICENSE_CANDIDATES):
        candidate = root / name
        if candidate.is_file():
            files[name] = candidate

    demo_dir = root / "demo"
    if demo_dir.is_dir():
        _add(_walk_included(demo_dir, root))

    return sorted(((abs_path, arcname) for arcname, abs_path in files.items()), key=lambda p: p[1])


def _canonical_release_manifest_bytes(path: Path) -> bytes:
    """Package RELEASE-MANIFEST.json without its own build ledger.

    `release_artifacts` records this script's own prior output (path, sha256,
    build timestamp). Left in place, the zip's content would depend on how
    many times the build previously ran instead of only on the source tree.
    Strip it before packaging so identical source produces an identical zip
    regardless of build history; `main()` still writes the full ledger,
    timestamp included, to the on-disk manifest after the zip exists.
    """
    manifest = json.loads(path.read_text())
    manifest.pop("release_artifacts", None)
    return (json.dumps(manifest, indent=2) + "\n").encode("utf-8")


def _stage(files: list[tuple[Path, str]], staging_root: Path) -> None:
    for abs_path, arcname in files:
        dest = staging_root / arcname
        dest.parent.mkdir(parents=True, exist_ok=True)
        if arcname == "RELEASE-MANIFEST.json":
            dest.write_bytes(_canonical_release_manifest_bytes(abs_path))
        else:
            shutil.copy2(abs_path, dest)


def _run_security_scan(target: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "security_scan.py"), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            "security_scan.py found credential-shaped content in the release tree; "
            "refusing to package it:\n" + result.stdout + result.stderr
        )


def _write_deterministic_zip(
    files: list[tuple[Path, str]], staging_root: Path, zip_path: Path
) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for _, arcname in sorted(files, key=lambda pair: pair[1]):
            data = (staging_root / arcname).read_bytes()
            info = zipfile.ZipInfo(arcname, date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # unix, so external_attr permission bits are honored
            info.external_attr = 0o644 << 16
            archive.writestr(info, data, compresslevel=9)


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _update_sha256sums(root: Path, rel_zip_path: str, digest: str) -> None:
    sums_path = root / "SHA256SUMS.txt"
    existing = sums_path.read_text().splitlines() if sums_path.exists() else []
    kept = [line for line in existing if line.strip() and not line.endswith(f"  {rel_zip_path}")]
    kept.append(f"{digest}  {rel_zip_path}")
    sums_path.write_text("\n".join(kept) + "\n")


def _update_release_manifest(root: Path, rel_zip_path: str, digest: str, version: str) -> None:
    manifest_path = root / "RELEASE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    artifacts = manifest.setdefault("release_artifacts", [])
    artifacts[:] = [a for a in artifacts if a.get("path") != rel_zip_path]
    artifacts.append(
        {
            "path": rel_zip_path,
            "sha256": digest,
            "version": version,
            "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


def build(root: Path) -> Path:
    version = _read_version(root)
    files = collect_release_files(root)
    with tempfile.TemporaryDirectory() as tmp_name:
        staging_root = Path(tmp_name)
        _stage(files, staging_root)
        _run_security_scan(staging_root)
        zip_path = root / "dist" / f"scout-portfolio-{version}.zip"
        _write_deterministic_zip(files, staging_root, zip_path)
    return zip_path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    zip_path = build(root)
    digest = _sha256_of_file(zip_path)
    rel_zip_path = zip_path.relative_to(root).as_posix()
    version = _read_version(root)
    _update_sha256sums(root, rel_zip_path, digest)
    _update_release_manifest(root, rel_zip_path, digest, version)
    print(f"built {rel_zip_path}")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

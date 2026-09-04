"""Generate the Codex host layout from the canonical Claude Code plugin tree.

Canonical sources (never edit the generated output by hand, regenerate it):
  - `.claude-plugin/plugin.json`      -> `codex/plugins/<name>/.codex-plugin/plugin.json`
  - `.claude-plugin/marketplace.json` -> `codex/.agents/plugins/marketplace.json`
  - `skills/`                          -> `codex/plugins/<name>/skills/`
  - `agents/` (if present)             -> `codex/plugins/<name>/agents/`

This repo has no `agents/` directory today; the mirror step is a no-op until one
exists, which keeps the generator correct without a special case later.

Claude Code is the primary host (see RELEASE-MANIFEST.json's `primary_host`).
Codex local marketplace is the first fallback host. A `claude/` mirror
directory, the shape the augment-builder reference bar uses when a product
repo is separate from its plugin folder, is deliberately SKIPPED here: this
repo's root already IS the Claude Code plugin (`.claude-plugin/` lives at the
repo root, see plugin-creator's "Step 1: Repo = plugin = runtime"). Mirroring
root into `claude/<name>/` would duplicate the same files under two paths in
the same tree for zero benefit, so this script only ever writes `codex/`.

Usage:
    python scripts/build_host_layouts.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path.cwd()
CLAUDE_PLUGIN_DIR = ROOT / ".claude-plugin"
SKILLS_DIR = ROOT / "skills"
AGENTS_DIR = ROOT / "agents"
CODEX_DIR = ROOT / "codex"


def _load_plugin_name() -> str:
    plugin_json = json.loads((CLAUDE_PLUGIN_DIR / "plugin.json").read_text())
    name = plugin_json.get("name")
    if not name:
        raise SystemExit("`.claude-plugin/plugin.json` is missing a `name` field")
    return str(name)


def _write_codex_plugin_manifest(plugin_dir: Path) -> None:
    plugin_json = json.loads((CLAUDE_PLUGIN_DIR / "plugin.json").read_text())
    codex_plugin_dir = plugin_dir / ".codex-plugin"
    codex_plugin_dir.mkdir(parents=True, exist_ok=True)
    (codex_plugin_dir / "plugin.json").write_text(json.dumps(plugin_json, indent=2) + "\n")


def _write_codex_marketplace(name: str) -> None:
    marketplace = json.loads((CLAUDE_PLUGIN_DIR / "marketplace.json").read_text())
    codex_marketplace = {
        "name": marketplace.get("name", name),
        "owner": marketplace.get("owner", {}),
        "description": marketplace.get("description", ""),
        "plugins": [
            {
                "name": name,
                "source": {"source": "local", "path": f"./plugins/{name}"},
                "description": next(
                    (
                        p.get("description", "")
                        for p in marketplace.get("plugins", [])
                        if p.get("name") == name
                    ),
                    "",
                ),
            }
        ],
    }
    agents_plugins_dir = CODEX_DIR / ".agents" / "plugins"
    agents_plugins_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(codex_marketplace, indent=2) + "\n"
    (agents_plugins_dir / "marketplace.json").write_text(payload)


def _mirror_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    if src.exists():
        shutil.copytree(src, dst)


def build() -> Path:
    name = _load_plugin_name()
    plugin_dir = CODEX_DIR / "plugins" / name

    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)
    plugin_dir.mkdir(parents=True, exist_ok=True)

    _write_codex_plugin_manifest(plugin_dir)
    _mirror_dir(SKILLS_DIR, plugin_dir / "skills")
    if AGENTS_DIR.exists():
        _mirror_dir(AGENTS_DIR, plugin_dir / "agents")
    _write_codex_marketplace(name)
    return plugin_dir


def main() -> int:
    plugin_dir = build()
    marketplace_path = CODEX_DIR / ".agents" / "plugins" / "marketplace.json"
    print(f"built codex host layout at {plugin_dir.relative_to(ROOT)}")
    print(f"built codex marketplace catalog at {marketplace_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Guard against the package version drifting from pyproject.toml."""

import tomllib
from pathlib import Path

import scout_portfolio_manager

ROOT = Path(__file__).resolve().parents[1]


def test_package_version_matches_pyproject():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    expected = pyproject["project"]["version"]
    assert scout_portfolio_manager.__version__ == expected

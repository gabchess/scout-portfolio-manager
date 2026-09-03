from pathlib import Path

from scripts.check_plugin_manifest import check as check_plugin_manifest
from scripts.security_scan import scan

ROOT = Path(__file__).parents[1]


def test_repository_has_no_credential_shaped_secrets():
    assert scan(ROOT) == []


def test_secret_scan_detects_private_key_in_fixture_tree(tmp_path):
    (tmp_path / "example.txt").write_text("token = '0x" + "a" * 64 + "'\n")
    assert scan(tmp_path) == [str(tmp_path / "example.txt") + ":1"]


def test_plugin_manifest_and_readme_contract_is_complete():
    assert check_plugin_manifest(ROOT) == []

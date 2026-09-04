import json
from pathlib import Path

import pytest

from scout_portfolio_manager import mcp_server
from scout_portfolio_manager.host import ReadOnlyHost

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "portfolio.json"


def test_build_host_uses_explicit_fixture_override(monkeypatch):
    monkeypatch.setenv("ZPM_FIXTURE_PATH", str(FIXTURE))
    assert isinstance(mcp_server.build_host(), ReadOnlyHost)
    assert mcp_server.build_host().get_pnl()["results"][0]["unrealized_usd"] == 250.0


def test_require_mcp_fails_with_install_hint(monkeypatch):
    real_import = __import__

    def no_mcp(name, *args, **kwargs):
        if name == "mcp.server.fastmcp":
            raise ImportError("missing test dependency")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", no_mcp)
    with pytest.raises(SystemExit, match="pip install -e"):
        mcp_server._require_mcp()


def test_create_server_registers_only_read_tools(monkeypatch):
    registered = {}

    class FakeMCP:
        def __init__(self, name, instructions):
            self.name = name
            self.instructions = instructions

        def tool(self, name):
            def decorator(function):
                registered[name] = function
                return function

            return decorator

    monkeypatch.setattr(mcp_server, "_require_mcp", lambda: FakeMCP)
    server = mcp_server.create_server(ReadOnlyHost(FIXTURE))
    assert server.name == "scout-portfolio"
    assert list(registered) == [
        "get_portfolio_snapshot",
        "get_pnl",
        "parse_dca_request",
        "preview_dca",
    ]
    assert not any("execute" in name for name in registered)
    payload = json.loads(registered["get_pnl"]())
    assert payload["results"][0]["unrealized_usd"] == 250.0

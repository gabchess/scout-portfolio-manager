"""Execution-boundary regression test.

CLAIMS.md: "Host and MCP have no execute, sign, or submit tool. Fake
execution adapter is test-only." That line was previously a docstring
convention (see `host.py`'s "FakeExecutionAdapter is test-only and is not
part of this host or MCP surface."), not something CI checked. This file
converts it into two mechanical CI gates:

(a) AST-scans `host.py` and `mcp_server.py`'s import statements, then walks
    the local `scout_portfolio_manager` module import graph those two
    entry points reach, and asserts the walk never reaches `adapters.py`
    (the only module that defines `FakeExecutionAdapter`) and that neither
    entry point names `FakeExecutionAdapter` directly. AST scanning (not
    importing and inspecting `sys.modules`) is enough here: the claim is
    about what the source *imports*, and a static parse answers that without
    executing any of the code under test.
(b) Boots the real MCP server (genuine `mcp.server.fastmcp.FastMCP`, not a
    monkeypatched fake) and asserts its registered tool set is EXACTLY the
    8 tools this release ships. A 9th tool, a rename, or a dropped tool
    fails this test until it is updated deliberately.
"""

from __future__ import annotations

import ast
import asyncio
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src" / "scout_portfolio_manager"

ENTRY_MODULES = ("host", "mcp_server")
FORBIDDEN_MODULE = "adapters"
FORBIDDEN_NAME = "FakeExecutionAdapter"

EXPECTED_TOOLS = frozenset(
    {
        "get_portfolio_snapshot",
        "get_pnl",
        "parse_dca_request",
        "preview_dca",
        "analyze_asset",
        "dca_windows",
        "set_alert",
        "check_alerts",
    }
)


def _parse(module_name: str) -> ast.Module:
    path = SRC / f"{module_name}.py"
    return ast.parse(path.read_text(), filename=str(path))


def _local_module_imports(module_name: str) -> set[str]:
    """Sibling `scout_portfolio_manager` module names `module_name.py` imports."""
    imported: set[str] = set()
    for node in ast.walk(_parse(module_name)):
        if isinstance(node, ast.ImportFrom):
            if node.level >= 1:
                # `from . import x` (module=None) or `from .x import y` (module="x")
                if node.module:
                    imported.add(node.module.split(".")[0])
                else:
                    for alias in node.names:
                        imported.add(alias.name)
            elif node.module and node.module.startswith("scout_portfolio_manager."):
                imported.add(node.module.split(".")[1])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("scout_portfolio_manager."):
                    imported.add(alias.name.split(".")[1])
    return imported


def _imported_names(module_name: str) -> set[str]:
    """Every name a module's `import`/`from ... import` statements bind."""
    names: set[str] = set()
    for node in ast.walk(_parse(module_name)):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def test_host_and_mcp_server_never_import_fake_execution_adapter_directly():
    for entry in ENTRY_MODULES:
        assert FORBIDDEN_NAME not in _imported_names(entry), (
            f"{entry}.py imports {FORBIDDEN_NAME} directly; CLAIMS.md says "
            "host/mcp_server carry no execution surface"
        )


def test_host_and_mcp_server_never_transitively_import_adapters_module():
    for entry in ENTRY_MODULES:
        seen: set[str] = set()
        frontier = {entry}
        while frontier:
            module_name = frontier.pop()
            if module_name in seen:
                continue
            seen.add(module_name)
            assert module_name != FORBIDDEN_MODULE, (
                f"{entry}.py transitively imports {FORBIDDEN_MODULE}.py "
                f"(the only module defining {FORBIDDEN_NAME}); this breaks "
                "the execution boundary CLAIMS.md describes"
            )
            if not (SRC / f"{module_name}.py").is_file():
                continue
            frontier |= _local_module_imports(module_name) - seen


def test_mcp_server_tool_registry_is_pinned_to_the_named_eight():
    mcp = pytest.importorskip("mcp", reason="mcp extra not installed")
    del mcp
    from scout_portfolio_manager.host import default_host
    from scout_portfolio_manager.mcp_server import create_server

    server = create_server(default_host())
    tools = asyncio.run(server.list_tools())
    tool_names = {tool.name for tool in tools}
    assert tool_names == EXPECTED_TOOLS

"""Smoke tests for the demo HTTP server.

Starts the real ``DemoHandler`` on an ephemeral port (never the hardcoded
8787, to avoid CI port collisions) and exercises the four endpoints named in
the demo's own README, plus two safety properties: a non-dict JSON body
returns 400 instead of crashing the request thread, and the server binds
only to 127.0.0.1.

``server.py`` lives in a hyphenated directory that is not an importable
Python package, so it is loaded here by file path via ``importlib``.
"""

from __future__ import annotations

import importlib.util
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import ModuleType
from typing import Any, Iterator

import pytest

SERVER_PATH = Path(__file__).resolve().parent / "server.py"


def _load_server_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("demo_server", SERVER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


server = _load_server_module()


@pytest.fixture
def running_server() -> Iterator[ThreadingHTTPServer]:
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.DemoHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        thread.join(timeout=5)


def _url(httpd: ThreadingHTTPServer, path: str) -> str:
    host = str(httpd.server_address[0])
    port = httpd.server_address[1]
    return f"http://{host}:{port}{path}"


def _get_json(httpd: ThreadingHTTPServer, path: str) -> dict[str, Any]:
    with urllib.request.urlopen(_url(httpd, path)) as response:
        result: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        return result


def _post_json(httpd: ThreadingHTTPServer, path: str, body: bytes) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        _url(httpd, path),
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            payload: dict[str, Any] = json.loads(response.read().decode("utf-8"))
            return response.status, payload
    except urllib.error.HTTPError as exc:
        error_payload: dict[str, Any] = json.loads(exc.read().decode("utf-8"))
        return exc.code, error_payload


def test_binds_only_to_loopback(running_server: ThreadingHTTPServer) -> None:
    assert running_server.server_address[0] == "127.0.0.1"


def test_get_snapshot(running_server: ThreadingHTTPServer) -> None:
    result = _get_json(running_server, "/api/snapshot")
    assert result["status"] == "ok"
    assert result["boundary"] == "observe"
    assert result["snapshot"]["holdings"][0]["asset"] == "ETH"


def test_get_pnl(running_server: ThreadingHTTPServer) -> None:
    result = _get_json(running_server, "/api/pnl")
    assert result["status"] == "ok"
    assert result["boundary"] == "calculate"
    assert result["results"][0]["asset"] == "ETH"


def test_get_pnl_filtered_by_asset(running_server: ThreadingHTTPServer) -> None:
    result = _get_json(running_server, "/api/pnl?asset=ETH")
    assert result["status"] == "ok"
    assert result["results"][0]["asset"] == "ETH"


def test_post_dca_parse_needs_clarification(running_server: ThreadingHTTPServer) -> None:
    body = json.dumps({"text": "DCA another $300 of ETH"}).encode("utf-8")
    status, result = _post_json(running_server, "/api/dca/parse", body)
    assert status == 200
    assert result["status"] == "needs_clarification"


def test_post_dca_preview_complete_request(running_server: ThreadingHTTPServer) -> None:
    text = "DCA $300 ETH on ethereum weekly from wallet:0xabc123 to wallet:0xdef456"
    body = json.dumps({"text": text}).encode("utf-8")
    status, result = _post_json(running_server, "/api/dca/preview", body)
    assert status == 200
    assert result["approval_state"] == "required"
    assert result["execution_available"] is False


@pytest.mark.parametrize("raw_body", [b"[1, 2, 3]", b'"just a string"', b"null", b"42"])
def test_post_with_non_dict_json_body_returns_400_not_a_crash(
    running_server: ThreadingHTTPServer, raw_body: bytes
) -> None:
    status, result = _post_json(running_server, "/api/dca/parse", raw_body)
    assert status == 400
    assert result["status"] == "error"


def test_post_with_malformed_json_returns_400(running_server: ThreadingHTTPServer) -> None:
    status, result = _post_json(running_server, "/api/dca/parse", b"{not json")
    assert status == 400
    assert result["status"] == "error"


def test_unknown_api_route_returns_404_not_execute(running_server: ThreadingHTTPServer) -> None:
    body = json.dumps({"text": "anything"}).encode("utf-8")
    status, result = _post_json(running_server, "/api/dca/execute", body)
    assert status == 404
    assert result["status"] == "error"

"""Thin local demo server for the Zerion portfolio-manager agent demo.

Wraps scout_portfolio_manager.host.ReadOnlyHost behind four read-only JSON
endpoints and serves the static front-end. Stdlib only; no new dependencies.

Endpoints (all read-only; there is no execute/sign/submit endpoint):
    GET  /api/snapshot          -> host.get_portfolio_snapshot()
    GET  /api/pnl[?asset=ETH]   -> host.get_pnl(asset)
    POST /api/dca/parse         -> host.parse_dca_request(text)
    POST /api/dca/preview       -> host.preview_dca(text)

Run:
    python3 demo/zerion-portfolio-agent/server.py
"""

from __future__ import annotations

import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

DEMO_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEMO_DIR.parent.parent
FIXTURE_PATH = REPO_ROOT / "fixtures" / "portfolio.json"

# Allow running straight from a checkout without `pip install -e .`,
# as long as pydantic is importable.
sys.path.insert(0, str(REPO_ROOT / "src"))

from scout_portfolio_manager.host import ReadOnlyHost  # noqa: E402

HOST = ReadOnlyHost(FIXTURE_PATH)

MAX_BODY_BYTES = 16 * 1024


def _relativize_snapshot_locator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Rewrite an absolute fixture path in the snapshot response to a repo-relative
    one, so the demo UI never displays the host's home directory. Display-only: the
    fixture is still read from the absolute FIXTURE_PATH."""
    locator = payload.get("snapshot", {}).get("source", {}).get("locator")
    if not locator:
        return payload
    try:
        relative = str(Path(locator).relative_to(REPO_ROOT))
    except ValueError:
        relative = os.path.relpath(locator, REPO_ROOT)
    payload["snapshot"]["source"]["locator"] = relative
    return payload


class DemoHandler(SimpleHTTPRequestHandler):
    """Static files from the demo directory plus the read-only JSON API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(DEMO_DIR / "static"), **kwargs)

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_text_body(self) -> str:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ValueError("request body must be non-empty JSON under 16 KiB")
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("field 'text' must be a non-empty string")
        return text

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        parsed = urlparse(self.path)
        if parsed.path == "/api/snapshot":
            self._send_json(_relativize_snapshot_locator(HOST.get_portfolio_snapshot()))
            return
        if parsed.path == "/api/pnl":
            asset_values = parse_qs(parsed.query).get("asset")
            asset: str | None = asset_values[0] if asset_values else None
            self._send_json(HOST.get_pnl(asset=asset))
            return
        if parsed.path.startswith("/api/"):
            self._send_json({"status": "error", "error": "unknown endpoint"}, status=404)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 (http.server API)
        parsed = urlparse(self.path)
        routes = {
            "/api/dca/parse": HOST.parse_dca_request,
            "/api/dca/preview": HOST.preview_dca,
        }
        handler = routes.get(parsed.path)
        if handler is None:
            # No execute/sign/submit route exists; anything else is refused.
            self._send_json(
                {
                    "status": "error",
                    "error": "unknown endpoint; this demo server is read-only "
                    "and provides no execution capability",
                },
                status=404,
            )
            return
        try:
            text = self._read_text_body()
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json({"status": "error", "error": str(exc)}, status=400)
            return
        self._send_json(handler(text))

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("demo-server: %s\n" % (format % args))


def main() -> None:
    port = int(os.environ.get("DEMO_PORT", "8787"))
    server = ThreadingHTTPServer(("127.0.0.1", port), DemoHandler)
    print("Zerion portfolio-manager agent demo (fixture-backed, read-only)")
    print(f"Fixture: {FIXTURE_PATH}")
    print(f"Serving on http://127.0.0.1:{port}  (Ctrl-C to stop)")
    server.serve_forever()


if __name__ == "__main__":
    main()

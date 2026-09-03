import base64
import json
from urllib.error import HTTPError

import pytest

from zerion_portfolio_manager.zerion_api import (
    ZerionAPIAuthError,
    ZerionAPIConfig,
    ZerionAPIRateLimitError,
    ZerionAPIReader,
    ZerionAPITransportError,
)

PAYLOAD = {
    "data": {
        "attributes": {
            "positions_distribution_by_type": {"wallet": 1864.7, "staked": 66.1},
            "positions_distribution_by_chain": {"ethereum": 1214.0},
            "total": {"positions": 2017.485823},
            "changes": {"absolute_1d": 102.02, "percent_1d": 5.32},
        }
    }
}


def test_maps_aggregate_portfolio_and_does_not_invent_ledger_data():
    requests = []

    def transport(request, timeout):
        requests.append((request, timeout))
        return PAYLOAD

    key_field = "api" + "_key"
    reader = ZerionAPIReader(
        ZerionAPIConfig(
            **{key_field: "test-key"}, base_url="https://api.zerion.io/v1", timeout_seconds=3.5
        ),
        transport=transport,
    )
    snapshot = reader.snapshot("0xabc/123")

    assert snapshot.holdings[0].asset == "PORTFOLIO"
    assert snapshot.holdings[0].value_usd == pytest.approx(2017.485823)
    assert snapshot.transactions == []  # aggregate endpoint is not a ledger
    assert snapshot.source.kind == "zerion_api"
    request, timeout = requests[0]
    assert request.method == "GET"
    assert request.full_url == (
        "https://api.zerion.io/v1/wallets/0xabc%2F123/portfolio"
        "?filter%5Bpositions%5D=only_simple&currency=usd"
    )
    assert request.get_header("Authorization") == "Basic " + base64.b64encode(b"test-key:").decode()
    assert request.get_header("Accept") == "application/json"
    assert timeout == 3.5


def test_config_rejects_non_https_base_url():
    with pytest.raises(ValueError, match="https"):
        ZerionAPIConfig(**{"api" + "_key": "key"}, base_url="http://api.zerion.io/v1")


def test_config_rejects_unexpected_base_url_host():
    with pytest.raises(ValueError, match="api.zerion.io"):
        ZerionAPIConfig(**{"api" + "_key": "key"}, base_url="https://evil.example/v1")


def test_credentials_are_not_exposed_by_config_or_errors():
    key = "opaque" + "-credential"
    config = ZerionAPIConfig(**{"api" + "_key": key})
    assert key not in repr(config)

    def transport(_, __):
        raise RuntimeError("transport detail " + key)

    with pytest.raises(ZerionAPITransportError) as caught:
        ZerionAPIReader(config, transport=transport).snapshot("0xabc")
    assert key not in str(caught.value)


def test_invalid_aggregate_response_is_typed_error():
    with pytest.raises(Exception, match="valid portfolio total"):
        ZerionAPIReader(
            ZerionAPIConfig(**{"api" + "_key": "key"}),
            transport=lambda *_: {"data": {"attributes": {}}},
        ).snapshot("0xabc")


def test_http_statuses_are_typed_and_safe(monkeypatch):
    def fake_urlopen(request, timeout):
        raise HTTPError(request.full_url, 401, "opaque credential", {}, None)

    monkeypatch.setattr("zerion_portfolio_manager.zerion_api.urlopen", fake_urlopen)
    with pytest.raises(ZerionAPIAuthError) as auth:
        ZerionAPIReader(ZerionAPIConfig(**{"api" + "_key": "opaque-credential"})).snapshot("0xabc")
    assert auth.value.status == 401
    assert "opaque-credential" not in str(auth.value)

    def fake_rate_limit(request, timeout):
        raise HTTPError(request.full_url, 429, "opaque credential", {}, None)

    monkeypatch.setattr("zerion_portfolio_manager.zerion_api.urlopen", fake_rate_limit)
    with pytest.raises(ZerionAPIRateLimitError) as rate:
        ZerionAPIReader(ZerionAPIConfig(**{"api" + "_key": "opaque-credential"})).snapshot("0xabc")
    assert rate.value.status == 429


def test_non_object_json_is_transport_error(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(["not", "an", "object"]).encode()

    monkeypatch.setattr(
        "zerion_portfolio_manager.zerion_api.urlopen", lambda *_args, **_kwargs: Response()
    )
    with pytest.raises(ZerionAPITransportError, match="non-object"):
        ZerionAPIReader(ZerionAPIConfig(**{"api" + "_key": "key"})).snapshot("0xabc")

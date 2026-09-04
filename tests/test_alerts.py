from scout_portfolio_manager.alerts import AlertRule, AlertStore, evaluate_alert


def test_alert_store_round_trips_through_a_temp_path(tmp_path):
    store = AlertStore(tmp_path / "nested" / "alerts.json")
    rule = store.add(asset="eth", kind="rsi_below", threshold=30.0)
    assert rule.asset == "ETH"
    assert rule.kind == "rsi_below"
    assert (tmp_path / "nested" / "alerts.json").exists()

    reopened = AlertStore(tmp_path / "nested" / "alerts.json")
    listed = reopened.list()
    assert len(listed) == 1
    assert listed[0].id == rule.id


def test_alert_store_list_filters_by_asset(tmp_path):
    store = AlertStore(tmp_path / "alerts.json")
    store.add(asset="ETH", kind="rsi_below", threshold=30.0)
    store.add(asset="BTC", kind="rsi_below", threshold=25.0)
    assert len(store.list()) == 2
    assert [r.asset for r in store.list(asset="btc")] == ["BTC"]


def test_evaluate_alert_rsi_below_fires_when_under_threshold():
    rule = AlertRule(
        id="r1", asset="ETH", kind="rsi_below", threshold=30.0, created_at="2026-09-03T12:00:00Z"
    )
    analysis = {"indicators": {"rsi_14": 21.5}, "freshness": {"stale": False}}
    result = evaluate_alert(rule, analysis=analysis, pnl=None)
    assert result["fired"] is True
    assert result["observed_value"] == 21.5
    assert result["stale"] is False


def test_evaluate_alert_rsi_below_does_not_fire_when_over_threshold():
    rule = AlertRule(
        id="r1", asset="ETH", kind="rsi_below", threshold=30.0, created_at="2026-09-03T12:00:00Z"
    )
    analysis = {"indicators": {"rsi_14": 55.0}, "freshness": {"stale": False}}
    result = evaluate_alert(rule, analysis=analysis, pnl=None)
    assert result["fired"] is False
    assert result["observed_value"] == 55.0


def test_evaluate_alert_price_pct_below_cost_basis_fires():
    rule = AlertRule(
        id="r2",
        asset="ETH",
        kind="price_pct_below_cost_basis",
        threshold=10.0,
        created_at="2026-09-03T12:00:00Z",
    )
    analysis = {"indicators": {}, "freshness": {"stale": False}}
    pnl = {"results": [{"asset": "ETH", "return_pct": -15.0}]}
    result = evaluate_alert(rule, analysis=analysis, pnl=pnl)
    assert result["fired"] is True
    assert result["observed_value"] == -15.0


def test_evaluate_alert_price_pct_below_cost_basis_does_not_fire_above_threshold():
    rule = AlertRule(
        id="r2",
        asset="ETH",
        kind="price_pct_below_cost_basis",
        threshold=10.0,
        created_at="2026-09-03T12:00:00Z",
    )
    analysis = {"indicators": {}, "freshness": {"stale": False}}
    pnl = {"results": [{"asset": "ETH", "return_pct": 5.0}]}
    result = evaluate_alert(rule, analysis=analysis, pnl=pnl)
    assert result["fired"] is False


def test_evaluate_alert_stale_propagates_without_changing_fire_decision():
    rule = AlertRule(
        id="r1", asset="ETH", kind="rsi_below", threshold=30.0, created_at="2026-09-03T12:00:00Z"
    )
    analysis = {"indicators": {"rsi_14": 21.5}, "freshness": {"stale": True}}
    result = evaluate_alert(rule, analysis=analysis, pnl=None)
    assert result["fired"] is True  # unchanged by staleness
    assert result["stale"] is True


def test_evaluate_alert_observed_value_none_when_indicator_missing():
    rule = AlertRule(
        id="r1", asset="ETH", kind="rsi_below", threshold=30.0, created_at="2026-09-03T12:00:00Z"
    )
    analysis = {"indicators": {}, "freshness": {"stale": False}}
    result = evaluate_alert(rule, analysis=analysis, pnl=None)
    assert result["observed_value"] is None
    assert result["fired"] is False

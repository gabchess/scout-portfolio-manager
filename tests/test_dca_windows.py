import pytest

from scout_portfolio_manager.dca_windows import SIZING_FRACTION, classify_window


def test_favorable_requires_both_rsi_and_range_to_agree():
    result = classify_window(
        rsi_14=28.4,
        distance_from_range_pct={"from_low_pct": 8.1, "from_high_pct": -30.0},
        risk_profile="balanced",
    )
    assert result["label"] == "favorable"
    assert "28.4" in result["rationale"]
    assert "8.1" in result["rationale"]


def test_low_rsi_alone_is_not_favorable_without_range_agreement():
    result = classify_window(
        rsi_14=20.0,
        distance_from_range_pct={"from_low_pct": 40.0, "from_high_pct": -2.0},
        risk_profile="balanced",
    )
    assert result["label"] == "neutral"


def test_unfavorable_requires_both_rsi_and_range_to_agree():
    result = classify_window(
        rsi_14=75.0,
        distance_from_range_pct={"from_low_pct": 50.0, "from_high_pct": -1.0},
        risk_profile="balanced",
    )
    assert result["label"] == "unfavorable"


def test_high_rsi_alone_is_not_unfavorable_without_range_agreement():
    result = classify_window(
        rsi_14=80.0,
        distance_from_range_pct={"from_low_pct": 50.0, "from_high_pct": -20.0},
        risk_profile="balanced",
    )
    assert result["label"] == "neutral"


def test_neutral_by_missing_rsi():
    result = classify_window(
        rsi_14=None,
        distance_from_range_pct={"from_low_pct": 1.0, "from_high_pct": -1.0},
        risk_profile="balanced",
    )
    assert result["label"] == "neutral"
    assert result["rationale"] == "insufficient data to classify this window"


def test_neutral_by_missing_range_distance():
    result = classify_window(
        rsi_14=20.0,
        distance_from_range_pct=None,
        risk_profile="balanced",
    )
    assert result["label"] == "neutral"
    assert result["rationale"] == "insufficient data to classify this window"


@pytest.mark.parametrize(
    "risk_profile,expected_fraction",
    [("conservative", 0.25), ("balanced", 0.5), ("aggressive", 1.0)],
)
def test_sizing_fraction_by_risk_profile(risk_profile, expected_fraction):
    assert SIZING_FRACTION[risk_profile] == expected_fraction
    result = classify_window(
        rsi_14=50.0,
        distance_from_range_pct={"from_low_pct": 10.0, "from_high_pct": -10.0},
        risk_profile=risk_profile,
        amount_usd=300.0,
    )
    assert result["sizing_fraction"] == expected_fraction
    assert result["suggested_amount_usd"] == 300.0 * expected_fraction


def test_suggested_amount_omitted_when_amount_usd_is_none():
    result = classify_window(
        rsi_14=50.0,
        distance_from_range_pct={"from_low_pct": 10.0, "from_high_pct": -10.0},
        risk_profile="balanced",
    )
    assert "suggested_amount_usd" not in result


def test_invalid_risk_profile_raises():
    with pytest.raises(ValueError):
        classify_window(
            rsi_14=50.0,
            distance_from_range_pct={"from_low_pct": 10.0, "from_high_pct": -10.0},
            risk_profile="yolo",
        )

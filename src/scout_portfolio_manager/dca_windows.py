"""Pure DCA-window classification. No I/O.

Compound conditions only, never a single indicator touch: RSI pins at
extremes during strong trends (crypto-active-trading's finding), so
favorable/unfavorable requires RSI AND range-distance to agree. Missing data
classifies as neutral, never favorable or unfavorable: an unclassifiable
window is not a signal.
"""

from typing import Any, Dict, Literal, Optional

#: Fixed sizing-fraction convention, not a computed value: conservative gets
#: a quarter, balanced a half, aggressive the full requested amount.
SIZING_FRACTION = {"conservative": 0.25, "balanced": 0.5, "aggressive": 1.0}

RiskProfile = Literal["conservative", "balanced", "aggressive"]


def classify_window(
    *,
    rsi_14: Optional[float],
    distance_from_range_pct: Optional[Dict[str, float]],
    risk_profile: RiskProfile,
    amount_usd: Optional[float] = None,
) -> Dict[str, Any]:
    """Classify the *current* window only; never a forecast of a future day."""
    if risk_profile not in SIZING_FRACTION:
        raise ValueError(f"unknown risk_profile: {risk_profile!r}")

    from_low_pct = (distance_from_range_pct or {}).get("from_low_pct")
    from_high_pct = (distance_from_range_pct or {}).get("from_high_pct")

    label = "neutral"
    rationale = "insufficient data to classify this window"
    if rsi_14 is not None and from_low_pct is not None and rsi_14 < 35 and from_low_pct <= 15:
        label = "favorable"
        rationale = f"RSI 14 at {rsi_14:.1f} and {from_low_pct:.1f}% above the 30-day low"
    elif rsi_14 is not None and from_high_pct is not None and rsi_14 > 70 and from_high_pct >= -5:
        label = "unfavorable"
        rationale = f"RSI 14 at {rsi_14:.1f} and {from_high_pct:.1f}% from the 30-day high"
    elif rsi_14 is not None and from_low_pct is not None:
        rationale = f"RSI 14 at {rsi_14:.1f} and {from_low_pct:.1f}% above the 30-day low"

    sizing_fraction = SIZING_FRACTION[risk_profile]
    result = {
        "label": label,
        "risk_profile": risk_profile,
        "sizing_fraction": sizing_fraction,
        "rationale": rationale,
        "sensitivity_note": (
            "If RSI is off by 10 points, this classification could flip; treat as "
            "directional, not precise."
        ),
    }
    if amount_usd is not None:
        result["suggested_amount_usd"] = amount_usd * sizing_fraction
    return result

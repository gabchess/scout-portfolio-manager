from typing import Any, Dict

from .contracts import PortfolioSnapshot
from .pnl import calculate_pnl


def format_pnl_report(snapshot: PortfolioSnapshot) -> Dict[str, Any]:
    observed = [
        "%s: %.4f units, $%.2f current value" % (h.asset, h.quantity, h.value_usd)
        for h in snapshot.holdings
    ]
    calculated = []
    assumed = []
    unknown = []
    for holding in snapshot.holdings:
        buys = [t for t in snapshot.transactions if t.asset == holding.asset and t.kind == "buy"]
        basis = sum(t.value_usd + t.fee_usd for t in buys)
        if not basis:
            unknown.append("missing acquisition basis for %s" % holding.asset)
            continue
        result = calculate_pnl(
            holding=holding,
            basis_usd=basis,
            valuation_at=snapshot.observed_at,
            transactions=snapshot.transactions,
        )
        sign = "+" if result.total_usd >= 0 else ""
        calculated.append("%s$%.0f (%.1f%%)" % (sign, result.total_usd, result.return_pct))
        if result.fees_usd == 0:
            assumed.append("fees are zero because fixture fee is zero")
    return {"observed": observed, "calculated": calculated, "assumed": assumed, "unknown": unknown}

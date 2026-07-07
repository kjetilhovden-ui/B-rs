"""Rough price-range estimates for the next week and month.

This is deliberately a simple model: recent average daily return ("drift")
projected forward, with a band around it based on how much the price has
historically swung day to day ("volatility"). It is NOT a forecast in any
rigorous sense - it's a plain-language way of saying "if the recent trend
and typical swings continue, here's a rough range". The UI must always
label this as an uncertain estimate, never a guaranteed target.
"""

import statistics
import sqlite3

from .. import config

MIN_RETURNS_REQUIRED = 10


def compute_price_prediction(ok_snapshots: list[sqlite3.Row]) -> dict | None:
    closes = [s["close"] for s in ok_snapshots if s["close"] is not None]
    if len(closes) < MIN_RETURNS_REQUIRED + 1:
        return None

    returns = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes)) if closes[i - 1]]
    if len(returns) < MIN_RETURNS_REQUIRED:
        return None

    drift = statistics.mean(returns)
    volatility = statistics.stdev(returns) if len(returns) >= 2 else 0.0
    latest_close = closes[-1]

    return {
        "latest_close": latest_close,
        "basis_days": len(returns),
        "week": _horizon_range(latest_close, drift, volatility, config.PREDICTION_HORIZON_WEEK_DAYS),
        "month": _horizon_range(latest_close, drift, volatility, config.PREDICTION_HORIZON_MONTH_DAYS),
    }


def _horizon_range(latest_close: float, drift: float, volatility: float, horizon_days: int) -> dict:
    projected_return = drift * horizon_days
    range_return = volatility * (horizon_days**0.5) * config.PREDICTION_RANGE_STD_DEVS
    return {
        "low": latest_close * (1 + projected_return - range_return),
        "mid": latest_close * (1 + projected_return),
        "high": latest_close * (1 + projected_return + range_return),
        "projected_return_pct": projected_return,
    }

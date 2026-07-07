"""Run from the etl/ directory with: python -m pytest"""

from etl.scoring.prediction import MIN_RETURNS_REQUIRED, compute_price_prediction


def _fake_snapshots(closes: list[float]) -> list[dict]:
    return [{"close": c} for c in closes]


def test_returns_none_with_too_little_history():
    closes = [100.0] * MIN_RETURNS_REQUIRED  # not quite enough returns
    assert compute_price_prediction(_fake_snapshots(closes)) is None


def test_flat_prices_give_a_flat_prediction():
    closes = [100.0] * (MIN_RETURNS_REQUIRED + 5)
    result = compute_price_prediction(_fake_snapshots(closes))
    assert result is not None
    assert result["week"]["mid"] == 100.0
    assert result["week"]["low"] == result["week"]["high"] == 100.0


def test_upward_trend_produces_higher_mid_than_latest_close():
    closes = [100.0 * (1.01**i) for i in range(MIN_RETURNS_REQUIRED + 5)]
    result = compute_price_prediction(_fake_snapshots(closes))
    assert result is not None
    assert result["week"]["mid"] > result["latest_close"]
    assert result["month"]["mid"] > result["week"]["mid"]


def test_range_widens_for_longer_horizon():
    closes = [100.0 + (i % 3) for i in range(MIN_RETURNS_REQUIRED + 10)]
    result = compute_price_prediction(_fake_snapshots(closes))
    assert result is not None
    week_width = result["week"]["high"] - result["week"]["low"]
    month_width = result["month"]["high"] - result["month"]["low"]
    assert month_width > week_width


def test_low_mid_high_are_ordered():
    closes = [100.0 - 0.2 * i + (i % 2) for i in range(MIN_RETURNS_REQUIRED + 8)]
    result = compute_price_prediction(_fake_snapshots(closes))
    assert result is not None
    for horizon in ("week", "month"):
        assert result[horizon]["low"] <= result[horizon]["mid"] <= result[horizon]["high"]

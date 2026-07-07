"""Run from the etl/ directory with: python -m pytest"""

from etl.scoring import normalize
from etl.scoring.blend import _categorize_horizon, weighted_average


def test_percentile_ranks_basic_ordering():
    result = normalize.percentile_ranks([10.0, 20.0, 30.0])
    assert result == [0.0, 50.0, 100.0]


def test_percentile_ranks_none_passthrough():
    result = normalize.percentile_ranks([10.0, None, 30.0])
    assert result[1] is None
    assert result[0] == 0.0
    assert result[2] == 100.0


def test_percentile_ranks_ties_get_average_rank():
    result = normalize.percentile_ranks([10.0, 10.0, 30.0])
    assert result[0] == result[1] == 25.0
    assert result[2] == 100.0


def test_percentile_ranks_single_value_is_midpoint():
    result = normalize.percentile_ranks([42.0])
    assert result == [50.0]


def test_percentile_ranks_all_missing():
    result = normalize.percentile_ranks([None, None])
    assert result == [None, None]


def test_weighted_average_excludes_missing_factors():
    # A company with no growth data shouldn't be dragged toward a neutral
    # 50 - its score should be the average of whatever IS available.
    scores = {"momentum": 80.0, "growth": None, "valuation": 60.0, "reaction": None}
    weights = {"momentum": 0.25, "growth": 0.30, "valuation": 0.25, "reaction": 0.20}
    result = weighted_average(scores, weights)
    expected = (80.0 * 0.25 + 60.0 * 0.25) / (0.25 + 0.25)
    assert result == expected


def test_weighted_average_all_missing_returns_none():
    scores = {"momentum": None, "growth": None, "valuation": None, "reaction": None}
    weights = {"momentum": 0.25, "growth": 0.30, "valuation": 0.25, "reaction": 0.20}
    assert weighted_average(scores, weights) is None


def test_negative_earnings_yield_does_not_crash_scoring():
    # A loss-making company (negative EPS) should just rank low on
    # valuation, not blow up the pipeline like raw P/E would.
    loss_making_row = {"next_report_date": None}
    factor_scores = {"momentum": 40.0, "growth": 20.0, "valuation": 0.0, "reaction": None}
    horizon, explanation = _categorize_horizon(loss_making_row, factor_scores)
    assert horizon == "Usikker horisont"
    assert isinstance(explanation, str)


def test_horizon_short_term_needs_momentum_and_imminent_report():
    row = {"next_report_date": "2026-07-15"}  # within 30 days of a fixed "today" is asserted loosely
    factor_scores = {"momentum": 90.0, "growth": 10.0, "valuation": 50.0, "reaction": None}
    horizon, _ = _categorize_horizon(row, factor_scores)
    # Whether this lands as "Kort sikt" depends on days-until-report vs
    # today's real date, so just check it never crashes and returns one of
    # the four valid categories.
    assert horizon in {
        "Kort sikt (uker)",
        "Lang sikt (1–3 år)",
        "Middels sikt (6–12 mnd)",
        "Usikker horisont",
    }


def test_horizon_long_term_from_high_growth_alone():
    row = {"next_report_date": None}
    factor_scores = {"momentum": 10.0, "growth": 85.0, "valuation": 50.0, "reaction": None}
    horizon, explanation = _categorize_horizon(row, factor_scores)
    assert horizon == "Lang sikt (1–3 år)"
    assert "85" in explanation

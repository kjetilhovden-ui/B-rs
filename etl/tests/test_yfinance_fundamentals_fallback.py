"""Tests for the income-statement-based fundamentals fallback, used when
Yahoo's quick-stats "info" fields are empty (the common case we found for
Oslo Børs tickers). Uses real pandas objects but no network - these are
pure functions over already-fetched data.

Run from the etl/ directory with: python -m pytest
"""

import pandas as pd

from etl.sources.yfinance_source import _first_matching_row, _income_statement_fundamentals, _yoy_growth


def _fake_income_stmt(latest_col, prior_col, net_income, revenue):
    return pd.DataFrame(
        {
            latest_col: {"Net Income": net_income[0], "Total Revenue": revenue[0]},
            prior_col: {"Net Income": net_income[1], "Total Revenue": revenue[1]},
        }
    )


def test_yoy_growth_basic():
    row = pd.Series({"2026-01-01": 120.0, "2025-01-01": 100.0})
    columns = ["2026-01-01", "2025-01-01"]
    assert _yoy_growth(row, columns) == 0.2


def test_yoy_growth_handles_zero_prior_value():
    row = pd.Series({"2026-01-01": 50.0, "2025-01-01": 0.0})
    columns = ["2026-01-01", "2025-01-01"]
    assert _yoy_growth(row, columns) is None


def test_yoy_growth_handles_negative_prior_value():
    # Went from a loss to a profit - growth is directionally positive,
    # magnitude relative to the loss size (abs(prior)).
    row = pd.Series({"2026-01-01": 10.0, "2025-01-01": -20.0})
    columns = ["2026-01-01", "2025-01-01"]
    assert _yoy_growth(row, columns) == (10.0 - -20.0) / 20.0


def test_first_matching_row_prefers_first_available_name():
    df = pd.DataFrame({"2026": {"Net Income Common Stockholders": 5.0}})
    row = _first_matching_row(df, ["Net Income", "Net Income Common Stockholders"])
    assert row is not None
    assert row["2026"] == 5.0


def test_first_matching_row_returns_none_when_nothing_matches():
    df = pd.DataFrame({"2026": {"Some Other Line": 5.0}})
    assert _first_matching_row(df, ["Net Income"]) is None


class _FakeTicker:
    def __init__(self, income_stmt, quarterly_income_stmt=None):
        self.income_stmt = income_stmt
        # Real yfinance.Ticker always has this attribute (empty DataFrame if
        # unavailable) - matching that shape here avoids spurious
        # AttributeError-driven retries in tests.
        self.quarterly_income_stmt = quarterly_income_stmt if quarterly_income_stmt is not None else pd.DataFrame()


def test_income_statement_fundamentals_computes_eps_and_growth():
    stmt = _fake_income_stmt("2026-12-31", "2025-12-31", net_income=[120.0, 100.0], revenue=[1200.0, 1000.0])
    ticker = _FakeTicker(stmt)
    info = {"sharesOutstanding": 60.0}

    eps, earnings_growth, revenue_growth = _income_statement_fundamentals(ticker, info)

    assert eps == 120.0 / 60.0
    assert earnings_growth == 0.2
    assert revenue_growth == 0.2


def test_income_statement_fundamentals_handles_missing_shares_outstanding():
    stmt = _fake_income_stmt("2026-12-31", "2025-12-31", net_income=[120.0, 100.0], revenue=[1200.0, 1000.0])
    ticker = _FakeTicker(stmt)
    info = {}  # no sharesOutstanding available

    eps, earnings_growth, revenue_growth = _income_statement_fundamentals(ticker, info)

    assert eps is None
    assert earnings_growth == 0.2


def test_income_statement_fundamentals_handles_empty_statement():
    ticker = _FakeTicker(pd.DataFrame())
    eps, earnings_growth, revenue_growth = _income_statement_fundamentals(ticker, {})
    assert (eps, earnings_growth, revenue_growth) == (None, None, None)


def test_income_statement_fundamentals_falls_back_to_quarterly():
    # Annual is empty, but quarterly has 5 periods (so a same-quarter-last-year
    # comparison, 4 periods back, is possible).
    quarterly = pd.DataFrame(
        {
            "2026-Q4": {"Net Income": 130.0, "Total Revenue": 1300.0},
            "2026-Q3": {"Net Income": 125.0, "Total Revenue": 1250.0},
            "2026-Q2": {"Net Income": 120.0, "Total Revenue": 1200.0},
            "2026-Q1": {"Net Income": 115.0, "Total Revenue": 1150.0},
            "2025-Q4": {"Net Income": 100.0, "Total Revenue": 1000.0},
        }
    )
    ticker = _FakeTicker(pd.DataFrame(), quarterly_income_stmt=quarterly)
    info = {"sharesOutstanding": 65.0}

    eps, earnings_growth, revenue_growth = _income_statement_fundamentals(ticker, info)

    assert eps == 130.0 / 65.0
    assert earnings_growth == 0.3
    assert revenue_growth == 0.3

"""Concrete PriceSource implementation backed by yfinance / Yahoo Finance.

Yahoo Finance's .OL tickers (Oslo Børs) and Morningstar-style fund codes
(e.g. "0P0001EFNB.IR" for DNB Norge) are unofficial - yfinance scrapes an
API Yahoo doesn't publish a contract for, so field availability varies a lot
per ticker and requests occasionally fail transiently (rate limiting is
common when fetching many tickers back-to-back). Callers should always be
ready for missing fields or a raised exception even after retries.
"""

import math
import time

from .. import config
from .price_source import Fundamentals, PriceBar

import yfinance as yf


class YFinanceSource:
    def get_history(self, ticker: str, lookback_days: int) -> list[PriceBar]:
        # Extra buffer beyond the requested lookback to absorb weekends,
        # public holidays, and the occasional missing trading day.
        period_days = lookback_days + 20

        def fetch():
            history = yf.Ticker(ticker).history(period=f"{period_days}d")
            if history.empty:
                raise ValueError(f"Ingen kursdata funnet for {ticker}")
            return history

        history = _with_retry(fetch)

        bars = []
        for index, row in history.iterrows():
            bars.append(
                PriceBar(
                    date=index.strftime("%Y-%m-%d"),
                    close=float(row["Close"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    volume=int(row["Volume"]) if not math.isnan(row["Volume"]) else None,
                )
            )
        return bars

    def get_fundamentals(self, ticker: str) -> Fundamentals:
        t = yf.Ticker(ticker)
        info = _with_retry(lambda: t.info or {})

        trailing_eps = _as_float(info.get("trailingEps"))
        earnings_growth = _as_float(info.get("earningsGrowth"))
        revenue_growth = _as_float(info.get("revenueGrowth"))

        # Yahoo's quick-stats "info" fields are frequently empty for
        # smaller/foreign listings (this is exactly what we found for most
        # Oslo Børs tickers). Fall back to computing growth/EPS ourselves
        # from the raw annual income statement, which tends to be better
        # populated than the pre-computed summary fields.
        if trailing_eps is None or earnings_growth is None or revenue_growth is None:
            stmt_eps, stmt_earnings_growth, stmt_revenue_growth = _income_statement_fundamentals(t, info)
            trailing_eps = trailing_eps if trailing_eps is not None else stmt_eps
            earnings_growth = earnings_growth if earnings_growth is not None else stmt_earnings_growth
            revenue_growth = revenue_growth if revenue_growth is not None else stmt_revenue_growth

        return Fundamentals(
            trailing_eps=trailing_eps,
            earnings_growth=earnings_growth,
            revenue_growth=revenue_growth,
        )


def _income_statement_fundamentals(t: "yf.Ticker", info: dict) -> tuple[float | None, float | None, float | None]:
    # Annual statements first (1 period back = YoY); if Yahoo has nothing
    # there (common for smaller/foreign listings), fall back to quarterly
    # statements (4 periods back = same quarter last year), which are
    # sometimes populated even when the annual view is empty.
    result = _statement_fundamentals(t, info, lambda ticker: ticker.income_stmt, periods_back=1)
    if result != (None, None, None):
        return result
    return _statement_fundamentals(t, info, lambda ticker: ticker.quarterly_income_stmt, periods_back=4)


def _statement_fundamentals(
    t: "yf.Ticker", info: dict, get_stmt, periods_back: int
) -> tuple[float | None, float | None, float | None]:
    try:
        stmt = _with_retry(lambda: get_stmt(t))
    except Exception:
        return None, None, None
    if stmt is None or stmt.empty:
        return None, None, None

    columns = sorted(stmt.columns, reverse=True)  # most recent period first
    if len(columns) <= periods_back:
        return None, None, None

    net_income_row = _first_matching_row(stmt, ["Net Income", "Net Income Common Stockholders"])
    revenue_row = _first_matching_row(stmt, ["Total Revenue", "Operating Revenue"])

    earnings_growth = _yoy_growth(net_income_row, columns, periods_back)
    revenue_growth = _yoy_growth(revenue_row, columns, periods_back)

    trailing_eps = None
    shares = _as_float(info.get("sharesOutstanding"))
    if net_income_row is not None and shares:
        latest_net_income = net_income_row.get(columns[0])
        if latest_net_income is not None and not _is_nan(latest_net_income):
            trailing_eps = float(latest_net_income) / shares

    return trailing_eps, earnings_growth, revenue_growth


def _first_matching_row(df, row_names: list[str]):
    for name in row_names:
        if name in df.index:
            return df.loc[name]
    return None


def _yoy_growth(row, columns, periods_back: int = 1) -> float | None:
    if row is None:
        return None
    latest = row.get(columns[0])
    prior = row.get(columns[periods_back])
    if latest is None or prior is None or _is_nan(latest) or _is_nan(prior) or prior == 0:
        return None
    return (float(latest) - float(prior)) / abs(float(prior))


def _is_nan(value) -> bool:
    try:
        return math.isnan(float(value))
    except (TypeError, ValueError):
        return False


def _with_retry(fn):
    last_exc: Exception | None = None
    for attempt in range(config.FETCH_RETRY_ATTEMPTS):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            if attempt < config.FETCH_RETRY_ATTEMPTS - 1:
                time.sleep(config.FETCH_RETRY_BACKOFF_SECONDS * (attempt + 1))
    raise last_exc


def _as_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

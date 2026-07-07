"""Concrete PriceSource implementation backed by yfinance / Yahoo Finance.

Yahoo Finance's .OL tickers (Oslo Børs) and Morningstar-style fund codes
(e.g. "0P0001EFNB.IR" for DNB Norge) are unofficial - yfinance scrapes an
API Yahoo doesn't publish a contract for, so field availability varies a lot
per ticker (funds in particular often lack trailingEps/earningsGrowth) and
the whole thing can break without notice. Callers should always be ready for
missing fields or a raised exception.
"""

import math

import yfinance as yf

from .price_source import Fundamentals, PriceBar


class YFinanceSource:
    def get_history(self, ticker: str, lookback_days: int) -> list[PriceBar]:
        # Extra buffer beyond the requested lookback to absorb weekends,
        # public holidays, and the occasional missing trading day.
        period_days = lookback_days + 20
        history = yf.Ticker(ticker).history(period=f"{period_days}d")

        if history.empty:
            raise ValueError(f"Ingen kursdata funnet for {ticker}")

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
        info = yf.Ticker(ticker).info or {}

        return Fundamentals(
            trailing_eps=_as_float(info.get("trailingEps")),
            earnings_growth=_as_float(info.get("earningsGrowth")),
            revenue_growth=_as_float(info.get("revenueGrowth")),
        )


def _as_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

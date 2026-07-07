"""Interface for a market data source.

yfinance is unofficial and can break without warning. Every other module in
this codebase talks to this interface, never to yfinance directly - so if
yfinance ever stops working, only yfinance_source.py needs to be replaced.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class PriceBar:
    date: str  # ISO date, "YYYY-MM-DD"
    close: float
    high: float
    low: float
    volume: int | None


@dataclass
class Fundamentals:
    trailing_eps: float | None
    earnings_growth: float | None  # YoY fraction, e.g. 0.12 = +12%
    revenue_growth: float | None  # YoY fraction, used as fallback


class PriceSource(Protocol):
    def get_history(self, ticker: str, lookback_days: int) -> list[PriceBar]:
        """Return daily bars, oldest first. Raises on total failure
        (ticker not found, network error) - caller is responsible for
        catching and recording data_status='missing'."""
        ...

    def get_fundamentals(self, ticker: str) -> Fundamentals:
        """Return whatever fundamentals are available. Individual fields
        may be None if Yahoo doesn't report them (common for smaller
        companies and funds) - that's a normal outcome, not an error."""
        ...

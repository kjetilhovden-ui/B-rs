"""Fetches price history and fundamentals for every active asset and stores
them in daily_snapshots.

Each asset is fetched independently inside its own try/except - if one
ticker fails (delisted, rate-limited, typo, temporary Yahoo hiccup), that
asset is marked data_status='missing' and the run continues. A bad ticker
must never take down the whole daily update.
"""

import sqlite3
import time
from datetime import date

from .. import config
from ..sources.price_source import PriceSource


def fetch_all(conn: sqlite3.Connection, source: PriceSource) -> list[dict]:
    """Returns a list of {ticker, status, note} for the run summary/warnings."""
    results = []
    assets = conn.execute(
        "SELECT id, ticker FROM assets WHERE active = 1"
    ).fetchall()

    for i, asset in enumerate(assets):
        if i > 0:
            # A short pause between assets meaningfully cuts down on
            # Yahoo rate-limiting a burst of back-to-back requests.
            time.sleep(config.FETCH_DELAY_BETWEEN_ASSETS_SECONDS)
        result = _fetch_one(conn, source, asset["id"], asset["ticker"])
        results.append(result)

    conn.commit()
    return results


def _fetch_one(conn: sqlite3.Connection, source: PriceSource, asset_id: int, ticker: str) -> dict:
    try:
        lookback = max(config.MOMENTUM_LOOKBACK_DAYS, config.PREDICTION_VOLATILITY_LOOKBACK_DAYS)
        bars = source.get_history(ticker, lookback)
    except Exception as exc:
        note = f"Klarte ikke hente kursdata: {exc}"
        conn.execute(
            """
            INSERT INTO daily_snapshots (asset_id, snapshot_date, data_status, data_note)
            VALUES (?, ?, 'missing', ?)
            ON CONFLICT(asset_id, snapshot_date) DO UPDATE SET
                data_status = 'missing', data_note = excluded.data_note
            """,
            (asset_id, date.today().isoformat(), note),
        )
        return {"ticker": ticker, "status": "missing", "note": note}

    fundamentals_note = None
    try:
        fundamentals = source.get_fundamentals(ticker)
    except Exception as exc:
        fundamentals = None
        fundamentals_note = f"Klarte ikke hente nøkkeltall: {exc}"

    latest_date = bars[-1].date
    for bar in bars:
        is_latest = bar.date == latest_date
        conn.execute(
            """
            INSERT INTO daily_snapshots
                (asset_id, snapshot_date, close, high, low, volume,
                 trailing_eps, earnings_growth, revenue_growth,
                 data_status, data_note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ok', ?)
            ON CONFLICT(asset_id, snapshot_date) DO UPDATE SET
                close = excluded.close, high = excluded.high, low = excluded.low,
                volume = excluded.volume,
                trailing_eps = COALESCE(excluded.trailing_eps, daily_snapshots.trailing_eps),
                earnings_growth = COALESCE(excluded.earnings_growth, daily_snapshots.earnings_growth),
                revenue_growth = COALESCE(excluded.revenue_growth, daily_snapshots.revenue_growth),
                data_status = 'ok',
                data_note = excluded.data_note
            """,
            (
                asset_id,
                bar.date,
                bar.close,
                bar.high,
                bar.low,
                bar.volume,
                fundamentals.trailing_eps if (is_latest and fundamentals) else None,
                fundamentals.earnings_growth if (is_latest and fundamentals) else None,
                fundamentals.revenue_growth if (is_latest and fundamentals) else None,
                fundamentals_note if is_latest else None,
            ),
        )

    return {"ticker": ticker, "status": "ok", "note": fundamentals_note}

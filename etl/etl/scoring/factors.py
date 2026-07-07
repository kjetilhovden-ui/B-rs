"""Reads the raw, per-asset numbers that scoring is based on out of the
database. This module only extracts raw values (momentum %, growth %,
earnings yield, historical report reaction %) - turning them into
comparable 0-100 scores happens in normalize.py / blend.py.
"""

import sqlite3
from datetime import date

from .. import config


def build_raw_factor_table(conn: sqlite3.Connection) -> list[dict]:
    assets = conn.execute(
        "SELECT id, ticker, name, asset_type, sector FROM assets WHERE active = 1"
    ).fetchall()

    rows = []
    for asset in assets:
        rows.append(_build_row(conn, asset))
    return rows


def _build_row(conn: sqlite3.Connection, asset: sqlite3.Row) -> dict:
    asset_id = asset["id"]

    snapshots = conn.execute(
        """
        SELECT snapshot_date, close, trailing_eps, earnings_growth,
               revenue_growth, data_status, data_note
        FROM daily_snapshots
        WHERE asset_id = ?
        ORDER BY snapshot_date ASC
        """,
        (asset_id,),
    ).fetchall()

    ok_snapshots = [s for s in snapshots if s["data_status"] == "ok" and s["close"] is not None]
    latest = ok_snapshots[-1] if ok_snapshots else None

    data_status = "ok" if latest is not None else "missing"
    data_note = None if latest is not None else _latest_note(snapshots)

    return {
        "asset_id": asset_id,
        "ticker": asset["ticker"],
        "name": asset["name"],
        "asset_type": asset["asset_type"],
        "sector": asset["sector"],
        "data_status": data_status,
        "data_note": data_note,
        "latest_close": latest["close"] if latest else None,
        "momentum_pct": _momentum_pct(ok_snapshots),
        "growth_pct": _growth_pct(latest),
        "earnings_yield": _earnings_yield(latest),
        "reaction_pct": _reaction_pct(conn, asset_id),
        "next_report_date": _next_report_date(conn, asset_id),
    }


def _latest_note(snapshots: list[sqlite3.Row]) -> str | None:
    return snapshots[-1]["data_note"] if snapshots else "Ingen data hentet ennå."


def _momentum_pct(ok_snapshots: list[sqlite3.Row]) -> float | None:
    lookback = config.MOMENTUM_LOOKBACK_DAYS
    if len(ok_snapshots) < lookback + 1:
        return None
    latest_close = ok_snapshots[-1]["close"]
    past_close = ok_snapshots[-(lookback + 1)]["close"]
    if not past_close:
        return None
    return (latest_close - past_close) / past_close


def _growth_pct(latest: sqlite3.Row | None) -> float | None:
    if latest is None:
        return None
    if latest["earnings_growth"] is not None:
        return latest["earnings_growth"]
    return latest["revenue_growth"]


def _earnings_yield(latest: sqlite3.Row | None) -> float | None:
    if latest is None:
        return None
    eps = latest["trailing_eps"]
    close = latest["close"]
    if eps is None or not close:
        return None
    return eps / close


def _reaction_pct(conn: sqlite3.Connection, asset_id: int) -> float | None:
    rows = conn.execute(
        """
        SELECT reaction_pct FROM report_reactions
        WHERE asset_id = ? AND reaction_pct IS NOT NULL
        ORDER BY report_date DESC
        LIMIT ?
        """,
        (asset_id, config.REPORT_REACTION_LOOKBACK),
    ).fetchall()
    values = [r["reaction_pct"] for r in rows]
    if len(values) < config.REPORT_REACTION_MIN_SAMPLES:
        return None
    return sum(values) / len(values)


def _next_report_date(conn: sqlite3.Connection, asset_id: int) -> str | None:
    row = conn.execute(
        """
        SELECT report_date FROM report_dates
        WHERE asset_id = ? AND report_date >= ?
        ORDER BY report_date ASC
        LIMIT 1
        """,
        (asset_id, date.today().isoformat()),
    ).fetchone()
    return row["report_date"] if row else None

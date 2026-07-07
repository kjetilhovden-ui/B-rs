"""Loads the human-edited YAML files (assets.yaml, report_dates.yaml) into
SQLite. These files are the source of truth for the asset universe and the
report calendar - this step just syncs the database to match them.
"""

import sqlite3

import yaml

from .. import config


def load_assets(conn: sqlite3.Connection) -> int:
    with open(config.ASSETS_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assets = data.get("assets", []) if data else []
    for asset in assets:
        conn.execute(
            """
            INSERT INTO assets (ticker, name, asset_type, sector, active)
            VALUES (:ticker, :name, :asset_type, :sector, 1)
            ON CONFLICT(ticker) DO UPDATE SET
                name = excluded.name,
                asset_type = excluded.asset_type,
                sector = excluded.sector,
                active = 1
            """,
            asset,
        )
    conn.commit()
    return len(assets)


def load_report_dates(conn: sqlite3.Connection) -> int:
    if not config.REPORT_DATES_FILE.exists():
        return 0

    with open(config.REPORT_DATES_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    entries = data.get("report_dates", []) if data else []

    # Manual file is the full source of truth for future report dates, so
    # replace what's stored rather than accumulating stale duplicates.
    conn.execute("DELETE FROM report_dates WHERE source = 'manual'")

    count = 0
    for entry in entries:
        row = conn.execute(
            "SELECT id FROM assets WHERE ticker = ?", (entry["ticker"],)
        ).fetchone()
        if row is None:
            continue  # ticker not in assets.yaml (yet) - skip quietly
        conn.execute(
            """
            INSERT INTO report_dates (asset_id, report_date, source, notes)
            VALUES (?, ?, 'manual', ?)
            """,
            (row["id"], entry["report_date"], entry.get("notes")),
        )
        count += 1
    conn.commit()
    return count

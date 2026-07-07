"""SQLite connection and schema setup.

The database file (data/history.db) is committed to the git repo by the
daily GitHub Actions workflow, since there's no separate persistent server
to hold it between runs. See docs/ for more on that tradeoff.
"""

import sqlite3

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL CHECK(asset_type IN ('aksje', 'fond')),
    sector TEXT,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS daily_snapshots (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    snapshot_date TEXT NOT NULL,
    close REAL,
    high REAL,
    low REAL,
    volume INTEGER,
    trailing_eps REAL,
    earnings_growth REAL,
    revenue_growth REAL,
    data_status TEXT NOT NULL DEFAULT 'ok' CHECK(data_status IN ('ok', 'missing', 'stale')),
    data_note TEXT,
    UNIQUE(asset_id, snapshot_date)
);

CREATE TABLE IF NOT EXISTS report_dates (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    report_date TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'manual' CHECK(source IN ('manual', 'euronext_api')),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS report_reactions (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    report_date TEXT NOT NULL,
    close_before REAL,
    close_after REAL,
    reaction_pct REAL,
    UNIQUE(asset_id, report_date)
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    prediction_date TEXT NOT NULL,
    expected_direction TEXT NOT NULL CHECK(expected_direction IN ('opp', 'ned', 'flat')),
    momentum_pct_at_prediction REAL,
    UNIQUE(asset_id, prediction_date)
);

CREATE TABLE IF NOT EXISTS outcomes (
    id INTEGER PRIMARY KEY,
    prediction_id INTEGER NOT NULL UNIQUE REFERENCES predictions(id),
    close_before REAL,
    close_after REAL,
    actual_change_pct REAL,
    high_pct REAL,
    low_pct REAL,
    direction_correct INTEGER,
    range_captured_expected INTEGER,
    status TEXT NOT NULL DEFAULT 'ok' CHECK(status IN ('ok', 'missing_data'))
);

CREATE TABLE IF NOT EXISTS market_outlook (
    id INTEGER PRIMARY KEY,
    published_date TEXT NOT NULL,
    headline TEXT,
    body_markdown TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY,
    run_timestamp TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ok', 'partial', 'failed')),
    warnings TEXT
);
"""


def connect() -> sqlite3.Connection:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()

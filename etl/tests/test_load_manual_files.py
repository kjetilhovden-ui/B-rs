"""Run from the etl/ directory with: python -m pytest"""

import sqlite3

import pytest
import yaml

from etl import config, db
from etl.ingest import load_manual_files


@pytest.fixture
def conn(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "history.db")
    monkeypatch.setattr(config, "MANUAL_DIR", tmp_path)
    monkeypatch.setattr(config, "ASSETS_FILE", tmp_path / "assets.yaml")
    monkeypatch.setattr(config, "REPORT_DATES_FILE", tmp_path / "report_dates.yaml")
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    db.init_schema(connection)
    yield connection
    connection.close()


def _write_assets(assets: list[dict]) -> None:
    config.ASSETS_FILE.write_text(yaml.dump({"assets": assets}), encoding="utf-8")


def test_load_assets_inserts_new_tickers(conn):
    _write_assets([{"ticker": "EQNR.OL", "name": "Equinor", "asset_type": "aksje", "sector": "Energi"}])
    load_manual_files.load_assets(conn)

    rows = conn.execute("SELECT ticker, active FROM assets").fetchall()
    assert [(r["ticker"], r["active"]) for r in rows] == [("EQNR.OL", 1)]


def test_load_assets_deactivates_removed_ticker(conn):
    # A ticker that was renamed (e.g. AKERBP.OL -> AKRBP.OL) must stop
    # being active, not linger as a stale "ghost" row that keeps getting
    # fetched and shown as permanently broken.
    _write_assets([{"ticker": "AKERBP.OL", "name": "Aker BP", "asset_type": "aksje", "sector": "Energi"}])
    load_manual_files.load_assets(conn)

    _write_assets([{"ticker": "AKRBP.OL", "name": "Aker BP", "asset_type": "aksje", "sector": "Energi"}])
    load_manual_files.load_assets(conn)

    rows = {r["ticker"]: r["active"] for r in conn.execute("SELECT ticker, active FROM assets").fetchall()}
    assert rows == {"AKERBP.OL": 0, "AKRBP.OL": 1}


def test_load_assets_reactivates_a_ticker_that_returns(conn):
    _write_assets([{"ticker": "EQNR.OL", "name": "Equinor", "asset_type": "aksje", "sector": "Energi"}])
    load_manual_files.load_assets(conn)

    _write_assets([])
    load_manual_files.load_assets(conn)
    assert conn.execute("SELECT active FROM assets WHERE ticker = 'EQNR.OL'").fetchone()["active"] == 0

    _write_assets([{"ticker": "EQNR.OL", "name": "Equinor", "asset_type": "aksje", "sector": "Energi"}])
    load_manual_files.load_assets(conn)
    assert conn.execute("SELECT active FROM assets WHERE ticker = 'EQNR.OL'").fetchone()["active"] == 1

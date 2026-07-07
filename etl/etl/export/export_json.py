"""Writes the JSON files the static frontend fetches at runtime. This is
the contract between the Python ETL side and the React side - the frontend
never talks to SQLite or yfinance directly, only to these files.
"""

import json
import re
from datetime import UTC, datetime

from .. import config


def export_ranking(scored_rows: list[dict]) -> None:
    payload = {
        "generated_at": _now_iso(),
        "default_weights": config.DEFAULT_WEIGHTS,
        "report_warning_days": config.REPORT_WARNING_DAYS,
        "assets": [_asset_payload(row) for row in scored_rows],
    }
    _write_json("ranking.json", payload)


def export_status(run_status: str, warnings: list[str], asset_count: int) -> None:
    payload = {
        "generated_at": _now_iso(),
        "last_run_status": run_status,
        "warnings": warnings,
        "asset_count": asset_count,
    }
    _write_json("status.json", payload)


def export_outlook() -> None:
    if not config.MANUAL_DIR.joinpath("market_outlook.md").exists():
        return

    text = config.MANUAL_DIR.joinpath("market_outlook.md").read_text(encoding="utf-8")
    entries = _parse_outlook(text)
    entries.sort(key=lambda e: e["published_date"], reverse=True)

    payload = {"generated_at": _now_iso(), "entries": entries}
    _write_json("outlook.json", payload)


def _asset_payload(row: dict) -> dict:
    return {
        "ticker": row["ticker"],
        "name": row["name"],
        "asset_type": row["asset_type"],
        "sector": row["sector"],
        "score": row["score"],
        "factor_scores": row["factor_scores"],
        "raw_factors": {
            "momentum_pct": row["momentum_pct"],
            "growth_pct": row["growth_pct"],
            "earnings_yield": row["earnings_yield"],
            "reaction_pct": row["reaction_pct"],
        },
        "horizon": row["horizon"],
        "horizon_explanation": row["horizon_explanation"],
        "next_report_date": row["next_report_date"],
        "latest_close": row["latest_close"],
        "data_status": row["data_status"],
        "data_note": row["data_note"],
    }


def _parse_outlook(md_text: str) -> list[dict]:
    pattern = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
    matches = list(pattern.finditer(md_text))
    entries = []
    for idx, m in enumerate(matches):
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(md_text)
        body = md_text[start:end].strip()
        entries.append({"published_date": m.group(1), "body_markdown": body})
    return entries


def _write_json(filename: str, payload: dict) -> None:
    config.FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = config.FRONTEND_DATA_DIR / filename
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")

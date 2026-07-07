"""Entry point for the daily update. Run manually with:

    python -m etl.run_daily

or let the GitHub Actions workflow (.github/workflows/daily-update.yml)
run it every weekday morning.

Only DB-unopenable / output-dir-unwritable errors are treated as fatal
here. Everything else (a bad ticker, missing fundamentals, a parsing
hiccup on one asset) is caught closer to where it happens and recorded as
a warning, so one bad asset never blocks the whole update.
"""

from datetime import UTC, datetime

from . import config, db
from .export import export_json
from .ingest import fetch_market_data, load_manual_files
from .scoring import blend, factors
from .sources.yfinance_source import YFinanceSource


def main() -> None:
    print(f"[{_now()}] Starter daglig oppdatering ...")

    try:
        conn = db.connect()
        db.init_schema(conn)
    except Exception as exc:
        # Can't even open the database - nothing else we can do.
        print(f"[{_now()}] FATAL: klarte ikke åpne databasen: {exc}")
        _write_failed_status([f"Klarte ikke åpne databasen: {exc}"])
        raise SystemExit(1)

    warnings: list[str] = []

    try:
        n_assets = load_manual_files.load_assets(conn)
        n_dates = load_manual_files.load_report_dates(conn)
        print(f"[{_now()}] Lastet {n_assets} aksjer/fond og {n_dates} rapportdatoer.")
    except Exception as exc:
        msg = f"Klarte ikke lese manuelle datafiler (assets.yaml/report_dates.yaml): {exc}"
        print(f"[{_now()}] FATAL: {msg}")
        _write_failed_status([msg])
        raise SystemExit(1)

    fetch_results = fetch_market_data.fetch_all(conn, YFinanceSource())
    for result in fetch_results:
        if result["status"] != "ok":
            warnings.append(f"{result['ticker']}: {result['note']}")
        elif result["note"]:
            warnings.append(f"{result['ticker']}: {result['note']}")
    print(f"[{_now()}] Hentet markedsdata for {len(fetch_results)} aksjer/fond "
          f"({len(warnings)} advarsler).")

    raw_rows = factors.build_raw_factor_table(conn)
    scored_rows = blend.compute_scores(raw_rows)

    export_json.export_ranking(scored_rows)
    try:
        export_json.export_outlook()
    except Exception as exc:
        warnings.append(f"Klarte ikke eksportere markedsutsikter: {exc}")

    run_status = "ok" if not warnings else "partial"
    export_json.export_status(run_status, warnings, len(scored_rows))

    conn.execute(
        "INSERT INTO runs (run_timestamp, status, warnings) VALUES (?, ?, ?)",
        (_now(), run_status, "; ".join(warnings) if warnings else None),
    )
    conn.commit()
    conn.close()

    print(f"[{_now()}] Ferdig. Status: {run_status}. {len(warnings)} advarsler.")


def _write_failed_status(warnings: list[str]) -> None:
    try:
        export_json.export_status("failed", warnings, 0)
    except Exception:
        pass  # if we can't even write status.json, there's nothing more to do


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


if __name__ == "__main__":
    main()

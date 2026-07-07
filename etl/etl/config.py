"""All tunable constants live here, so they're easy to find and adjust
without hunting through the rest of the codebase.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = REPO_ROOT / "data"
DB_PATH = DATA_DIR / "history.db"
MANUAL_DIR = DATA_DIR / "manual"
ASSETS_FILE = MANUAL_DIR / "assets.yaml"
REPORT_DATES_FILE = MANUAL_DIR / "report_dates.yaml"

FRONTEND_DATA_DIR = REPO_ROOT / "frontend" / "public" / "data"

# How many trading days back momentum looks. ~10 trading days is roughly
# two calendar weeks.
MOMENTUM_LOOKBACK_DAYS = 10

# How many quarters of report-reaction history to average (Fase 2+).
REPORT_REACTION_LOOKBACK = 8
REPORT_REACTION_MIN_SAMPLES = 2

# Default factor weights for the blended score. Must sum to 1.0.
# These are the "sensible defaults" the user should never have to touch -
# the Advanced view lets them override these with sliders.
DEFAULT_WEIGHTS = {
    "growth": 0.30,
    "momentum": 0.25,
    "valuation": 0.25,
    "reaction": 0.20,
}

# Time-horizon thresholds (percentile scores, 0-100).
HORIZON_MOMENTUM_THRESHOLD = 70
HORIZON_GROWTH_LONG_THRESHOLD = 70
HORIZON_GROWTH_MEDIUM_THRESHOLD = 50
HORIZON_SHORT_TERM_MAX_DAYS_TO_REPORT = 30

# A daily price move smaller than this (in percent) is treated as "flat"
# rather than up/down, so tiny noise doesn't get scored as a wrong
# prediction in the accuracy log.
FLAT_MOVE_DEADZONE_PCT = 0.15

# Days-until-report warning threshold shown in red in the UI.
REPORT_WARNING_DAYS = 14

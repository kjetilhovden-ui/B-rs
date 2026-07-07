"""Combines the four raw factors into one ranked score per asset, and
assigns a time-horizon category with a human-readable explanation.

The same weighted-average-of-available-factors formula is re-implemented
in frontend/src/lib/scoring.ts for the client-side "Advanced" weight
sliders. Keep this function simple - any drift between the two makes the
sliders lie about what they're doing.
"""

from datetime import date

from .. import config
from . import normalize


def compute_scores(raw_rows: list[dict], weights: dict | None = None) -> list[dict]:
    weights = weights or config.DEFAULT_WEIGHTS

    factor_names = ["momentum", "growth", "valuation", "reaction"]
    raw_value_key = {
        "momentum": "momentum_pct",
        "growth": "growth_pct",
        "valuation": "earnings_yield",
        "reaction": "reaction_pct",
    }
    percentile_scores = {
        factor: normalize.percentile_ranks([row[raw_value_key[factor]] for row in raw_rows])
        for factor in factor_names
    }

    results = []
    for i, row in enumerate(raw_rows):
        factor_scores = {factor: percentile_scores[factor][i] for factor in factor_names}
        blended = weighted_average(factor_scores, weights)
        horizon, explanation = _categorize_horizon(row, factor_scores)
        results.append(
            {
                **row,
                "factor_scores": factor_scores,
                "score": blended,
                "horizon": horizon,
                "horizon_explanation": explanation,
            }
        )

    # Assets with a real score are sorted best-to-worst; assets with no
    # score at all (every factor unavailable) sink to the bottom rather
    # than being dropped, so missing data stays visible.
    results.sort(key=lambda r: (r["score"] is None, -(r["score"] or 0)))
    return results


def weighted_average(factor_scores: dict[str, float | None], weights: dict[str, float]) -> float | None:
    """Weighted mean over only the factors that are actually available for
    this asset - a missing factor is excluded, not substituted with a
    neutral 50, so data-sparse assets aren't unfairly dragged to the middle.
    """
    weighted_sum = 0.0
    total_weight = 0.0
    for factor, score in factor_scores.items():
        if score is None:
            continue
        weight = weights.get(factor, 0)
        weighted_sum += score * weight
        total_weight += weight
    if total_weight == 0:
        return None
    return weighted_sum / total_weight


def _categorize_horizon(row: dict, factor_scores: dict) -> tuple[str, str]:
    momentum_score = factor_scores["momentum"]
    growth_score = factor_scores["growth"]
    days_until_report = _days_until(row["next_report_date"])

    if (
        momentum_score is not None
        and momentum_score >= config.HORIZON_MOMENTUM_THRESHOLD
        and days_until_report is not None
        and days_until_report <= config.HORIZON_SHORT_TERM_MAX_DAYS_TO_REPORT
    ):
        return (
            "Kort sikt (uker)",
            f"Sterk momentum (persentil {momentum_score:.0f}) og kvartalsrapport "
            f"om {days_until_report} dager.",
        )

    if growth_score is not None and growth_score >= config.HORIZON_GROWTH_LONG_THRESHOLD:
        return (
            "Lang sikt (1–3 år)",
            f"Høy fundamental vekst (persentil {growth_score:.0f}), mindre "
            "avhengig av kortsiktig støy.",
        )

    if growth_score is not None and growth_score >= config.HORIZON_GROWTH_MEDIUM_THRESHOLD:
        return (
            "Middels sikt (6–12 mnd)",
            f"Moderat fundamental vekst (persentil {growth_score:.0f}).",
        )

    return (
        "Usikker horisont",
        "Verken tydelig vekst eller momentum i dataene som er tilgjengelig nå.",
    )


def _days_until(iso_date: str | None) -> int | None:
    if not iso_date:
        return None
    return (date.fromisoformat(iso_date) - date.today()).days

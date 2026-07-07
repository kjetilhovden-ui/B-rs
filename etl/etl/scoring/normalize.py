"""Turns raw factor values into 0-100 percentile scores within today's
universe. Percentile rank (rather than e.g. min-max scaling) is robust to
one wild outlier skewing everyone else's score, and is easy to explain:
"this stock is in the 80th percentile of momentum today".
"""


def percentile_ranks(values: list[float | None]) -> list[float | None]:
    """Same length as `values`. None stays None (factor unavailable for
    that asset). Ties get the average rank of the tied group."""
    indexed = [(i, v) for i, v in enumerate(values) if v is not None]
    result: list[float | None] = [None] * len(values)
    n = len(indexed)

    if n == 0:
        return result
    if n == 1:
        result[indexed[0][0]] = 50.0
        return result

    sorted_indexed = sorted(indexed, key=lambda pair: pair[1])
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sorted_indexed[j + 1][1] == sorted_indexed[i][1]:
            j += 1
        avg_rank = (i + j) / 2  # 0-based rank, averaged across ties
        percentile = avg_rank / (n - 1) * 100
        for k in range(i, j + 1):
            original_index = sorted_indexed[k][0]
            result[original_index] = percentile
        i = j + 1

    return result

"""Turn readings into green / amber / red. Plain Python, no Streamlit."""
import math

from core.thresholds import INDICATORS, THRESHOLDS

SEVERITY = {"green": 0, "amber": 1, "red": 2}


def assess(indicator, value):
    """Return "green", "amber" or "red" for one reading."""
    if indicator not in THRESHOLDS:
        raise ValueError(f"Unknown indicator: {indicator!r}")
    if value is None or (isinstance(value, float) and math.isnan(value)):
        raise ValueError(f"No value for {indicator}")
    t = THRESHOLDS[indicator]
    if t["green"][0] <= value < t["green"][1]:
        return "green"
    if t["amber"][0] <= value < t["amber"][1]:
        return "amber"
    return "red"


def assess_row(row):
    """Status of every indicator present in a check-in.

    `row` can be a dict or a pandas Series. Missing or empty values are skipped.
    Returns e.g. {"heart_rate": "green", "sleep_hours": "red", ...}.
    """
    statuses = {}
    for indicator in INDICATORS:
        value = row.get(indicator)
        if value is None or (isinstance(value, float) and math.isnan(value)):
            continue
        statuses[indicator] = assess(indicator, value)
    return statuses


def overall_status(row):
    """Worst single status in the row (any red makes it red).

    Returns "unknown" if the row has no readings at all.
    """
    statuses = assess_row(row).values()
    if not statuses:
        return "unknown"
    return max(statuses, key=SEVERITY.__getitem__)

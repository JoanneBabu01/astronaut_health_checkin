"""Turn readings into green / amber / red, spot trends, and score the day.

Plain Python, no Streamlit. Fixed rules only: no machine learning, no forecasting.
"""
import math

import pandas as pd

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


# ------------------------------------------------------------------ health score

AMBER_PENALTY = 5     # team choices: tune freely
RED_PENALTY = 15


def health_score(statuses):
    """0-100 score for the dashboard and the gamification (XP, badges).

    Start at 100, subtract 5 for each amber and 15 for each red, never below 0.
    `statuses` is the dict from assess_row(). It is a game-style summary, not a
    medical measure: colour the dial with overall_status(), not with the score,
    so one red reading can never look green.
    """
    penalty = 0
    for status in statuses.values():
        if status == "amber":
            penalty += AMBER_PENALTY
        elif status == "red":
            penalty += RED_PENALTY
    return max(0, 100 - penalty)


# ------------------------------------------------------------------ trend flags
# A trend is often more useful than one bad reading. These are plain rules over
# the recent days (counting days and comparing averages), not predictions.

# (id, indicator, test on one day's value, days in a row, status, message)
STREAK_RULES = [
    ("sleep_short", "sleep_hours", lambda v: v < 6, 3, "red",
     "Sleep was under 6 hours for 3 nights in a row."),
    ("sleep_low", "sleep_hours", lambda v: v < 7, 3, "amber",
     "Sleep was under 7 hours for 3 nights in a row."),
    ("mood_low", "mood", lambda v: v <= 2, 3, "red",
     "Mood was 2 or lower for 3 days in a row."),
    ("mood_dip", "mood", lambda v: v <= 3, 3, "amber",
     "Mood was 3 or lower for 3 days in a row."),
    ("stress_high", "stress", lambda v: v >= 4, 3, "red",
     "Stress was 4 or 5 for 3 days in a row."),
    ("stress_up", "stress", lambda v: v >= 3, 3, "amber",
     "Stress was 3 or higher for 3 days in a row."),
]

# (id, indicator, smallest rise that counts). Compares the average of the last
# 7 days with the 7 days before. Team choices: tune freely.
RISE_RULES = [
    ("systolic_rising", "systolic_bp", 8),
    ("diastolic_rising", "diastolic_bp", 5),
    ("heart_rate_rising", "heart_rate", 5),
]


def _daily_series(df, indicator, first_day, last_day):
    """One value per calendar day (the day's last reading); days with none are NaN."""
    frame = pd.DataFrame({"t": df["_t"], "v": pd.to_numeric(df[indicator], errors="coerce")}).dropna()
    frame["day"] = frame["t"].dt.normalize()
    daily = frame.sort_values("t").groupby("day")["v"].last()
    return daily.reindex(pd.date_range(first_day, last_day, freq="D"))


def trend_flags(df):
    """Trend flags for one astronaut's log (use load_log(astronaut)).

    Returns a list of dicts, most important first (active before past, red before
    amber, then newest):
      id, indicator, label, status ("amber"/"red"), message, start, end, active
    "active" means the pattern runs up to the latest check-in. A flag that
    already ended is kept as history (for an alert log) with active False.
    Days in a row means consecutive calendar days: a missed day breaks a streak.
    """
    if df is None or len(df) == 0 or "timestamp" not in df.columns:
        return []
    df = df.copy()
    if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["_t"] = df["timestamp"]
    else:
        from core.data import _parse_timestamps
        df["_t"] = _parse_timestamps(df["timestamp"])
    first_day = df["_t"].min().normalize()
    last_day = df["_t"].max().normalize()

    found = []

    def add(rule_id, indicator, status, message, end):
        found.append({
            "id": rule_id, "indicator": indicator,
            "label": THRESHOLDS[indicator]["label"], "status": status,
            "message": message, "end": end, "active": end == last_day,
        })

    for rule_id, indicator, test, days, status, message in STREAK_RULES:
        if indicator not in df.columns:
            continue
        series = _daily_series(df, indicator, first_day, last_day)
        hit = series.notna() & test(series)
        windows = hit.astype(int).rolling(days).sum() == days
        ends = windows[windows].index
        if len(ends):
            add(rule_id, indicator, status, message, ends[-1])
            found[-1]["start"] = ends[-1] - pd.Timedelta(days=days - 1)

    for rule_id, indicator, minimum in RISE_RULES:
        if indicator not in df.columns:
            continue
        series = _daily_series(df, indicator, first_day, last_day)
        average = series.rolling(7, min_periods=7).mean()
        rise = average - average.shift(7)
        ends = rise[rise >= minimum].index
        if len(ends):
            end = ends[-1]
            t = THRESHOLDS[indicator]
            add(rule_id, indicator, "amber",
                f"{t['label']} (7-day average) rose about {rise[end]:.0f} {t['unit']} "
                f"compared with the week before.", end)
            found[-1]["start"] = end - pd.Timedelta(days=13)

    # If a red and an amber flag for the same indicator end on the same day, keep the red.
    best = {}
    for flag in found:
        key = (flag["indicator"], flag["end"])
        if key not in best or SEVERITY[flag["status"]] > SEVERITY[best[key]["status"]]:
            best[key] = flag
    flags = list(best.values())
    flags.sort(key=lambda f: (not f["active"], f["status"] != "red", -f["end"].value))
    return flags

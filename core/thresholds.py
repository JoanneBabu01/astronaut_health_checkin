"""Normal ranges per indicator (starting thresholds, from the team plan).

For education and demonstration only, not medical advice. Real flight
medicine compares each astronaut against their own baseline.

How to read an entry (ranges are half-open: low <= value < high):
  green      -> the "OK" range
  amber      -> the wider "watch" range; inside it but outside green = amber
  anything outside the amber range = red
  plot_range -> axis limits for charts (used by get_bands)

Keys match the column names in data/sample_crew_log.csv.
"""

THRESHOLDS = {
    "systolic_bp": {
        "label": "Systolic blood pressure", "unit": "mmHg",
        "green": (90, 120), "amber": (70, 140), "plot_range": (60, 170),
    },
    "diastolic_bp": {
        "label": "Diastolic blood pressure", "unit": "mmHg",
        "green": (60, 80), "amber": (40, 90), "plot_range": (40, 110),
    },
    "heart_rate": {
        "label": "Resting heart rate", "unit": "bpm",
        "green": (50, 101), "amber": (40, 121), "plot_range": (30, 140),
    },
    "blood_glucose": {
        "label": "Blood glucose (fasting)", "unit": "mg/dL",
        "green": (70, 100), "amber": (55, 126), "plot_range": (40, 160),
    },
    "body_temp": {
        "label": "Body temperature", "unit": "°C",
        "green": (36.1, 37.3), "amber": (35.5, 38.0), "plot_range": (35.0, 39.0),
    },
    # Sleep: the plan's table has no upper limit; we treat 9.1-10 h as amber
    # and anything longer as red.
    "sleep_hours": {
        "label": "Sleep", "unit": "h",
        "green": (7.0, 9.1), "amber": (6.0, 10.1), "plot_range": (3.0, 11.0),
    },
    "mood": {
        "label": "Mood", "unit": "1-5",
        "green": (4, 6), "amber": (3, 6), "plot_range": (1, 5),
    },
    # Stress: HIGHER is worse, so the ranges sit at the low end.
    "stress": {
        "label": "Stress", "unit": "1-5",
        "green": (1, 3), "amber": (1, 4), "plot_range": (1, 5),
    },
    "exercise_min": {
        "label": "Exercise", "unit": "min/day",
        "green": (90, 1441), "amber": (30, 1441), "plot_range": (0, 180),
    },
}

INDICATORS = list(THRESHOLDS)


def get_bands(indicator):
    """Return [(low, high, status), ...] for shading chart backgrounds.

    Bands are clipped to the indicator's plot_range and listed bottom to top.
    """
    t = THRESHOLDS[indicator]
    gl, gh = t["green"]
    al, ah = t["amber"]
    lo, hi = t["plot_range"]
    raw = [(lo, al, "red"), (al, gl, "amber"), (gl, gh, "green"),
           (gh, ah, "amber"), (ah, hi, "red")]
    bands = []
    for a, b, status in raw:
        a, b = max(a, lo), min(b, hi)
        if b > a:
            bands.append((a, b, status))
    return bands

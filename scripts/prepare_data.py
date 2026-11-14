"""Generate the simulated crew health log in the team's data contract.

Run from the repo root:  python scripts/prepare_data.py
Writes:                  data/sample_crew_log.csv

Contract: one row per check-in, columns
  timestamp, astronaut, environment, systolic_bp, diastolic_bp, heart_rate,
  blood_glucose, body_temp, sleep_hours, mood, stress, exercise_min

ALL VALUES ARE SIMULATED. Baselines are chosen so normal days sit in the
green band of the starting thresholds; drift sizes are illustrative and
should be replaced with cited literature values (see TODO in README).
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_DAYS = 50
ASTRONAUT = "Commander A"
ENVIRONMENT = "ISS"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_crew_log.csv"

COLUMNS = [
    "timestamp", "astronaut", "environment", "systolic_bp", "diastolic_bp",
    "heart_rate", "blood_glucose", "body_temp", "sleep_hours", "mood",
    "stress", "exercise_min",
]

# column: (baseline, daily noise std, decimals, hard min, hard max)
SPEC = {
    "systolic_bp":   (110.0, 3.0, 0, 70, 220),
    "diastolic_bp":  (70.0, 2.5, 0, 40, 140),
    "heart_rate":    (62.0, 2.5, 0, 30, 220),
    "blood_glucose": (88.0, 5.0, 0, 40, 400),
    "body_temp":     (36.7, 0.15, 1, 34, 42),
    "sleep_hours":   (7.7, 0.4, 1, 0, 14),
    "mood":          (4.4, 0.5, 0, 1, 5),
    "stress":        (1.7, 0.5, 0, 1, 5),
    "exercise_min":  (115.0, 12.0, 0, 0, 600),
}


def drift_story(n_days):
    """Additive offsets per column. Day numbers are 1-based in comments.

    - days 20-24: short sleep, high stress, less exercise (stressful week)
    - days 22-30: mood dips (red at the worst point), then recovers
    - days 25-50: blood pressure and heart rate climb slowly (ends red)
    - day 33: one high glucose reading (red)
    - days 40-42: mild temperature rise (amber)
    """
    d = {name: np.zeros(n_days) for name in SPEC}
    d["sleep_hours"][19:24] -= 1.9
    d["stress"][19:25] += 2.0
    d["exercise_min"][19:24] -= 60
    d["mood"][21:30] -= np.linspace(2.4, 0.6, 9)

    ramp = np.linspace(0, 1, n_days - 24)
    d["systolic_bp"][24:] += 32 * ramp
    d["diastolic_bp"][24:] += 21 * ramp
    d["heart_rate"][24:] += 10 * ramp

    d["blood_glucose"][32] += 48
    d["body_temp"][39:42] += 0.6
    return d


def generate(n_days=N_DAYS, seed=SEED, end_date=None):
    """Return a DataFrame in contract format.

    end_date defaults to yesterday so the app's "next check-in due" reminder
    is not months overdue.
    """
    if end_date is None:
        end_date = pd.Timestamp.today().normalize() - pd.Timedelta(days=1)
    dates = pd.date_range(end=pd.Timestamp(end_date), periods=n_days, freq="D")
    rng = np.random.default_rng(seed)
    drift = drift_story(n_days)

    data = {
        "timestamp": (dates + pd.Timedelta(hours=8)).strftime("%Y-%m-%d %H:%M"),
        "astronaut": ASTRONAUT,
        "environment": ENVIRONMENT,
    }
    for name, (base, sd, decimals, lo, hi) in SPEC.items():
        values = base + drift[name] + rng.normal(0, sd, n_days)
        values = np.clip(np.round(values, decimals), lo, hi)
        data[name] = values.astype(int) if decimals == 0 else values
    return pd.DataFrame(data)[COLUMNS]


def validate(df):
    """Raise ValueError on wrong columns, missing values or impossible readings."""
    if list(df.columns) != COLUMNS:
        raise ValueError(f"Columns must be {COLUMNS}")
    if df.isna().any().any():
        raise ValueError("Missing values found")
    for name, (_, _, _, lo, hi) in SPEC.items():
        if not df[name].between(lo, hi).all():
            raise ValueError(f"{name} has values outside {lo}-{hi}")
    return df


if __name__ == "__main__":
    out = validate(generate())
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(out)} rows to {OUT_PATH}")

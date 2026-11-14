"""Generate the simulated crew health log (long format).

Run from the repo root:  python scripts/prepare_data.py
Writes:                  data/vitals.csv

Columns: date, indicator, value, unit, source, source_ref
Everything here is SIMULATED. Baselines and drift sizes are placeholders
until Person D verifies literature values; put the citation in SOURCE_REFS.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_DAYS = 50
START_DATE = "2026-01-01"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "vitals.csv"

# indicator: (baseline, daily noise std, unit, hard min, hard max)
INDICATORS = {
    "heart_rate":      (62.0, 2.5, "bpm", 30, 220),
    "systolic_bp":     (118.0, 3.0, "mmHg", 70, 220),
    "diastolic_bp":    (76.0, 2.5, "mmHg", 40, 140),
    "glucose":         (92.0, 5.0, "mg/dL", 40, 400),
    "body_temp":       (36.7, 0.15, "C", 34, 42),
    "sleep_hours":     (7.0, 0.5, "h", 0, 14),
    "mood":            (4.0, 0.4, "score 1-5", 1, 5),
}

# TODO (Person D): replace with verified citations once literature is checked.
SOURCE_REFS = {name: "TODO: cite (placeholder baseline)" for name in INDICATORS}


def drift_story(n_days):
    """Return {indicator: array of additive offsets per day}.

    Story: a stable first 3 weeks, then
      - days 20-24: short sleep (stressful week)
      - days 22-30: mood dips after the bad sleep
      - days 25-49: slow blood pressure and resting heart rate rise
      - day 33: one high glucose reading
      - days 40-42: mild temperature rise
    """
    d = {name: np.zeros(n_days) for name in INDICATORS}

    d["sleep_hours"][19:24] -= 1.9
    d["mood"][21:30] -= np.linspace(1.6, 0.4, 9)

    ramp = np.linspace(0, 1, n_days - 24)
    d["systolic_bp"][24:] += 22 * ramp
    d["diastolic_bp"][24:] += 12 * ramp
    d["heart_rate"][24:] += 9 * ramp

    d["glucose"][32] += 48
    d["body_temp"][39:42] += 0.6
    return d


def generate(n_days=N_DAYS, seed=SEED):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(START_DATE, periods=n_days, freq="D")
    drift = drift_story(n_days)
    frames = []
    for name, (base, sd, unit, lo, hi) in INDICATORS.items():
        values = base + drift[name] + rng.normal(0, sd, n_days)
        values = np.clip(values, lo, hi)
        if name == "mood":
            values = np.clip(np.round(values), 1, 5)
        elif name == "body_temp":
            values = np.round(values, 1)
        else:
            values = np.round(values, 1)
        frames.append(pd.DataFrame({
            "date": dates,
            "indicator": name,
            "value": values,
            "unit": unit,
            "source": "simulated",
            "source_ref": SOURCE_REFS[name],
        }))
    return pd.concat(frames, ignore_index=True).sort_values(["date", "indicator"]).reset_index(drop=True)


def validate(df):
    """Raise ValueError on missing values or impossible readings."""
    if df.isna().any().any():
        raise ValueError("Missing values found")
    for name, (_, _, _, lo, hi) in INDICATORS.items():
        v = df.loc[df["indicator"] == name, "value"]
        if not v.between(lo, hi).all():
            raise ValueError(f"{name} has values outside {lo}-{hi}")
    return df


if __name__ == "__main__":
    out = validate(generate())
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(out)} rows to {OUT_PATH}")
